"""Construit le jeu d'évaluation local : une zone .npz par îlot annoté (entrée à ~9 µm + étiquettes).

Usage : python scripts/build_evalset.py [--out data/eval] [--only pherc0814-46527 ...] [--family seen unseen]

- « seen »   : 9 segments réservés de ink_9um, entrée 2,4 µm réduite à 21 couches (représentation « pooled »).
- « unseen » : PHerc. 0841 (3 segments) et PHerc. 0009B (1 segment), représentation « pooled » (étiquettes S3
  de niveau 2, même repère que la surface 2,4 µm de niveau 2).
État au 22/11/2026 : outil expérimental, essayé sur deux segments seulement (pherc0814-46527 et pherc0841-w00).
La représentation native (~9 µm) des segments non vus n'est pas faite : le recalage entre les deux repères
(6 à 8 px d'après d'autres auteurs) reste à vérifier.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import evalset as E  # noqa: E402


def build_segment(name, family, out_dir):
    t0 = time.time()
    if family == "seen":
        lab = E.labels_seen(name)
        surface = E.SEEN[name]
    else:
        lab = E.labels_unseen(name, level=2)
        surface = E.UNSEEN[name]["seg"] + E.UNSEEN[name]["sv24"]
    ink, sup = lab["ink"], lab["sup"]
    val = lab["val"] if lab["val"] is not None else np.zeros_like(sup)
    read, (H, W) = E.pooled_reader(surface)
    assert (H, W) == ink.shape, (name, (H, W), ink.shape)
    # zone à lire : supervision et validation pour un segment vu ; supervision seule pour un segment non vu, dont
    # le masque de validation de l'équipe (modèle 2,4 µm) couvre presque toute la surface
    annot = (sup | val) if family == "seen" else sup
    zones = E.find_zones(annot)
    seg_dir = os.path.join(out_dir, family, name)
    rows = []
    for k, (a, b, c, d) in enumerate(zones):
        sub = annot[a:b, c:d]
        yy, xx = np.nonzero(sub)
        roi = [int(a + yy.min()), int(a + yy.max() + 1), int(c + xx.min()), int(c + xx.max() + 1)]
        image = read(a, b, c, d)
        meta = dict(segment=name, scroll=E.scroll_of(name), family=family, representation="pooled21",
                    surface=surface, zone=k, origin=[int(a), int(c)], shape=[int(b - a), int(d - c)],
                    full_shape=[int(H), int(W)], roi=roi, layers=int(image.shape[0]), pixel_um=9.6)
        E.save_zone(os.path.join(seg_dir, f"pooled21_{k:03d}.npz"), image, ink[a:b, c:d], sup[a:b, c:d],
                    val[a:b, c:d], meta)
        rows.append(dict(zone=k, origin=meta["origin"], shape=meta["shape"], roi=roi,
                         sup_px=int(sup[a:b, c:d].sum()), val_px=int(val[a:b, c:d].sum()),
                         ink_px=int((ink & annot)[a:b, c:d].sum()), vide=float((image[image.shape[0] // 2] == 0).mean())))
    info = dict(segment=name, family=family, full_shape=[int(H), int(W)], zones=rows,
                sup_px=int(sup.sum()), val_px=int(val.sum()), ink_in_sup_px=int((ink & sup).sum()),
                ink_out_px=int((ink & ~annot).sum()), val_in_sup=float((sup & val).sum() / max(1, val.sum())),
                bytes_read=int(read.array.downloaded), seconds=round(time.time() - t0, 1))
    with open(os.path.join(seg_dir, "info.json"), "w") as f:
        json.dump(info, f, indent=1)
    area = sum(r["shape"][0] * r["shape"][1] for r in rows)
    print(f"{name} [{family}] : {len(zones)} zones, {area / 1e6:.1f} Mpx lus, supervision {info['sup_px'] * 9.6e-4 ** 2:.2f} cm2, "
          f"validation {info['val_px'] * 9.6e-4 ** 2:.2f} cm2 (dont {info['val_in_sup']:.0%} dans la supervision), "
          f"encre {info['ink_in_sup_px'] / max(1, info['sup_px']):.1%} de la supervision, "
          f"{info['bytes_read'] / 1e9:.2f} Go, {info['seconds']:.0f} s", flush=True)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/eval")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--family", nargs="*", default=["seen", "unseen"])
    a = ap.parse_args()
    todo = [(n, "seen") for n in E.SEEN if "seen" in a.family] + [(n, "unseen") for n in E.UNSEEN if "unseen" in a.family]
    for name, family in todo:
        if a.only and name not in a.only:
            continue
        build_segment(name, family, a.out)


if __name__ == "__main__":
    main()
