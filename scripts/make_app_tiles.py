"""Découpe des tuiles pour l'appli d'étiquetage au stylet (`app/`), sur le canevas natif ~9 µm d'un segment.

Pour chaque tuile : une planche JPEG (panneaux côte à côte : composite CT autour de la surface, cinq couches CT,
carte du modèle 2 µm reportée) et un PNG de pré-étiquette (0 = je ne sais pas, 64 = hors papyrus, 127 = fond,
255 = encre ; règle
de reader-v2-labels : encre si carte >= 128, fond si <= 64). Écrit aussi `manifest.json`.

Mode `etalon` : tuiles d'un segment déjà annoté par l'équipe, pour une séance en aveugle. Les étiquettes de
l'équipe ne sont PAS écrites dans le dossier de l'appli : elles vont dans `--truth` pour la comparaison.
Mode `production` : moitié des tuiles par incertitude (pixels de la bande 64..128 et bords de taches), moitié
au hasard parmi celles qui contiennent de l'encre prédite.

Aucun rouleau éligible à First Letters. Images dérivées de « Vesuvius Challenge - CT Scans of Herculaneum
Papyri » (CC BY-NC 4.0).

Usage : python scripts/make_app_tiles.py --object PHerc0500P2 --segment 20250825181859--1 --set etalon-m1 \
            --mode etalon --count 12 --seen 2700,3340,690,1730
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import evalset as E, register as R, zarrio as Z  # noqa: E402

T_HI, T_LO = 128, 64
LAYERS = [10, 12, 14, 16, 18]          # couches natives montrées (14 = surface, 28 couches)
COMPOSITE = (11, 18)                   # moyenne des couches 11 à 17
Image.MAX_IMAGE_PIXELS = None


def stretch(a, valid):
    """Étire le contraste entre les centiles 1 et 99 des pixels valides."""
    if not valid.any():
        return np.zeros(a.shape, np.uint8)
    lo, hi = np.percentile(a[valid], [1, 99])
    return np.clip((a.astype(np.float32) - lo) / max(1.0, hi - lo) * 255, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", required=True)
    ap.add_argument("--segment", required=True)
    ap.add_argument("--set", required=True, help="nom du lot de tuiles")
    ap.add_argument("--mode", choices=["etalon", "production"], required=True)
    ap.add_argument("--count", type=int, default=12)
    ap.add_argument("--size", type=int, default=768, help="taille de la tuile de travail, en pixels réduits")
    ap.add_argument("--scale", type=int, default=2, help="réduction : une tuile couvre size x scale pixels natifs")
    ap.add_argument("--exclude", default="", help="y0,y1,x0,x1 (canevas natif) : tuiles à écarter si elles touchent cette zone")
    ap.add_argument("--seen", default="", help="y0,y1,x0,x1 (canevas natif) : zone déjà montrée avec ses étiquettes, à retirer du score")
    ap.add_argument("--min-sup", type=int, default=30000, help="mode etalon : pixels supervisés par l'équipe au minimum")
    ap.add_argument("--out", default="data/app")
    ap.add_argument("--truth", default="data/app_truth")
    ap.add_argument("--seed", type=int, default=20261123)
    a = ap.parse_args()
    inv = json.load(open("data/inventory/inventory.json"))["catalog"][a.object]
    assert not inv["first_letters"], "jamais de tuiles d'étiquetage sur un rouleau éligible à First Letters"
    fit = R.load(os.path.join("data/register", a.object, a.segment + ".json"))
    carte = np.asarray(Image.open(os.path.join("data/prelabels", a.object, a.segment, "carte.png")))
    read, (H, W) = E.native_reader(f"{a.object}/segments/{a.segment}/surface-volumes/{fit['volume_natif']}/")
    assert carte.shape == (H, W), (carte.shape, (H, W))
    S, rng = a.size * a.scale, np.random.default_rng(a.seed)   # S : côté de la tuile en pixels natifs

    def grid(n):
        g = list(range(0, max(1, n - S + 1), S))
        return g + ([n - S] if n > S and (n - S) % S else [])     # dernière tuile alignée sur le bord

    def down(img, mean=True):
        """Réduit une image (S, S) d'un facteur `scale` par moyenne de blocs."""
        k = a.scale
        v = img.astype(np.float32).reshape(a.size, k, a.size, k).mean((1, 3))
        return v if mean else v >= 0.5
    truth = None
    if a.mode == "etalon":
        lab = [x for g in inv["segments"].values() if g["long_id"] == a.segment for x in g["labels"] if x["um"] < 5][0]
        t = {k: Z.RemoteArray(f"{Z.S3}{lab['path']}{n}.zarr/2/", max_chunks=4)[:, :] > 0 for k, n in (("ink", "inklabels"), ("sup", "supervision"))}
        truth = {k: R.fine_to_native(v.astype(np.float32), fit) >= (0.999 if k == "sup" else 0.5) for k, v in t.items()}
        truth["ink"] &= truth["sup"]
    ex = [int(v) for v in a.exclude.split(",")] if a.exclude else None
    cands = []
    for y in grid(H):
        for x in grid(W):
            if ex and y < ex[1] and y + S > ex[0] and x < ex[3] and x + S > ex[2]:
                continue
            c = carte[y:y + S, x:x + S]
            if c.shape != (S, S):
                continue
            ink, band = int((c >= T_HI).sum()), int(((c > T_LO) & (c < T_HI)).sum())
            sup = int(truth["sup"][y:y + S, x:x + S].sum()) if truth else 0
            cands.append(dict(y=y, x=x, encre=ink, bande=band, sup=sup))
    if a.mode == "etalon":
        chosen = []
        for c in sorted(cands, key=lambda c: -c["sup"]):          # glouton, sans recouvrement de plus de 20 %
            ov = max([max(0, S - abs(c["y"] - d["y"])) * max(0, S - abs(c["x"] - d["x"])) / S ** 2 for d in chosen] or [0])
            if c["sup"] >= a.min_sup and ov <= 0.2 and len(chosen) < a.count:
                chosen.append(c)
        cands = chosen
        for c in cands:
            c["tirage"] = "etalon"
    else:
        with_ink = [c for c in cands if c["encre"] >= 2000]
        by_unc = sorted(with_ink, key=lambda c: -c["bande"])[:a.count // 2]
        rest = [c for c in with_ink if c not in by_unc]
        rnd = [rest[i] for i in rng.choice(len(rest), min(len(rest), a.count - len(by_unc)), replace=False)]
        for c in by_unc:
            c["tirage"] = "incertitude"
        for c in rnd:
            c["tirage"] = "hasard"
        cands = by_unc + rnd
    order = rng.permutation(len(cands))            # ordre de présentation mélangé
    out = os.path.join(a.out, a.set)
    os.makedirs(os.path.join(out, "t"), exist_ok=True)
    os.makedirs(os.path.join(a.truth, a.set), exist_ok=True)
    tiles = []
    for rank, i in enumerate(order):
        c = cands[int(i)]
        y, x = c["y"], c["x"]
        tid = f"{a.set}-{y:05d}-{x:05d}"
        vol = read(y, y + S, x, x + S)
        valid = down(vol[LAYERS].max(0) > 0) >= 0.5
        panels = [stretch(down(vol[COMPOSITE[0]:COMPOSITE[1]].astype(np.float32).mean(0)), valid)]
        panels += [stretch(down(vol[k]), valid) for k in LAYERS]
        m = np.clip(np.rint(down(carte[y:y + S, x:x + S])), 0, 255).astype(np.uint8)
        panels.append(np.where(valid, m, 0).astype(np.uint8))   # carte masquée là où le scan ~9 µm n'a pas de donnée
        Image.fromarray(np.concatenate(panels, 1)).save(os.path.join(out, "t", tid + ".jpg"), quality=88, subsampling=0)
        pre = np.where(m >= T_HI, 255, np.where(m <= T_LO, 127, 0)).astype(np.uint8)
        pre[~valid] = 64                                   # hors papyrus : verrouillé dans l'appli
        Image.fromarray(pre).save(os.path.join(out, "t", tid + ".png"), optimize=True)
        tiles.append(dict(id=tid, segment=a.segment, y=y, x=x, taille=a.size, echelle=a.scale, tirage=c["tirage"], rang=rank,
                          planche=f"t/{tid}.jpg", pre=f"t/{tid}.png"))
        if truth:
            seen = np.zeros((S, S), bool)
            if a.seen:
                sy0, sy1, sx0, sx1 = (int(v) for v in a.seen.split(","))
                seen[max(0, sy0 - y):max(0, sy1 - y), max(0, sx0 - x):max(0, sx1 - x)] = True
            # vérité à la résolution native de la tuile (S x S) ; `pre` et `carte` à la résolution de travail
            np.savez_compressed(os.path.join(a.truth, a.set, tid + ".npz"), ink=truth["ink"][y:y + S, x:x + S],
                                sup=truth["sup"][y:y + S, x:x + S], pre=pre, carte=m, vu=seen)
        print(f"{tid} : {c['tirage']}, encre prédite {c['encre']} px, bande {c['bande']} px, supervisé par l'équipe {c['sup']} px", flush=True)
    manifest = dict(lot=a.set, objet=a.object, segment=a.segment, um=fit["um_natif"], taille=a.size, echelle=a.scale, mode=a.mode,
                    panneaux=["CT (composite)"] + [f"CT couche {k - 14:+d}" for k in LAYERS] + ["Carte du modèle 2 µm"],
                    source="Vesuvius Challenge - CT Scans of Herculaneum Papyri (CC BY-NC 4.0)", tuiles=tiles)
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    size = sum(os.path.getsize(os.path.join(out, "t", n)) for n in os.listdir(os.path.join(out, "t")))
    print(len(tiles), "tuiles,", round(size / 1e6, 1), "Mo dans", out)


if __name__ == "__main__":
    main()
