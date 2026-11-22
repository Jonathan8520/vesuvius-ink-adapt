"""Pré-étiquettes sur le canevas natif ~9 µm : carte du modèle 2 µm de l'équipe reportée par le recalage de
`register.py`, puis seuillée (encre si >= 128, fond si <= 64, règle de reader-v2-labels).

Pour chaque segment déjà recalé (`data/register/<objet>/<segment>.json`), écrit dans
`data/prelabels/<objet>/<segment>/` : `carte.png` (carte du modèle, 0 à 255, canevas natif) et `stats.json`.
Aucun rouleau éligible à First Letters.

Usage : python scripts/make_prelabels.py --object PHerc0500P2 --match 2025082518 20250628074500
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vesuvius_ink_adapt import core, register as R  # noqa: E402
import teacher_vs_team as T  # noqa: E402

T_HI, T_LO = 128, 64
Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--object", required=True)
    ap.add_argument("--match", nargs="*")
    ap.add_argument("--out", default="data/prelabels")
    a = ap.parse_args()
    inv = json.load(open("data/inventory/inventory.json"))["catalog"][a.object]
    assert not inv["first_letters"], "jamais de pré-étiquette sur un rouleau éligible à First Letters"
    for path in sorted(glob.glob(os.path.join("data/register", a.object, "*.json"))):
        fit = R.load(path)
        seg = fit["segment"]
        if a.match and not any(m in seg for m in a.match):
            continue
        out = os.path.join(a.out, a.object, seg)
        if os.path.exists(os.path.join(out, "stats.json")):
            continue
        _, keys = core.s3_list(f"{a.object}/segments/{seg}/ink-detection/")
        vol_id = fit["volume_fin"].split("volume-")[-1].replace(".zarr", "")
        maps = [k for k in keys if T.TEACHER in k and vol_id in k and k.endswith(".tif")]
        if not maps:
            print(seg, ": pas de carte du modèle 2 µm")
            continue
        tif = T.download(maps[0], os.path.join(a.out, "cache"))
        teacher2, _ = T.teacher_level2(tif, fit["forme_fin"])
        os.remove(tif)
        native = np.clip(np.rint(R.fine_to_native(teacher2, fit)), 0, 255).astype(np.uint8)
        valid = R.fine_to_native(np.ones(fit["forme_fin"], np.float32), fit) >= 0.999
        os.makedirs(out, exist_ok=True)
        Image.fromarray(native).save(os.path.join(out, "carte.png"), optimize=True)
        stats = dict(objet=a.object, segment=seg, forme=list(native.shape), carte_source=maps[0],
                     recalage=dict(A=fit["A"], t=fit["t"], residu_median_px=fit["residu_median_px"]),
                     part_valide=round(float(valid.mean()), 4),
                     part_encre=round(float((native >= T_HI)[valid].mean()), 4),
                     part_bande=round(float(((native > T_LO) & (native < T_HI))[valid].mean()), 4),
                     surface_cm2=round(float(valid.sum()) * (fit["um_natif"] * 1e-4) ** 2, 2))
        with open(os.path.join(out, "stats.json"), "w") as f:
            json.dump(stats, f, indent=1, ensure_ascii=False)
        print(f"{seg} : {native.shape}, encre {100 * stats['part_encre']:.1f} %, bande {100 * stats['part_bande']:.1f} %, "
              f"{stats['surface_cm2']} cm²", flush=True)


if __name__ == "__main__":
    main()
