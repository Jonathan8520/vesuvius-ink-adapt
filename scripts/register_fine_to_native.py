"""Recale le canevas du scan fin (niveau 2) sur le canevas natif ~9 µm, par la texture CT, segment par segment.

Pour chaque segment hors concours qui a un volume de surface fin et un volume de surface ~9 µm, écrit
`data/register/<objet>/<segment>.json` : transformation affine `index_fin = A @ index_natif + t` et résidus.
Sert à reporter sur la surface ~9 µm les cartes du modèle 2 µm et les étiquettes posées sur le scan fin.

Usage : python scripts/register_fine_to_native.py --objects PHerc0500P2 [--match 2025082518] [--coarse]
        python scripts/register_fine_to_native.py --table      (tableau récapitulatif)
"""
import argparse
import glob
import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core, register as R, zarrio as Z  # noqa: E402

OUT = "data/register"


def volumes_of(obj, long_id):
    """Volumes de surface du segment : [(nom, taille de voxel en µm)]."""
    prefixes, _ = core.s3_list(f"{obj}/segments/{long_id}/surface-volumes/")
    out = []
    for p in prefixes:
        name = p.rstrip("/").split("/")[-1]
        m = re.match(r"([0-9.]+)um", name)
        if m and name.endswith(".zarr"):
            out.append((name, float(m.group(1))))
    return out


def pick(vols, labelled_volume=None):
    """Le volume ~9 µm (7 à 10 µm) et le volume fin (le plus fin, ou celui des étiquettes s'il est donné)."""
    native = [v for v in vols if 7 <= v[1] <= 10]
    fine = [v for v in vols if v[1] <= 2.6]
    if labelled_volume:
        fine = [v for v in fine if labelled_volume in v[0]] or fine
    if not native or not fine:
        return None, None
    return min(native, key=lambda v: v[1]), min(fine, key=lambda v: v[1])


def run(obj, long_id, labelled_volume, coarse, force=False):
    path = os.path.join(OUT, obj, long_id + ".json")
    if os.path.exists(path) and not force:
        return json.load(open(path))
    native, fine = pick(volumes_of(obj, long_id), labelled_volume)
    if native is None:
        return None
    base = f"{Z.S3}{obj}/segments/{long_id}/surface-volumes/"
    ln, lf = (1, 3) if coarse else (0, 2)
    t0 = time.time()
    a = R.surface_planes(f"{base}{native[0]}/{ln}/")
    b = R.surface_planes(f"{base}{fine[0]}/{lf}/", um=fine[1], um_native=native[1])
    fit, rows = R.register(a, b, native[1] * 2 ** ln, fine[1] * 2 ** lf, tile=192 if coarse else 384)
    if coarse:  # ramener au repère de référence : natif niveau 0, fin niveau 2 (les deux niveaux sont réduits de 2)
        fit["t"] = [2 * v for v in fit["t"]]
        fit["forme_natif"], fit["forme_fin"] = [2 * v for v in fit["forme_natif"]], [2 * v for v in fit["forme_fin"]]
        for k in ("residu_median_px", "residu_p90_px"):
            fit[k] *= 2
        fit["um_natif"], fit["um_fin"] = native[1], fine[1] * 4
    fit.update(objet=obj, segment=long_id, volume_natif=native[0], volume_fin=fine[0], niveaux=[ln, lf],
               secondes=round(time.time() - t0))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(fit, f, indent=1)
    np.save(path.replace(".json", ".field.npy"), rows)
    return fit


def table():
    rows = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(OUT, "*", "*.json")))]
    print("| Objet | Segment | Échelle (y, x) | Décalage (px) | Résidu médian / p90 (px) | Tuiles > 2 px |")
    print("| --- | --- | --- | --- | --- | --- |")
    for r in rows:
        A = np.array(r["A"])
        print(f"| {r['objet']} | `{r['segment']}` | {A[0, 0]:.4f}, {A[1, 1]:.4f} | {r['t'][0]:.1f}, {r['t'][1]:.1f} | "
              f"{r['residu_median_px']:.2f} / {r['residu_p90_px']:.2f} | {100 * r['part_tuiles_sup_2px']:.1f} % |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--objects", nargs="*", default=[])
    ap.add_argument("--match", nargs="*", help="sous-chaînes de l'identifiant du segment")
    ap.add_argument("--coarse", action="store_true", help="natif niveau 1 et fin niveau 3 (8 fois moins de données)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()
    if a.table:
        return table()
    inv = json.load(open("data/inventory/inventory.json"))["catalog"]
    for obj in a.objects:
        c = inv[obj]
        if c["first_letters"]:
            print(f"{obj} : éligible à First Letters, ignoré")  # aucun calcul sur un rouleau éligible
            continue
        for gid, g in sorted(c["segments"].items()):
            if a.match and not any(m in g["long_id"] for m in a.match):
                continue
            if not (g["surfaces"].get("fin") and g["surfaces"].get("9um")):
                continue
            lab = [x["volume"] for x in g["labels"] if c["volumes"][x["volume"]]["kind"] == "fin"]
            try:
                fit = run(obj, g["long_id"], lab[-1] if lab else None, a.coarse, a.force)
            except Exception as e:  # un segment qui échoue ne bloque pas les autres
                print(f"{obj} {g['long_id']} : ÉCHEC {type(e).__name__} {e}", flush=True)
                continue
            if fit is None:
                continue
            A = np.array(fit["A"])
            print(f"{obj} {g['long_id']} : échelle {A[0, 0]:.4f} {A[1, 1]:.4f}, décalage {fit['t'][0]:.1f} {fit['t'][1]:.1f}, "
                  f"résidu médian {fit['residu_median_px']:.2f} px, p90 {fit['residu_p90_px']:.2f}, "
                  f"{fit['tuiles_gardees']}/{fit['tuiles']} tuiles, {fit.get('secondes', 0)} s", flush=True)


if __name__ == "__main__":
    main()
