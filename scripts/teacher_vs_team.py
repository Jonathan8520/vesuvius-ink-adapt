"""Marge de la correction humaine : la carte du modèle 2 µm de l'équipe contre les étiquettes humaines de l'équipe.

Pour chaque segment qui a des étiquettes de l'équipe sur S3 (jeu `ink-labels`), on compare, dans le repère du scan
fin, la carte publiée du modèle 2 µm (`new_canon_autoresearch_recipe`) aux étiquettes humaines, au pas d'environ
9 µm (niveau 2). La comparaison est faite séparément dans la zone de validation (que le modèle 2 µm n'a pas vue à
l'entraînement, d'après les masques de l'équipe) et dans le reste de la supervision.

Pré-étiquette évaluée : la règle de reader-v2-labels (encre si carte >= 128, fond si carte <= 64, bande
intermédiaire laissée de côté).

Usage : python scripts/teacher_vs_team.py [--only PHerc0500P2 ...] [--cache data/teacher]
Sortie : une ligne par segment, et data/teacher/teacher_vs_team.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import tifffile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core, zarrio as Z  # noqa: E402

TEACHER = "new_canon_autoresearch_recipe"
T_HI, T_LO = 128, 64


def download(key, cache):
    path = os.path.join(cache, key.replace("/", "__"))
    if not os.path.exists(path):
        os.makedirs(cache, exist_ok=True)
        with Z._SESSION.get(Z.S3 + key, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path + ".part", "wb") as f:
                for block in r.iter_content(1 << 22):
                    f.write(block)
        os.replace(path + ".part", path)
    return path


def teacher_level2(path, shape2, strip=4096):
    """Carte du modèle 2 µm (niveau 0 du scan fin) ramenée au niveau 2 par moyenne 4 x 4."""
    with tifffile.TiffFile(path) as tif:
        full = tif.series[0].levels[0].asarray()
    if full.ndim == 3:
        full = full[..., 0]
    h2, w2 = shape2
    if abs(full.shape[0] - 4 * h2) > 8 or abs(full.shape[1] - 4 * w2) > 8:
        raise ValueError(f"carte {full.shape} incompatible avec les étiquettes de niveau 2 {shape2}")
    out = np.zeros(shape2, np.float32)
    h, w = min(h2, full.shape[0] // 4), min(w2, full.shape[1] // 4)
    for y in range(0, h, strip // 4):
        y1 = min(h, y + strip // 4)
        blk = full[4 * y:4 * y1, :4 * w].astype(np.float32)
        out[y:y1, :w] = blk.reshape(y1 - y, 4, w, 4).mean((1, 3))
    return out, full.shape


def compare(teacher, ink, region):
    t, y = teacher[region], ink[region]
    n = int(region.sum())
    if n == 0 or y.sum() == 0:
        return None
    pre_ink, pre_bg = t >= T_HI, t <= T_LO
    band = ~pre_ink & ~pre_bg
    tp, fp, fn = int((pre_ink & y).sum()), int((pre_ink & ~y).sum()), int((~pre_ink & y).sum())
    order = np.argsort(t, kind="stable")
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)
    auc = (ranks[y].sum() - y.sum() * (y.sum() + 1) / 2) / max(1, int(y.sum()) * int((~y).sum()))
    # seuil optimal (F1) : sépare l'erreur de calibrage de l'erreur de classement
    hist_ink = np.bincount(np.clip(t[y], 0, 255).astype(np.int64), minlength=256)
    hist_bg = np.bincount(np.clip(t[~y], 0, 255).astype(np.int64), minlength=256)
    tp_t = hist_ink[::-1].cumsum()[::-1].astype(np.float64)   # encre humaine avec carte >= seuil
    fp_t = hist_bg[::-1].cumsum()[::-1].astype(np.float64)
    f1_t = 2 * tp_t / np.maximum(1, tp_t + fp_t + y.sum())
    k = int(np.argmax(f1_t))
    return dict(px=n, part_encre=round(float(y.mean()), 3), auc=round(float(auc), 4),
                precision=round(tp / max(1, tp + fp), 3), rappel=round(tp / max(1, tp + fn), 3),
                iou=round(tp / max(1, tp + fp + fn), 3), f1=round(2 * tp / max(1, 2 * tp + fp + fn), 3),
                seuil_opt=k, f1_opt=round(float(f1_t[k]), 3),
                bande=round(float(band.mean()), 3),                       # part de la zone dans la bande 64..128
                encre_dans_bande=round(float((band & y).sum() / max(1, y.sum())), 3),   # encre humaine tombée dans la bande
                encre_dite_fond=round(float((pre_bg & y).sum() / max(1, y.sum())), 3),  # encre humaine que la carte dit fond
                fond_dit_encre=round(float((pre_ink & ~y).sum() / max(1, (~y).sum())), 4))  # fond humain que la carte dit encre


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--cache", default="data/teacher")
    a = ap.parse_args()
    inv = json.load(open("data/inventory/inventory.json"))["catalog"]
    out_json = os.path.join(a.cache, "teacher_vs_team.json")
    rows = json.load(open(out_json)) if os.path.exists(out_json) else []
    done = {(r["objet"], r["segment"]) for r in rows}
    for obj, c in sorted(inv.items()):
        if a.only and obj not in a.only:
            continue
        if c["first_letters"]:
            continue  # jamais d'étiquettes ni de mesure d'étiquetage sur un rouleau éligible
        for gid, g in sorted(c["segments"].items()):
            labs = [lab for lab in g["labels"] if c["volumes"][lab["volume"]]["kind"] == "fin"]
            if not labs:
                continue
            if (obj, g["long_id"]) in done:
                continue
            lab = labs[-1]
            seg = f"{obj}/segments/{g['long_id']}/"
            _, keys = core.s3_list(seg + "ink-detection/")
            maps = [k for k in keys if TEACHER in k and lab["volume"] in k and k.endswith(".tif")]
            if not maps:
                print(f"{obj} {g['long_id']} : pas de carte {TEACHER} sur le volume {lab['volume']}", flush=True)
                continue
            base = Z.S3 + lab["path"]
            ink, sup = (Z.RemoteArray(f"{base}{k}.zarr/2/", max_chunks=4)[:, :] > 0 for k in ("inklabels", "supervision"))
            try:
                val = Z.RemoteArray(f"{base}validation.zarr/2/", max_chunks=4)[:, :] > 0
            except FileNotFoundError:
                val = np.zeros_like(sup)  # segment sans zone de validation
            path = download(maps[0], a.cache)
            teacher, full_shape = teacher_level2(path, ink.shape)
            row = dict(objet=obj, segment=g["long_id"], pas_um=round(lab["um"] * 4, 2), carte=list(full_shape),
                       validation=compare(teacher, ink, sup & val), reste=compare(teacher, ink, sup & ~val))
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
            os.remove(path)
            with open(out_json, "w") as f:
                json.dump(rows, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
