"""Audit des zones de validation réservées d'ink_9um, à partir des masques publics.

Constat du 22 novembre 2026 : les checkpoints `scrollprize/ink_9um` déclarent 9 `reserved_validation_cases`, mais
le dépôt d'étiquettes 9 µm (bucket Hugging Face `scrollprize/datasets`, dossier `ink_9um/`) ne publie un
`_validation_mask` que pour 3 d'entre eux. Pour les autres, la zone réservée existe sur le bucket S3
(`<segment>/ink-labels/<volume>/<date>/validation.zarr`, niveau 2 = même repère que les étiquettes 9,6 µm) et n'a
aucun pixel commun avec le masque de supervision d'entraînement publié.

Usage :
  python scripts/audit_reserved_validation.py                  # masques seuls, aucun modèle (CPU, quelques minutes)
  python scripts/audit_reserved_validation.py --memo s43-75k   # ajoute le test de mémorisation (CPU, 30 à 60 min)
  options : --only <cas> ... ; --cache <dossier> (défaut data/reserved) ; --train-zones N (défaut 6)

Sorties : une ligne JSON par cas, et `<cache>/audit.json`.
- « proche » : part des pixels de la zone à moins de 128 px puis 256 px d'un pixel de supervision d'entraînement
  (même mesure que https://github.com/khj1222/vesuvius-challenge/blob/main/docs/17_holdout_audit.md).
- test de mémorisation : inférence officielle (fenêtre centrée, sens direct, grille globale) dans la zone réservée
  et sur un échantillon de pixels d'entraînement du même segment. Un checkpoint tardif retrouve presque
  parfaitement ses pixels d'entraînement ; une zone jamais vue garde un score nettement plus bas.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core, evalset as E, zarrio as Z  # noqa: E402

PX_CM2 = 9.596e-4 ** 2  # surface d'un pixel de niveau 2 (9,596 µm) en cm²


def load_case(name, cache):
    """Masques d'un cas réservé : supervision et encre HF (9,6 µm), validation HF si publiée, sinon validation S3."""
    path = os.path.join(cache, f"{name}.npz")
    if os.path.exists(path):
        z = np.load(path)
        return {k: z[k] for k in ("sup", "ink", "val")} | {"published": bool(z["published"]), "source": str(z["source"])}
    hf = E.labels_seen(name)
    out = {"sup": hf["sup"], "ink": hf["ink"], "published": hf["val"] is not None}
    if out["published"]:
        out["val"], out["source"] = hf["val"], "HF"
    else:
        segment = E.SEEN[name].split("surface-volumes/")[0]
        volumes, _ = core.s3_list(segment + "ink-labels/")
        if not volumes:
            out["val"], out["source"] = np.zeros_like(out["sup"]), "aucune"
        else:
            dates, _ = core.s3_list(sorted(volumes)[0])
            base = Z.S3 + sorted(dates)[-1]
            out["val"] = Z.RemoteArray(base + "validation.zarr/2/", max_chunks=4)[:, :] > 0
            out["source"] = "S3 " + sorted(dates)[-1].rstrip("/").split("/")[-1]
            assert out["val"].shape == out["sup"].shape, (name, out["val"].shape, out["sup"].shape)
    os.makedirs(cache, exist_ok=True)
    np.savez_compressed(path, **out)
    return out


def audit_masks(name, case):
    sup, ink, val = case["sup"], case["ink"], case["val"]
    labels, n = ndimage.label(val)
    dist = []
    for sl in ndimage.find_objects(labels):  # distance par îlot : mémoire bornée même sur les grands segments
        a, b = max(0, sl[0].start - 400), min(val.shape[0], sl[0].stop + 400)
        c, d = max(0, sl[1].start - 400), min(val.shape[1], sl[1].stop + 400)
        near = sup[a:b, c:d]
        dd = ndimage.distance_transform_edt(~near) if near.any() else np.full(near.shape, 1e9)
        dist.append(dd[val[a:b, c:d]].astype(np.float32))
    dist = np.concatenate(dist) if dist else np.zeros(0, np.float32)
    return dict(cas=name, masque_publie_a_9um=case["published"], source=case["source"],
                zone_px=int(val.sum()), zone_cm2=round(float(val.sum() * PX_CM2), 3),
                commun_avec_supervision_px=int((val & sup).sum()), ilots=int(n),
                part_encre=round(float(ink[val].mean()), 3) if val.any() else None,
                proche_128=round(float((dist < 128).mean()), 3) if dist.size else None,
                proche_256=round(float((dist < 256).mean()), 3) if dist.size else None)


