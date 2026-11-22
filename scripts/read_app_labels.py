"""Relit les étiquettes enregistrées par l'appli (`app/index.html`) et, pour un lot d'étalonnage, les compare
aux étiquettes de l'équipe.

Entrée : un dossier de documents JSON (un par tuile, tels que la base de l'artifact les rend, ou la « copie de
secours » de l'appli), et le dossier de vérité écrit par `scripts/make_app_tiles.py --mode etalon`.
Classes de l'appli : 0 je ne sais pas, 1 fond, 2 encre, 3 hors papyrus. Supervisé = classes 1 et 2 d'une tuile
validée.

Usage : python scripts/read_app_labels.py --docs data/app_docs/etiquettes --truth data/app_truth/etalon-m1
"""
import argparse
import base64
import glob
import json
import os

import numpy as np


def rle_decode(b64, n):
    raw, out, p, i = base64.b64decode(b64), np.zeros(n, np.uint8), 0, 0
    while i < len(raw) and p < n:
        v, run, shift = raw[i], 0, 0
        i += 1
        while True:
            b = raw[i]
            i += 1
            run |= (b & 127) << shift
            shift += 7
            if not b & 128:
                break
        out[p:p + run] = v
        p += run
    assert p == n, (p, n)
    return out


def rle_encode(a):
    a = np.asarray(a, np.uint8).ravel()
    cuts = np.flatnonzero(np.diff(a)) + 1
    starts, ends = np.r_[0, cuts], np.r_[cuts, a.size]
    out = bytearray()
    for s, e in zip(starts, ends):
        out.append(int(a[s]))
        run = int(e - s)
        while run >= 128:
            out.append((run & 127) | 128)
            run >>= 7
        out.append(run)
    return base64.b64encode(bytes(out)).decode()


def load_docs(path):
    docs = {}
    if os.path.isfile(path):                         # copie de secours : un seul JSON {tuile: document}
        for k, d in json.load(open(path)).items():
            docs[k] = d
        return docs
    for f in sorted(glob.glob(os.path.join(path, "*.json"))):
        d = json.load(open(f))
        d = d.get("data", d)
        if "rle" in d:
            docs[d["tuile"]] = d
    return docs


def iou(a, b, m):
    return float((a & b & m).sum() / max(1, ((a | b) & m).sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", required=True)
    ap.add_argument("--truth")
    ap.add_argument("--um", type=float, default=9.362)
    a = ap.parse_args()
    docs = load_docs(a.docs)
    rows, tot = [], dict(s=0, px=0)
    for tid, d in sorted(docs.items()):
        S, k = d["taille"], d.get("echelle", 1)
        cls = rle_decode(d["rle"], S * S).reshape(S, S)
        up = np.repeat(np.repeat(cls, k, 0), k, 1)                      # résolution native de la tuile
        sup, ink = (up == 1) | (up == 2), up == 2
        row = dict(tuile=tid, valide=d.get("valide"), secondes=d.get("secondes"), traits=d.get("traits"),
                   remplissages=d.get("remplissages"), supervise_cm2=round(float(sup.sum()) * (a.um * 1e-4) ** 2, 3),
                   part_encre=round(float(ink.sum() / max(1, sup.sum())), 3))
        if a.truth and os.path.exists(os.path.join(a.truth, tid + ".npz")):
            t = np.load(os.path.join(a.truth, tid + ".npz"))
            pre = np.repeat(np.repeat(t["pre"], k, 0), k, 1)
            region = t["sup"] & sup & ~t["vu"]                           # jugé par l'équipe et par l'annotateur, jamais montré
            pre_region = t["sup"] & ~t["vu"] & ((pre == 255) | (pre == 127))
            tp = int((ink & t["ink"] & region).sum())
            row.update(compare_px=int(region.sum()), iou=round(iou(ink, t["ink"], region), 3),
                       precision=round(tp / max(1, int((ink & region).sum())), 3),
                       rappel=round(tp / max(1, int((t["ink"] & region).sum())), 3),
                       iou_preetiquette=round(iou(pre == 255, t["ink"], pre_region), 3),
                       pixels_changes=int(((cls == 2) != (t["pre"] == 255)).sum()),
                       laisse_en_doute=round(float(((up == 0) & t["sup"] & ~t["vu"]).sum() / max(1, (t["sup"] & ~t["vu"]).sum())), 3))
        rows.append(row)
        if d.get("valide"):
            tot["s"] += d.get("secondes") or 0
            tot["px"] += int(sup.sum())
        print(json.dumps(row, ensure_ascii=False))
    if tot["s"]:
        cm2 = tot["px"] * (a.um * 1e-4) ** 2
        print(f"total validé : {cm2:.2f} cm² en {tot['s'] / 60:.1f} min, soit {cm2 / (tot['s'] / 3600):.1f} cm² par heure")


if __name__ == "__main__":
    main()
