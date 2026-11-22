"""Recalage 2D entre le canevas du scan fin (2,2 à 2,4 µm, niveau 2) et le canevas natif ~9 µm d'un même segment.

Les deux volumes de surface publiés pour un segment viennent du même maillage aplati, mais leurs canevas ne se
déduisent pas l'un de l'autre par le seul rapport des tailles de voxel : on mesure un écart d'échelle d'environ
0,4 % et un décalage constant de plusieurs pixels. On estime donc une transformation affine sur la texture CT
(fibres du papyrus), par corrélation de tuiles autour de la surface.

Convention : `index_fin = A @ index_natif + t`, en indices de pixel (ligne, colonne), `index_fin` au niveau 2 du
volume fin (pas de 4 voxels fins).
"""
import json

import numpy as np
import torch
import torch.nn.functional as F
from scipy import ndimage as ndi

from . import zarrio as Z


def surface_planes(url, n_layers_native_equiv=4, um=None, um_native=None):
    """Moyenne des plans autour de la surface (indice D // 2). Pour le volume fin, donner `um` (taille de voxel
    en z) et `um_native` : on moyenne la même épaisseur physique que `n_layers_native_equiv` couches natives."""
    probe = Z.RemoteArray(url, max_chunks=1)
    d, h, w = probe.shape
    half = n_layers_native_equiv // 2 if um is None else max(1, int(round(n_layers_native_equiv / 2 * um_native / um)))
    # lecture par bandes : un chunk contient tous les plans, on ne garde donc en mémoire qu'une bande à la fois
    band = 2 * probe.chunks[1]
    a = Z.RemoteArray(url, max_chunks=2 * (w // probe.chunks[2] + 2))
    out = np.zeros((h, w), np.float32)
    for y in range(0, h, band):
        out[y:y + band] = a[d // 2 - half:d // 2 + half, y:min(h, y + band), :].astype(np.float32).mean(0)
    return out


def _highpass(a):
    g = a - ndi.gaussian_filter(a, 12)
    g = ndi.gaussian_filter(g, 1.0)
    g[a <= 0] = 0
    return g


def resample(a, shape, A, t, mode="bilinear"):
    """Rééchantillonne l'image `a` (repère source) sur un canevas `shape` (repère cible), avec
    index_source = A @ index_cible + t."""
    H, W = shape
    A = np.asarray(A, np.float64)
    ys = torch.arange(H, dtype=torch.float64)[:, None]
    xs = torch.arange(W, dtype=torch.float64)[None, :]
    sy = A[0, 0] * ys + A[0, 1] * xs + t[0]
    sx = A[1, 0] * ys + A[1, 1] * xs + t[1]
    grid = torch.stack([2 * (sx + 0.5) / a.shape[1] - 1, 2 * (sy + 0.5) / a.shape[0] - 1], -1)[None].float()
    src = torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32))[None, None]
    return F.grid_sample(src, grid, mode=mode, padding_mode="zeros", align_corners=False)[0, 0].numpy()


def texture_field(native, fine, s, tile=384, min_valid=0.6):
    """Décalages locaux entre `fine` et `native` mis à l'échelle nominale `s` (fin = s * natif + d).
    Retourne un tableau (n, 5) : centre y, centre x (repère fin), dy, dx, hauteur du pic normalisée."""
    nat_w = resample(native, fine.shape, np.eye(2) / s, (0.0, 0.0))
    a, b = _highpass(nat_w), _highpass(fine)
    win = np.outer(np.hanning(tile), np.hanning(tile)).astype(np.float32)
    rows = []
    for y in range(0, fine.shape[0] - tile + 1, tile // 2):
        for x in range(0, fine.shape[1] - tile + 1, tile // 2):
            if (nat_w[y:y + tile, x:x + tile] > 0).mean() < min_valid or (fine[y:y + tile, x:x + tile] > 0).mean() < min_valid:
                continue
            p, q = a[y:y + tile, x:x + tile] * win, b[y:y + tile, x:x + tile] * win
            cc = np.fft.irfft2(np.fft.rfft2(q) * np.conj(np.fft.rfft2(p)), s=(tile, tile))
            k = np.unravel_index(np.argmax(cc), cc.shape)
            dy, dx = (k[0] + tile // 2) % tile - tile // 2, (k[1] + tile // 2) % tile - tile // 2
            # raffinement sous-pixel par parabole sur les voisins du pic
            sub = []
            for axis, kk in ((0, k[0]), (1, k[1])):
                idx = [list(k), list(k), list(k)]
                idx[0][axis], idx[2][axis] = (kk - 1) % tile, (kk + 1) % tile
                c0, c1, c2 = (cc[tuple(i)] for i in idx)
                den = c0 - 2 * c1 + c2
                sub.append(0.0 if den == 0 else float(np.clip(0.5 * (c0 - c2) / den, -0.5, 0.5)))
            peak = cc[k] / (np.sqrt(float((p ** 2).sum()) * float((q ** 2).sum())) + 1e-9)
            rows.append((y + tile / 2, x + tile / 2, dy + sub[0], dx + sub[1], peak))
    return np.array(rows, np.float64).reshape(-1, 5)


def fit_affine(rows, s, min_peak_quantile=0.2):
    """Ajuste index_fin = A @ index_natif + t à partir du champ de décalages. Régression robuste (3 passes)."""
    good = rows[rows[:, 4] >= np.quantile(rows[:, 4], min_peak_quantile)]
    X = np.c_[np.ones(len(good)), good[:, 0], good[:, 1]]
    coefs, keep_all = [], np.ones(len(good), bool)
    for i in (2, 3):
        r, keep = good[:, i], np.ones(len(good), bool)
        for _ in range(3):
            coef, *_ = np.linalg.lstsq(X[keep], r[keep], rcond=None)
            e = r - X @ coef
            keep = np.abs(e) < max(1.5, 3 * np.median(np.abs(e[keep])))
        coefs.append(coef)
        keep_all &= keep
    (a0, a1, a2), (b0, b1, b2) = coefs
    # fin = s * natif + d(fin), d = c0 + c1 * y_fin + c2 * x_fin  =>  M @ fin = s * natif + c0
    M = np.array([[1 - a1, -a2], [-b1, 1 - b2]])
    Minv = np.linalg.inv(M)
    A, t = Minv * s, Minv @ np.array([a0, b0])
    Xall = np.c_[np.ones(len(rows)), rows[:, 0], rows[:, 1]]
    err = np.hypot(rows[:, 2] - Xall @ coefs[0], rows[:, 3] - Xall @ coefs[1])
    return dict(A=A.tolist(), t=t.tolist(), s_nominal=float(s), tuiles=int(len(rows)), tuiles_gardees=int(keep_all.sum()),
                pic_median=float(np.median(rows[:, 4])), residu_median_px=float(np.median(err)),
                residu_p90_px=float(np.percentile(err, 90)), part_tuiles_sup_2px=float((err > 2).mean()))


def register(native, fine, um_native, um_fine_level, tile=384):
    """Recalage complet. `um_fine_level` : pas du niveau lu du volume fin (4 x la taille de voxel au niveau 2)."""
    s = um_native / um_fine_level
    rows = texture_field(native, fine, s, tile)
    if len(rows) < 12:
        raise ValueError(f"trop peu de tuiles valides ({len(rows)})")
    fit = fit_affine(rows, s)
    fit.update(um_natif=um_native, um_fin=um_fine_level, forme_natif=list(native.shape), forme_fin=list(fine.shape))
    return fit, rows


def fine_to_native(img_fine, fit, mode="bilinear"):
    """Reporte une image du repère fin (niveau du recalage) sur le canevas natif."""
    return resample(img_fine, fit["forme_natif"], np.array(fit["A"]), fit["t"], mode)


def native_to_fine(img_native, fit, mode="bilinear"):
    """Reporte une image du canevas natif sur le repère fin."""
    Ainv = np.linalg.inv(np.array(fit["A"]))
    return resample(img_native, fit["forme_fin"], Ainv, -Ainv @ np.array(fit["t"]), mode)


def load(path):
    with open(path) as f:
        return json.load(f)
