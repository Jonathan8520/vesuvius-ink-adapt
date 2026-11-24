"""Lance les branches du banc de mesure : affinages d'`ink_9um` qui ne diffèrent que par les étiquettes ajoutées.

Branches :
- `base` : le checkpoint publié, sans affinage (contrôle : on doit retrouver les chiffres connus) ;
- `C` : témoin, affinage sur le seul corpus de l'équipe ;
- `T` : corpus de l'équipe + segments nouveaux étiquetés par la carte du modèle 2 µm seuillée ;
- `H` : corpus de l'équipe + les mêmes pixels étiquetés à la main (étiquettes de l'équipe reportées) ;
- `D` : corpus de l'équipe + la carte du modèle 2 µm sur toute la surface des mêmes segments, sans choix humain ;
- `S` : comme `T`, mais la carte est reportée sans recalage (simple mise à l'échelle, décalage de 5 à 10 px).

Mesure : les 9 zones réservées d'`ink_9um` et PHerc0841, grille de tuiles officielle, fenêtre centrée.

Usage (CPU, essai) : python scripts/run_bench.py --arms base --ckpt s43-75k
Usage (Kaggle)     : python scripts/run_bench.py --arms C,T,H --seeds 0,1,2 --steps 1000 --shard 0/2
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core, finetune as FT  # noqa: E402

NEW = ["pherc0500p2-m1", "pherc0009b-ag487"]
QUOTAS = {
    "C": {"0139": 29, "1667": 22, "Paris4": 11, "0814": 2},                 # quotas de la recette de l'équipe
    "N": {"0139": 20, "1667": 15, "Paris4": 8, "0814": 1, NEW[0]: 10, NEW[1]: 10},   # 31 % de segments nouveaux
    # branche D : mêmes segments, carte du modèle 2 µm sur toute leur surface, sans aucun choix humain
    "D": {"0139": 20, "1667": 15, "Paris4": 8, "0814": 1, NEW[0] + "-dense": 10, NEW[1] + "-dense": 10},
}


def scale_quotas(q, batch):
    """Réduit les quotas pour un essai sur CPU, en gardant au moins un patch par groupe."""
    if batch >= sum(q.values()):
        return dict(q)
    return {k: max(1, round(v * batch / sum(q.values()))) for k, v in q.items()}


def summarize(runs):
    """Moyenne et écart-type par branche et par segment, puis écarts appariés H - T et H - C par graine."""
    out = {"branches": {}, "ecarts": {}}
    segs = sorted({s for r in runs for s in r["scores"]})
    for arm in sorted({r["branche"] for r in runs}):
        rs = [r for r in runs if r["branche"] == arm]
        out["branches"][arm] = {"graines": sorted(r["graine"] for r in rs), "segments": {
            s: {m: [round(float(np.mean(v)), 4), round(float(np.std(v)), 4)]
                for m in ("ba", "f1", "auc") for v in [[r["scores"][s][m] for r in rs if s in r["scores"]]] if v}
            for s in segs}}
    for a, b in (("H", "T"), ("H", "C"), ("T", "C")):
        ra = {r["graine"]: r for r in runs if r["branche"] == a}
        rb = {r["graine"]: r for r in runs if r["branche"] == b}
        seeds = sorted(set(ra) & set(rb))
        if not seeds:
            continue
        out["ecarts"][f"{a}-{b}"] = {"graines": seeds, "segments": {
            s: {m: [round(float(np.mean(d)), 4), round(float(np.std(d)), 4), int(sum(x > 0 for x in d))]
                for m in ("ba", "auc") for d in [[ra[g]["scores"][s][m] - rb[g]["scores"][s][m] for g in seeds
                                                  if s in ra[g]["scores"] and s in rb[g]["scores"]]] if d}
            for s in segs}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", default="data/bench")
    ap.add_argument("--out", default=None)
    ap.add_argument("--ckpt", default="s43-75k")
    ap.add_argument("--arms", default="base")
    ap.add_argument("--seeds", default="0")
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=0.002)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--shard", default="0/1", help="i/n : ne lance que les couples (branche, graine) d'indice i modulo n")
    ap.add_argument("--eval-only", nargs="*", help="noms de segments d'évaluation à garder (essais)")
    ap.add_argument("--eval-at", default="", help="pas intermédiaires où noter aussi, séparés par des virgules")
    a = ap.parse_args()
    out = a.out or os.path.join(a.bench, "results")
    os.makedirs(out, exist_ok=True)
    core.CKPTS.setdefault("s43-75k", "hybrid_3d2d-seed43/step-075000.pth")
    core.CKPTS.setdefault("s42-75k", "hybrid_3d2d-seed42/step-075000.pth")
    i, n = (int(v) for v in a.shard.split("/"))
    jobs = [(arm, seed) for arm in a.arms.split(",") for seed in ([0] if arm == "base" else [int(s) for s in a.seeds.split(",")])]
    jobs = [j for k, j in enumerate(jobs) if k % n == i]
    path = os.path.join(out, f"runs_{i}of{n}.json")
    runs = json.load(open(path)) if os.path.exists(path) else []
    done = {(r["branche"], r["graine"], r["pas"]) for r in runs}
    logf = open(os.path.join(out, f"log_{i}of{n}.txt"), "a")

    def log(*msg):
        line = time.strftime("%H:%M:%S ") + " ".join(str(m) for m in msg)
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    log("appareil", core.DEV, "| travaux", jobs)
    packs = {}
    for arm, seed in jobs:
        steps = 0 if arm == "base" else a.steps
        if (arm, seed, steps) in done:
            continue
        quotas = scale_quotas(QUOTAS["C" if arm in ("base", "C") else ("D" if arm == "D" else "N")], a.batch)
        versions = {name: {"T": "t", "S": "s"}.get(arm, "h") for name in NEW}
        key = tuple(sorted(quotas))
        if steps and key not in packs:
            t0 = time.time()
            packs[key] = FT.load_packs(a.bench, quotas)
            log(f"{len(packs[key])} paquets de tuiles chargés en {round(time.time() - t0)} s")
        log(f"--- branche {arm}, graine {seed}, {steps} pas, quotas {quotas}")
        res, _ = FT.run_arm(a.bench, a.ckpt, arm, seed, steps, quotas, versions, lr=a.lr, warmup=a.warmup,
                            packs=packs.get(key, []), log=log, eval_only=a.eval_only,
                            eval_at=[int(v) for v in a.eval_at.split(",") if v], out=out)
        res["checkpoint"] = a.ckpt
        for s, v in sorted(res["scores"].items()):
            log(f"  {s:22s} BA {v['ba']:.4f}  F1 {v['f1']:.4f}  AUC {v['auc']:.4f}  ({v['px']} px)")
        runs.append(res)
        FT.save_json(path, runs)
        FT.save_json(os.path.join(out, f"resume_{i}of{n}.json"), summarize(runs))
    log("terminé")


if __name__ == "__main__":
    main()
