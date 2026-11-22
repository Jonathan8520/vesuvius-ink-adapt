"""Jeu d'évaluation : segments étiquetés publics, entrées à ~9 µm et étiquettes, découpés en petites zones.

Deux familles (voir docs/RESEARCH.md) :
- « vu » : les 9 segments `reserved_validation_cases` de `ink_9um` (PHerc. 0139, 0814, 1667). Les checkpoints ont
  été entraînés sur ces segments ; seules les zones `validation_mask` (3 segments) sont tenues à l'écart.
  Entrée : surface publique à 2,4 µm ramenée à 9,6 µm (niveau 2 en XY, moyenne de 4 plans en Z, 21 couches).
- « non vu » : PHerc. 0841 (3 segments) et PHerc. 0009B (1 segment), absents de l'entraînement de `ink_9um`.
  Entrées : la même réduction de la surface 2,4 µm (« pooled ») et la surface native à ~9 µm (« native »).

Une « zone » est un rectangle autour d'un îlot annoté, élargi pour contenir toutes les tuiles officielles
(grille de pas 64) qui touchent un pixel annoté. Chaque zone est enregistrée dans un fichier .npz autonome.
"""
import json
import os
import re

import numpy as np
from scipy import ndimage

from . import zarrio

P, STRIDE = 128, 64
POOL_Z, OUT_Z = 4, 21  # 84 plans centrés de la surface 2,4 µm -> 21 couches (prepare_9um_isotropic_input.py)
HF_LABELS = "ink_9um/labels/aligned-scrollprizeorg-21slices/"

SEEN = {
    "pherc0139-w016": "PHerc0139/segments/20250108000004-w029_2025010827/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr/",
    "pherc0139-w028": "PHerc0139/segments/20260115000000-w044_2026011522/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr/",
    "pherc0139-w029": "PHerc0139/segments/20260126000000-w045_2026012619/surface-volumes/2.399um-0.22m-78keV-volume-20260102150214.zarr/",
    "pherc0814-46527": "PHerc0814/segments/20260226000000-46527_2um_try2/surface-volumes/2.399um-0.22m-78keV-volume-20260309142202.zarr/",
    "pherc1667-w018": "PHerc1667/segments/20240304144031-w018_20240304144031_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr/",
    "pherc1667-w023": "PHerc1667/segments/20240304161941-w023_20240304161941_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr/",
    "pherc1667-w028": "PHerc1667/segments/20251208130119-w028_20251208130119156_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr/",
    "pherc1667-w029": "PHerc1667/segments/20251212185248-w029_20251212185248662_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr/",
    "pherc1667-w031": "PHerc1667/segments/20251223230000-w031_2025122323_flatboi/surface-volumes/2.399um-0.22m-78keV-volume-20251217075048.zarr/",
}

UNSEEN = {
    "pherc0841-w00": dict(
        seg="PHerc0841/segments/20260220213127-w00/",
        sv24="surface-volumes/2.403um-0.22m-77keV-volume-20260319124803.zarr/",
        sv9="surface-volumes/9.366um-1.2m-113keV-volume-20250821151531.zarr/",
        labels="ink-labels/2.403um-volume-20260319124803/20260918/"),
    "pherc0841-ag144552896": dict(
        seg="PHerc0841/segments/20260220214732-auto_grown_20260220144552896/",
        sv24="surface-volumes/2.403um-0.22m-77keV-volume-20260319124803.zarr/",
        sv9="surface-volumes/9.366um-1.2m-113keV-volume-20250821151531.zarr/",
        labels="ink-labels/2.403um-volume-20260319124803/20260918/"),
    "pherc0841-ag174252405": dict(
        seg="PHerc0841/segments/20260221022814-auto_grown_20260220174252405/",
        sv24="surface-volumes/2.403um-0.22m-77keV-volume-20260319124803.zarr/",
        sv9="surface-volumes/9.366um-1.2m-113keV-volume-20250821151531.zarr/",
        labels="ink-labels/2.403um-volume-20260319124803/20260918/"),
    "pherc0009b-ag055754487": dict(
        seg="PHerc0009B/segments/20250919125754-auto_grown_20250919055754487_inp_hr/",
        sv24="surface-volumes/2.401um-0.35m-77keV-volume-20250820154339.zarr/",
        sv9="surface-volumes/8.64um-1.2m-116keV-volume-20250521125136.zarr/",
        labels="ink-labels/2.401um-volume-20250820154339/20260918/"),
}


