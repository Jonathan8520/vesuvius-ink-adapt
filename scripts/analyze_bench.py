"""Analyse d'un run du banc de mesure : écarts appariés entre branches, avec bootstrap par blocs et par graines.

Lit les histogrammes par bloc écrits par `scripts/run_bench.py` (`blocs_<branche>_g<graine>_p<pas>.npz`).
Règle de lecture : `docs/PLAN.md`, étape 5b (écrite avant le résultat). Mesure principale : AUC, écart H - T,
moyenne sur les segments d'un groupe (cas réservés d'`ink_9um` d'un côté, PHerc0841 de l'autre).

Bootstrap hiérarchique apparié : à chaque tirage, les blocs de chaque segment sont rééchantillonnés avec remise
(les mêmes pour toutes les branches et toutes les graines), puis les graines (les mêmes pour les deux branches
comparées, puisqu'elles voient les mêmes patchs).

Usage : python scripts/analyze_bench.py data/kaggle_out/pretest/results [--step 1000] [--draws 2000]
"""
import argparse
import glob
import json
import os
import re

import numpy as np


def auc_ba(h):
    """AUC et précision équilibrée au seuil 0,5 à partir d'histogrammes (2, 256) : h[0] fond, h[1] encre."""
    bg, ink = h[0].astype(np.float64), h[1].astype(np.float64)
    nb, ni = bg.sum(), ink.sum()
    if nb == 0 or ni == 0:
        return np.nan, np.nan
    below = np.cumsum(bg) - bg
    auc = float((ink * (below + 0.5 * bg)).sum() / (ni * nb))
    ba = 0.5 * (ink[128:].sum() / ni + bg[:128].sum() / nb)
    return auc, float(ba)


def load(results, step):
    data, steps = {}, set()
    for path in glob.glob(os.path.join(results, "blocs_*_g*_p*.npz")):
        m = re.match(r"blocs_(.+)_g(\d+)_p(\d+)\.npz", os.path.basename(path))
        steps.add(int(m.group(3)))
        data[(m.group(1), int(m.group(2)), int(m.group(3)))] = path
    final = max(s for (a, g, s) in data if a != "base") if step is None else step
    out = {}
    for (arm, seed, s), path in data.items():
        if s != (0 if arm == "base" else final):
            continue
        z = np.load(path)
        out[(arm, seed)] = {k[:-6]: (z[k], z[k[:-6] + "__hist"]) for k in z.files if k.endswith("__cles")}
    return out, final, sorted(steps)