def scores(p, y):
    pred = p >= 0.5
    tp, fp, fn, tn = (pred & y).sum(), (pred & ~y).sum(), (~pred & y).sum(), (~pred & ~y).sum()
    order = np.argsort(p, kind="stable")
    ranks = np.empty(len(p))
    ranks[order] = np.arange(1, len(p) + 1)
    auc = (ranks[y].sum() - y.sum() * (y.sum() + 1) / 2) / max(1, y.sum() * (~y).sum())
    return dict(px=int(len(p)), precision_equilibree=round(float(0.5 * (tp / max(1, tp + fn) + tn / max(1, tn + fp))), 4),
                f1=round(float(2 * tp / max(1, 2 * tp + fp + fn)), 4), auc=round(float(auc), 4))


def memorization(name, case, model, train_zones, rng):
    read, shape = E.pooled_reader(E.SEEN[name])
    idx = core.center_window(E.OUT_Z)
    out = {}
    for kind, mask in (("zone_reservee", case["val"]), ("entrainement", case["sup"])):
        zones = E.find_zones(mask)
        if kind == "entrainement" and len(zones) > train_zones:
            zones = [zones[i] for i in sorted(rng.choice(len(zones), train_zones, replace=False))]
        ps, ys = [], []
        for a, b, c, d in zones:
            yy, xx = np.nonzero(mask[a:b, c:d])
            roi = (a + yy.min(), a + yy.max() + 1, c + xx.min(), c + xx.max() + 1)
            prob, _ = core.infer_roi(read, shape, roi, model, idx)
            m = mask[roi[0]:roi[1], roi[2]:roi[3]]
            ps.append(prob[m])
            ys.append(case["ink"][roi[0]:roi[1], roi[2]:roi[3]][m])
        out[kind] = scores(np.concatenate(ps), np.concatenate(ys)) if ps else None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--cache", default="data/reserved")
    ap.add_argument("--memo", help="checkpoint pour le test de mémorisation, par exemple s43-75k")
    ap.add_argument("--train-zones", type=int, default=6)
    a = ap.parse_args()
    model = None
    if a.memo:
        seed, step = a.memo.split("-")
        core.CKPTS.setdefault(a.memo, f"hybrid_3d2d-seed{seed[1:]}/step-{int(step[:-1]) * 1000:06d}.pth")
        model = core.load_model(a.memo)
    rng = np.random.default_rng(0)
    rows, t0 = [], time.time()
    for name in E.SEEN:
        if a.only and name not in a.only:
            continue
        case = load_case(name, a.cache)
        row = audit_masks(name, case)
        if model is not None and case["val"].any():
            row["memorisation_" + a.memo] = memorization(name, case, model, a.train_zones, rng)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        with open(os.path.join(a.cache, "audit.json"), "w") as f:
            json.dump(rows, f, indent=1, ensure_ascii=False)
    pub = sum(r["zone_px"] for r in rows if r["masque_publie_a_9um"])
    hid = sum(r["zone_px"] for r in rows if not r["masque_publie_a_9um"])
    print(f"zones publiées à 9 µm : {pub} px ({pub * PX_CM2:.2f} cm2) ; zones absentes du dossier 9 µm (publiées dans le repère 2,4 µm) : {hid} px "
          f"({hid * PX_CM2:.2f} cm2) ; {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