def scroll_of(name):
    return name.split("-")[0]


# ------------------------------------------------------------------ étiquettes
def labels_seen(name):
    """Étiquettes 9,6 µm d'un segment « vu » : dict(ink, sup, val) de tableaux 2D booléens (val=None si absent).

    Le bucket Hugging Face limite le nombre de requêtes : on liste d'abord les chunks, et on ne télécharge que
    ceux dont l'empreinte diffère de celle du chunk vide. Les étiquettes ne sont posées qu'au plan Z = 10.
    """
    files = zarrio.hf_tree(HF_LABELS + name)
    out = {}
    for kind, key in (("inklabels", "ink"), ("supervision_mask", "sup"), ("validation_mask", "val")):
        prefix = f"{HF_LABELS}{name}/{name}_{kind}.zarr/0/"
        chunks = [(p[len(prefix):], h) for p, _, h in files
                  if p.startswith(prefix) and re.fullmatch(r"\d+([./]\d+)+", p[len(prefix):])]
        if not chunks:
            out[key] = None
            continue
        hashes = [h for _, h in chunks]
        empty = max(set(hashes), key=hashes.count)
        arr = zarrio.RemoteArray(zarrio.HF_BUCKET + prefix, max_chunks=100000,
                                 skip={k for k, h in chunks if h == empty})
        gz, gy, gx = (-(-s // c) for s, c in zip(arr.shape, arr.chunks))
        assert gz == 1, arr.chunks
        full = np.zeros(arr.shape[1:], bool)
        todo = sorted({tuple(int(v) for v in k.split(arr.sep)) for k, h in chunks if h != empty})
        got = arr._chunks_for(todo)
        for (_, cy, cx), ch in got.items():
            planes = np.nonzero(ch.reshape(ch.shape[0], -1).any(1))[0]
            assert set(planes.tolist()) <= {arr.shape[0] // 2}, (name, kind, planes)
            y0, x0 = cy * arr.chunks[1], cx * arr.chunks[2]
            blk = ch[arr.shape[0] // 2] > 0
            h, w = min(arr.chunks[1], arr.shape[1] - y0), min(arr.chunks[2], arr.shape[2] - x0)
            full[y0:y0 + h, x0:x0 + w] = blk[:h, :w]
        out[key] = full
    return out


def labels_unseen(name, level=2):
    """Étiquettes S3 (Zarr v3) d'un segment « non vu », au niveau demandé (2 = 9,6 µm) : dict(ink, sup, val)."""
    d = UNSEEN[name]
    base = zarrio.S3 + d["seg"] + d["labels"]
    return {key: zarrio.RemoteArray(f"{base}{kind}.zarr/{level}/", max_chunks=4)[:, :] > 0
            for kind, key in (("inklabels", "ink"), ("supervision", "sup"), ("validation", "val"))}


def resample_mask(mask, shape):
    """Ramène un masque 2D sur une grille de forme `shape` couvrant le même domaine (moyenne de surface, seuil 0,5)."""
    zy, zx = shape[0] / mask.shape[0], shape[1] / mask.shape[1]
    return ndimage.zoom(mask.astype(np.float32), (zy, zx), order=1, grid_mode=True, mode="nearest") >= 0.5


# ------------------------------------------------------------------ zones
def _tile_span(lo, hi, length):
    """Étendue [a, b) couverte par les tuiles officielles (pas 64, taille 128) qui touchent [lo, hi)."""
    if length <= P:
        return 0, length
    last = length - P
    starts = list(range(0, last + 1, STRIDE))
    if starts[-1] != last:
        starts.append(last)
    hit = [s for s in starts if s < hi and s + P > lo]
    return hit[0], min(length, hit[-1] + P)


def find_zones(annot, gap=192):
    """Rectangles autour des îlots annotés d'un masque 2D, élargis aux tuiles officielles qui les touchent.

    Deux îlots séparés de moins de `gap` pixels sont regroupés. Renvoie [(y0, y1, x0, x1)] avec, pour chaque
    zone, toutes les tuiles de la grille globale qui recouvrent un pixel annoté de l'îlot.
    """
    H, W = annot.shape
    if not annot.any():
        return []
    cell = 64
    coarse = np.zeros((-(-H // cell), -(-W // cell)), bool)
    ys, xs = np.nonzero(annot)
    coarse[ys // cell, xs // cell] = True
    r = max(1, int(round(gap / cell / 2)))
    lab, n = ndimage.label(ndimage.binary_dilation(coarse, np.ones((2 * r + 1, 2 * r + 1), bool)))
    lab[~coarse] = 0
    zones = []
    for sl in ndimage.find_objects(lab):
        if sl is None:
            continue
        y0, y1 = sl[0].start * cell, min(H, sl[0].stop * cell)
        x0, x1 = sl[1].start * cell, min(W, sl[1].stop * cell)
        sub = annot[y0:y1, x0:x1]
        yy, xx = np.nonzero(sub)
        if yy.size == 0:
            continue
        a, b = _tile_span(y0 + yy.min(), y0 + yy.max() + 1, H)
        c, d = _tile_span(x0 + xx.min(), x0 + xx.max() + 1, W)
        zones.append((a, b, c, d))
    return _merge_overlapping(zones)


def _merge_overlapping(zones):
    zones = list(zones)
    changed = True
    while changed:
        changed = False
        out = []
        while zones:
            a, b, c, d = zones.pop()
            k = 0
            while k < len(zones):
                e, f, g, h = zones[k]
                if a < f and e < b and c < h and g < d:
                    a, b, c, d = min(a, e), max(b, f), min(c, g), max(d, h)
                    zones.pop(k)
                    changed = True
                    k = 0
                else:
                    k += 1
            out.append((a, b, c, d))
        zones = out
    return sorted(zones)


# ------------------------------------------------------------------ entrées
def pooled_reader(surface_prefix, level=2):
    """Lecteur de la représentation « alignée » : surface 2,4 µm au niveau 2, 84 plans centrés moyennés par 4.

    Renvoie (read, (H, W)) où read(y0, y1, x0, x1) -> uint8 (21, h, w). Même arrondi que l'outil officiel.
    """
    arr = zarrio.RemoteArray(zarrio.S3 + surface_prefix + f"{level}/", max_chunks=64)
    depth = arr.shape[0]
    z0 = -(-(depth - OUT_Z * POOL_Z) // 2)  # math.ceil : marge impaire placée avant la tranche

    def read(y0, y1, x0, x1, tile=512):
        out = np.zeros((OUT_Z, y1 - y0, x1 - x0), np.uint8)
        for ya in range(y0, y1, tile):
            for xa in range(x0, x1, tile):
                yb, xb = min(y1, ya + tile), min(x1, xa + tile)
                blk = arr[z0:z0 + OUT_Z * POOL_Z, ya:yb, xa:xb].astype(np.float32)
                out[:, ya - y0:yb - y0, xa - x0:xb - x0] = np.rint(
                    blk.reshape(OUT_Z, POOL_Z, yb - ya, xb - xa).mean(axis=1)).astype(np.uint8)
        return out

    read.array = arr
    return read, arr.shape[1:]


def native_reader(surface_prefix):
    """Lecteur d'une surface native à ~9 µm (28 ou 31 couches) : (read, (H, W)), read -> uint8 (L, h, w)."""
    arr = zarrio.RemoteArray(zarrio.S3 + surface_prefix + "0/", max_chunks=256)

    def read(y0, y1, x0, x1):
        return arr[:, y0:y1, x0:x1]

    read.array = arr
    return read, arr.shape[1:]


# ------------------------------------------------------------------ fichiers de zones
def save_zone(path, image, ink, sup, val, meta):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez_compressed(path, image=image, ink=np.packbits(ink), sup=np.packbits(sup), val=np.packbits(val),
                        meta=json.dumps(meta))


def load_zone(path):
    z = np.load(path)
    meta = json.loads(str(z["meta"]))
    h, w = meta["shape"]
    un = lambda k: np.unpackbits(z[k])[:h * w].reshape(h, w).astype(bool)
    return dict(image=z["image"], ink=un("ink"), sup=un("sup"), val=un("val"), meta=meta)
