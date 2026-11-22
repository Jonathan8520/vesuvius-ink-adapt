"""Vérifie que notre chaîne reproduit les sorties officielles du Vesuvius Challenge.

Deux contrôles sur le segment PHerc. 211 « crop1711-lines123-v9 » (lettres connues, données publiques) :
1. rendu : notre rendu tifxyz contre la surface officielle (vc_render_tifxyz), couche par couche ;
2. encre : notre inférence ink_9um (seed43, step 20k) contre la prédiction officielle publiée
   avec le même checkpoint.

Usage : python tests/validate_against_official.py   (CPU suffit, ~1 min)
Seuils : corrélation moyenne > 0,85 pour le rendu ; > 0,99 pour l'encre sur la grille officielle
(et > 0,85 sur la grille locale au recadrage, ancienne mesure).
"""
import io
import os
import sys

import numpy as np
import tifffile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core  # noqa: E402

SEG = "PHerc0211/segments/20261028201525-crop1711-lines123-v9/"
MESH = SEG + "mesh/20261028201525-on-20250821151803-9.362um.tifxyz/"
SURF = SEG + "surface-volumes/9.362um-1.2m-113keV-volume-20250821151803.zarr/0/"
PRED = SEG + ("ink-detection/PHerc0211-20261028201525-9.362um-1.2m-113keV-volume-20250821151803-"
              "20260814010243-ink9um-hybrid3d2d-s43-20k-tile128-stride64.tif")
VOLUME = "PHerc0211/volumes/20250821151803-9.362um-1.2m-113keV-masked.zarr/0/"


def corr(a, b):
    m = (a > 0) & (b > 0)
    return float(np.corrcoef(a[m].astype(np.float64), b[m].astype(np.float64))[0, 1])


def main():
    ok = True
    # 1. rendu
    vol = core.RemoteVolume(VOLUME, max_chunks=200)
    g, valid, scale, _ = core.load_tifxyz(MESH)
    roi = (600, 856, 4400, 4656)
    mine = core.render(g, valid, scale, vol, roi=roi)
    official = core.RemoteVolume(SURF, max_chunks=50)
    ref, _ = official.block((0, roi[0], roi[2]), (28, roi[1], roi[3]))
    rs = [corr(mine[i], ref[i]) for i in range(28)]
    print(f"rendu : corrélation moyenne {np.mean(rs):.3f} (min {np.min(rs):.3f}) sur 28 couches")
    ok &= np.mean(rs) > 0.85
    # 2. encre, tuiles sur la grille globale comme l'outil officiel : doit être quasi identique
    y0, y1, x0, x1 = 0, 1720, 4000, 4500
    depth, height, width = official.shape
    model = core.load_model("s43-20k")
    pub = tifffile.imread(io.BytesIO(core.http_get(core.S3 + PRED))).astype(np.float32)[y0:y1, x0:x1]
    m = pub > 0

    def read(a, b, c, d):
        return official.block((0, a, c), (depth, b, d))[0]

    prob, n = core.infer_roi(read, (height, width), (y0, y1, x0, x1), model, core.center_window(depth))
    r = float(np.corrcoef(prob[m], pub[m])[0, 1])
    ecart = np.abs(np.floor(np.clip(prob, 0, 1) * 255)[m] - pub[m])
    print(f"encre (grille officielle) : corrélation {r:.4f} avec la prédiction officielle ({n} patchs), "
          f"écart max {ecart.max():.0f} niveau(x) sur 255")
    ok &= r > 0.99
    # 3. encre, grille locale au recadrage (ancienne mesure, gardée pour détecter une régression de core.infer)
    prob2, n2 = core.infer(read(y0, y1, x0, x1), model, 6, False)
    r2 = float(np.corrcoef(prob2[m], pub[m])[0, 1])
    print(f"encre (grille locale au recadrage) : corrélation {r2:.3f} ({n2} patchs)")
    ok &= r2 > 0.85
    print("VALIDATION OK" if ok else "VALIDATION ÉCHOUÉE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
