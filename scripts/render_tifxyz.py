"""Rendu d'une surface tifxyz depuis un volume OME-Zarr distant (S3), par tuiles.

- positions : interpolation bilinéaire de la grille xyz (pixel (r, c) <-> grille (r*scale, c*scale))
- normales : produit vectoriel des dérivées de la grille, interpolées puis normalisées
- échantillonnage trilinéaire du volume (ordre z, y, x) à p + k*n pour chaque décalage k
- les chunks 128^3 nécessaires sont téléchargés à la demande et gardés sur disque
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import tifffile
import zarr
from scipy.ndimage import map_coordinates

B = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"


class RemoteVolume:
    def __init__(self, s3_level_prefix: str, cache_root: str):
        self.prefix = s3_level_prefix.rstrip("/") + "/"
        self.root = os.path.join(cache_root, self.prefix)
        meta = json.loads(urllib.request.urlopen(B + self.prefix + ".zarray", timeout=30).read())
        self.shape = tuple(meta["shape"])
        self.chunks = tuple(meta["chunks"])
        self.sep = meta.get("dimension_separator", ".")
        assert meta.get("compressor") is None and meta["dtype"] == "|u1", meta

    def _path(self, key):
        return os.path.join(self.root, self.sep.join(map(str, key)))

    def _fetch(self, key):
        p = self._path(key)
        if os.path.exists(p):
            return
        os.makedirs(os.path.dirname(p), exist_ok=True)
        url = B + urllib.parse.quote(self.prefix + self.sep.join(map(str, key)))
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                data = b""  # chunk absent = vide (masqué)
            else:
                raise
        with open(p + ".part", "wb") as f:
            f.write(data)
        os.replace(p + ".part", p)

    def _load(self, key):
        p = self._path(key)
        raw = open(p, "rb").read()
        if not raw:
            return np.zeros(self.chunks, np.uint8)
        return np.frombuffer(raw, np.uint8).reshape(self.chunks)

    def block(self, lo, hi, workers=16):
        """Bloc dense [lo, hi) en (z, y, x)."""
        lo = [max(0, int(v)) for v in lo]
        hi = [min(s, int(v)) for v, s in zip(hi, self.shape)]
        ranges = [range(l // c, (h - 1) // c + 1) for l, h, c in zip(lo, hi, self.chunks)]
        keys = [(a, b, c) for a in ranges[0] for b in ranges[1] for c in ranges[2]]
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(self._fetch, keys))
        out = np.zeros([h - l for l, h in zip(lo, hi)], np.uint8)
        for key in keys:
            ch = self._load(key)
            c0 = [k * c for k, c in zip(key, self.chunks)]
            s = [max(l, a) for l, a in zip(lo, c0)]
            e = [min(h, a + c) for h, a, c in zip(hi, c0, self.chunks)]
            out[s[0] - lo[0]:e[0] - lo[0], s[1] - lo[1]:e[1] - lo[1], s[2] - lo[2]:e[2] - lo[2]] = \
                ch[s[0] - c0[0]:e[0] - c0[0], s[1] - c0[1]:e[1] - c0[1], s[2] - c0[2]:e[2] - c0[2]]
        return out, lo, len(keys)


def load_grid(tifxyz_dir):
    m = json.load(open(os.path.join(tifxyz_dir, "meta.json")))
    g = np.stack([tifffile.imread(os.path.join(tifxyz_dir, f"{a}.tif")).astype(np.float64) for a in "xyz"], -1)
    valid = (g > 0).all(-1) & np.isfinite(g).all(-1)
    return g, valid, float(m["scale"][0])


def grid_normals(g, valid):
    d_col = np.zeros_like(g)
    d_row = np.zeros_like(g)
    d_col[:, 1:-1] = (g[:, 2:] - g[:, :-2]) / 2
    d_col[:, 0] = g[:, 1] - g[:, 0]
    d_col[:, -1] = g[:, -1] - g[:, -2]
    d_row[1:-1] = (g[2:] - g[:-2]) / 2
    d_row[0] = g[1] - g[0]
    d_row[-1] = g[-1] - g[-2]
    n = np.cross(d_col, d_row)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    # validité des normales : voisins valides
    vv = valid.copy()
    vv[:, 1:-1] &= valid[:, 2:] & valid[:, :-2]
    vv[1:-1] &= valid[2:] & valid[:-2]
    return n, vv


def bilinear(field, valid, rr, cc):
    """Interpole field (Hg, Wg, k) aux coordonnées grille (rr, cc). Renvoie valeurs et validité."""
    Hg, Wg = valid.shape
    r0 = np.clip(np.floor(rr).astype(int), 0, Hg - 2)
    c0 = np.clip(np.floor(cc).astype(int), 0, Wg - 2)
    fr = (rr - r0)[..., None]
    fc = (cc - c0)[..., None]
    v = valid[r0, c0] & valid[r0 + 1, c0] & valid[r0, c0 + 1] & valid[r0 + 1, c0 + 1]
    val = (field[r0, c0] * (1 - fr) * (1 - fc) + field[r0 + 1, c0] * fr * (1 - fc)
           + field[r0, c0 + 1] * (1 - fr) * fc + field[r0 + 1, c0 + 1] * fr * fc)
    return val, v


def render(tifxyz_dir, vol: RemoteVolume, out_zarr, offsets, tile=256, roi=None, flip_normal=False, log_every=10):
    g, valid, scale = load_grid(tifxyz_dir)
    n, nvalid = grid_normals(g, valid)
    if flip_normal:
        n = -n
    H, W = int(round(g.shape[0] / scale)), int(round(g.shape[1] / scale))
    r0, r1, c0, c1 = roi if roi else (0, H, 0, W)
    L = len(offsets)
    out = zarr.open(out_zarr, mode="w", shape=(L, r1 - r0, c1 - c0), chunks=(L, 128, 128), dtype="u1")
    offs = np.asarray(offsets, np.float64)
    t0 = time.time()
    tiles = [(a, b) for a in range(r0, r1, tile) for b in range(c0, c1, tile)]
    nchunks = 0
    for i, (ta, tb) in enumerate(tiles):
        ha, hb = min(tile, r1 - ta), min(tile, c1 - tb)
        rr, cc = np.meshgrid(np.arange(ta, ta + ha) * scale, np.arange(tb, tb + hb) * scale, indexing="ij")
        pos, pv = bilinear(g, valid, rr, cc)
        nor, nv = bilinear(n, valid & nvalid, rr, cc)
        ok = pv & nv
        if not ok.any():
            continue
        nor /= np.maximum(np.linalg.norm(nor, axis=-1, keepdims=True), 1e-9)
        pts = pos[None] + offs[:, None, None, None] * nor[None]  # (L, ha, hb, 3) en x, y, z
        sel = pts[:, ok]
        lo = np.floor(sel.min(axis=(0, 1)))[::-1] - 1  # -> z, y, x
        hi = np.ceil(sel.max(axis=(0, 1)))[::-1] + 2
        blk, lo_i, k = vol.block(lo, hi)
        nchunks += k
        coords = np.stack([sel[..., 2] - lo_i[0], sel[..., 1] - lo_i[1], sel[..., 0] - lo_i[2]])
        samp = map_coordinates(blk, coords.reshape(3, -1), order=1, mode="constant", cval=0).reshape(L, -1)
        res = np.zeros((L, ha, hb), np.uint8)
        res[:, ok] = np.clip(np.round(samp), 0, 255).astype(np.uint8)
        out[:, ta - r0:ta - r0 + ha, tb - c0:tb - c0 + hb] = res
        if i % log_every == 0:
            print(f"  tuile {i + 1}/{len(tiles)} | {time.time() - t0:.0f} s | bloc {tuple(blk.shape)} | {nchunks} chunks lus", flush=True)
    print(f"rendu fini en {time.time() - t0:.0f} s -> {out_zarr} {out.shape}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tifxyz_dir")
    ap.add_argument("volume_s3_level")
    ap.add_argument("out_zarr")
    ap.add_argument("--cache", default="data")
    ap.add_argument("--offset-min", type=int, default=-14)
    ap.add_argument("--offset-max", type=int, default=13)
    ap.add_argument("--roi", type=int, nargs=4)
    ap.add_argument("--tile", type=int, default=256)
    ap.add_argument("--flip-normal", action="store_true")
    a = ap.parse_args()
    vol = RemoteVolume(a.volume_s3_level, a.cache)
    render(a.tifxyz_dir, vol, a.out_zarr, list(range(a.offset_min, a.offset_max + 1)), a.tile, a.roi, a.flip_normal)


if __name__ == "__main__":
    main()