def group_of(seg):
    return "PHerc0841 (jamais vu)" if seg.startswith("pherc0841") else "cas réservés (rouleaux vus)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--step", type=int)
    ap.add_argument("--draws", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261122)
    ap.add_argument("--json")
    a = ap.parse_args()
    runs, step, steps = load(a.results, a.step)
    arms = sorted({arm for arm, _ in runs})
    segs = sorted({s for r in runs.values() for s in r})
    print(f"pas analysé : {step} (pas disponibles : {steps}) ; branches : "
          + ", ".join(f"{arm} ({sum(1 for x, _ in runs if x == arm)} graines)" for arm in arms))
    # aligner les blocs de chaque segment entre runs
    keys = {s: np.unique(np.concatenate([r[s][0] for r in runs.values() if s in r])) for s in segs}
    H = {}
    for (arm, seed), r in runs.items():
        for s in segs:
            if s not in r:
                continue
            k, h = r[s]
            full = np.zeros((2, len(keys[s]), 256), np.float64)
            full[:, np.searchsorted(keys[s], k)] = h
            H[(arm, seed, s)] = full
    report = dict(pas=step, segments={}, groupes={}, controles={})
    # scores ponctuels
    print("\nAUC par segment (moyenne des graines) :")
    print(f"{'segment':22s} {'blocs':>5s} " + " ".join(f"{arm:>8s}" for arm in arms))
    point = {}
    for s in segs:
        row = {}
        for arm in arms:
            v = [auc_ba(H[(arm, g, s)].sum(1))[0] for (x, g) in runs if x == arm and (arm, g, s) in H]
            row[arm] = float(np.mean(v)) if v else np.nan
        point[s] = row
        report["segments"][s] = {k: round(v, 4) for k, v in row.items()}
        print(f"{s:22s} {len(keys[s]):5d} " + " ".join(f"{row[arm]:8.4f}" for arm in arms))
    # contrôle : le témoin ne doit pas perdre plus de 0,02 d'AUC par rapport au checkpoint publié
    if "base" in arms and "C" in arms:
        for grp in sorted({group_of(s) for s in segs}):
            d = float(np.mean([point[s]["C"] - point[s]["base"] for s in segs if group_of(s) == grp]))
            report["controles"][f"C - base, {grp}"] = round(d, 4)
            print(f"contrôle C - base, {grp} : {d:+.4f}" + ("  (RECETTE TROP BRUTALE)" if d < -0.02 else ""))
    # bootstrap apparié
    rng = np.random.default_rng(a.seed)
    for hi, lo in (("H", "T"), ("H", "C"), ("T", "C"), ("D", "H"), ("D", "T"), ("D", "C"), ("T", "S"), ("H", "S"), ("S", "C")):
        seeds = sorted({g for (x, g) in runs if x == hi} & {g for (x, g) in runs if x == lo})
        if not seeds:
            continue
        for grp in sorted({group_of(s) for s in segs}):
            gs = [s for s in segs if group_of(s) == grp and all((arm, g, s) in H for arm in (hi, lo) for g in seeds)]
            if not gs:
                continue
            for metric in (0, 1):
                est = np.mean([np.mean([auc_ba(H[(hi, g, s)].sum(1))[metric] - auc_ba(H[(lo, g, s)].sum(1))[metric] for g in seeds]) for s in gs])
                draws = np.empty(a.draws)
                for d in range(a.draws):
                    pick = rng.integers(0, len(seeds), len(seeds))
                    acc = []
                    for s in gs:
                        n = len(keys[s])
                        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(np.float64)
                        acc.append(np.mean([auc_ba(np.einsum("n,cnb->cb", w, H[(hi, seeds[i], s)]))[metric]
                                            - auc_ba(np.einsum("n,cnb->cb", w, H[(lo, seeds[i], s)]))[metric] for i in pick]))
                    draws[d] = np.nanmean(acc)
                lo95, hi95 = np.nanpercentile(draws, [2.5, 97.5])
                name = "AUC" if metric == 0 else "précision équilibrée"
                per_seed = [float(np.mean([auc_ba(H[(hi, g, s)].sum(1))[metric] - auc_ba(H[(lo, g, s)].sum(1))[metric] for s in gs])) for g in seeds]
                report["groupes"][f"{hi} - {lo} | {grp} | {name}"] = dict(estimation=round(float(est), 4), ic95=[round(float(lo95), 4), round(float(hi95), 4)],
                                                                       par_graine=[round(v, 4) for v in per_seed], segments=len(gs), graines=len(seeds))
                print(f"{hi} - {lo} | {grp:28s} | {name:20s} : {est:+.4f}  IC 95 % [{lo95:+.4f} ; {hi95:+.4f}]  par graine "
                      + " ".join(f"{v:+.4f}" for v in per_seed))
    # verdict selon la règle écrite avant le résultat
    g = {k: v for k, v in report["groupes"].items() if k.startswith("H - T") and k.endswith("AUC")}
    if len(g) == 2:
        lows, highs, ests = [v["ic95"][0] for v in g.values()], [v["ic95"][1] for v in g.values()], [v["estimation"] for v in g.values()]
        if any(l > 0 for l in lows) and all(e >= 0 for e in ests):
            verdict = "l'humain fait mieux"
        elif any(h < 0 for h in highs) and all(e <= 0 for e in ests):
            verdict = "la carte fait mieux"
        else:
            verdict = "pas de différence mesurable"
        report["verdict"] = verdict
        print("\nVerdict (règle du plan) :", verdict)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(report, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
