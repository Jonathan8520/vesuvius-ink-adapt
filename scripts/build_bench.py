"""Construit les données du banc de mesure : tuiles d'entraînement et zones d'évaluation, au pas d'environ 9 µm.

Le banc sert à comparer, à recette égale, des affinages du modèle `ink_9um` qui ne diffèrent que par la source des
étiquettes ajoutées (carte du modèle 2 µm seuillée, ou étiquettes vérifiées à la main).

Trois familles de données, décrites dans `data/bench/manifest.json` :
- `rejeu` : le corpus de l'équipe (étiquettes `ink_9um`), pour que l'affinage n'oublie pas ce qu'il sait.
  Représentation « alignée » (scan 2,4 µm réduit, 21 couches) ou native (9,362 µm, 28 couches).
- `nouveau` : segments hors corpus, sur le canevas natif, avec deux versions d'étiquettes posées sur les mêmes
  pixels : `h` (humaines, de l'équipe, reportées du scan fin par `register.py`) et `t` (carte du modèle 2 µm
  seuillée à 128 et 64, règle de reader-v2-labels).
- `eval` : les 9 zones réservées d'`ink_9um` (jamais entraînées) et les segments de PHerc0841 (rouleau jamais vu).

Aucun rouleau éligible à First Letters. Les zones réservées et PHerc0841 ne sont jamais écrites dans `train/`.

Usage : python scripts/build_bench.py --what manifest|train|eval [--only nom ...] [--out data/bench]
"""
import argparse
import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import core, evalset as E, register as R, zarrio as Z  # noqa: E402

TILE = 256
T_HI, T_LO = 128, 64
TEACHER = "new_canon_autoresearch_recipe"
README = "https://huggingface.co/buckets/scrollprize/datasets/resolve/ink_9um/README.md"
RESERVED = ["pherc0139-w016", "pherc0139-w028", "pherc0139-w029", "pherc0814-46527", "pherc1667-w018",
            "pherc1667-w023", "pherc1667-w028", "pherc1667-w029", "pherc1667-w031"]
# nombre maximal de tuiles de rejeu par représentation (tirage fixe) : le rejeu n'a pas besoin de tout le corpus
CAP = {"PHercParis4": 150, "PHerc1667": 120, "PHerc0139": 400, "PHerc0814": 400}
# segments hors corpus : (nom, objet, identifiant, rôle)
NEW = [("pherc0500p2-m1", "PHerc0500P2", "20250825181859--1", "nouveau"),
       ("pherc0009b-ag487", "PHerc0009B", "20250919125754-auto_grown_20250919055754487_inp_hr", "nouveau"),
       ("pherc0841-w00", "PHerc0841", "20260220213127-w00", "eval"),
       ("pherc0841-ag896", "PHerc0841", "20260220214732-auto_grown_20260220144552896", "eval"),
       ("pherc0841-ag405", "PHerc0841", "20260221022814-auto_grown_20260220174252405", "eval")]


def manifest(out):
    inv = json.load(open("data/inventory/inventory.json"))["catalog"]
    text = Z.http_get(README).decode()
    rows = re.findall(r"\| (\S+) \| [^|]+ \| \[[^\]]+\]\(https://vesuvius-challenge-open-data\.s3\.amazonaws\.com/"
                      r"index\.html#([^)]+)\) \|", text)
    reps = []
    for name, prefix in rows:
        obj, _, long_id, _, vol = prefix.rstrip("/").split("/")
        native = vol.startswith("9.")
        labs = [g for g in inv[obj]["segments"].values() if g["long_id"] == long_id][0]["labels"]
        lab = [x["path"] for x in labs if (x["um"] > 5) == native]
        reps.append(dict(nom=("natif-" if native else "") + name, role="rejeu", objet=obj, segment=long_id,
                         famille="natif" if native else "aligne", volume=prefix.rstrip("/") + "/",
                         etiquettes=lab[0] if lab else None, reserve=name in RESERVED and not native))
    for name, obj, long_id, role in NEW:
        assert not inv[obj]["first_letters"], obj
        fit = R.load(os.path.join("data/register", obj, long_id + ".json"))
        labs = [g for g in inv[obj]["segments"].values() if g["long_id"] == long_id][0]["labels"]
        reps.append(dict(nom=name, role=role, objet=obj, segment=long_id, famille="natif",
                         volume=f"{obj}/segments/{long_id}/surface-volumes/{fit['volume_natif']}/",
                         volume_fin=fit["volume_fin"], etiquettes=[x["path"] for x in labs if x["um"] < 5][0],
                         recalage=dict(A=fit["A"], t=fit["t"], forme_natif=fit["forme_natif"], forme_fin=fit["forme_fin"]),
                         reserve=False))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump(reps, f, indent=1)
    print(len(reps), "représentations :", {r: sum(1 for x in reps if x["role"] == r) for r in ("rejeu", "nouveau", "eval")})


def s3_labels(path, level):
    out = {}
    for kind, key in (("inklabels", "ink"), ("supervision", "sup"), ("validation", "val")):
        try:
            out[key] = Z.RemoteArray(f"{Z.S3}{path}{kind}.zarr/{level}/", max_chunks=4)[:, :] > 0
        except FileNotFoundError:
            out[key] = None
    return out


def teacher_level2(rep, cache):
    """Carte du modèle 2 µm du segment, moyennée 4 x 4 (niveau 2 du scan fin)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import teacher_vs_team as T
    seg = f"{rep['objet']}/segments/{rep['segment']}/"
    _, keys = core.s3_list(seg + "ink-detection/")
    vol_id = rep["volume_fin"].split("volume-")[-1].replace(".zarr", "")
    key = [k for k in keys if TEACHER in k and vol_id in k and k.endswith(".tif")][0]
    path = T.download(key, cache)
    t, _ = T.teacher_level2(path, rep["recalage"]["forme_fin"])
    os.remove(path)
    return t


def labels_of(rep, cache):
    """Étiquettes 2D sur le canevas de la représentation : dict(ink, sup, val[, ink_t, sup_t])."""
    if rep["role"] == "rejeu" and rep["famille"] == "aligne":
        name = rep["nom"]
        npz = os.path.join("data/reserved", name + ".npz")
        if os.path.exists(npz):                      # étiquettes exactes du dépôt 9 µm (cas réservés)
            z = np.load(npz)
            return dict(ink=z["ink"], sup=z["sup"] & ~z["val"], val=z["val"])
        lab = s3_labels(rep["etiquettes"], 2)        # même repère que le dépôt 9 µm
        val = lab["val"] if lab["val"] is not None else np.zeros_like(lab["sup"])
        return dict(ink=lab["ink"], sup=lab["sup"] & ~val, val=val)
    if rep["role"] == "rejeu":
        lab = s3_labels(rep["etiquettes"], 0)        # étiquettes natives de l'équipe (PHerc0139)
        return dict(ink=lab["ink"], sup=lab["sup"], val=np.zeros_like(lab["sup"]))
    # segments hors corpus : étiquettes du scan fin reportées sur le canevas natif
    lab = s3_labels(rep["etiquettes"], 2)
    fit = rep["recalage"]
    to_native = lambda a: R.fine_to_native(a.astype(np.float32), fit)
    ink, sup = to_native(lab["ink"]) >= 0.5, to_native(lab["sup"]) >= 0.999   # supervision : bord exclu
    teacher = to_native(teacher_level2(rep, cache))
    return dict(ink=ink & sup, sup=sup, val=np.zeros_like(sup),
                ink_t=(teacher >= T_HI) & sup, sup_t=sup & ((teacher >= T_HI) | (teacher <= T_LO)))


def reader_of(rep):
    return E.pooled_reader(rep["volume"]) if rep["famille"] == "aligne" else E.native_reader(rep["volume"])


def build_train(rep, out, cache, rng):
    path = os.path.join(out, "train", rep["nom"] + ".npz")
    if os.path.exists(path):
        return
    lab = labels_of(rep, cache)
    read, (H, W) = reader_of(rep)
    assert lab["sup"].shape == (H, W), (rep["nom"], lab["sup"].shape, (H, W))
    assert not (lab["sup"] & lab["val"]).any()
    sup_any = lab["sup"] | lab.get("sup_t", lab["sup"])
    tiles = [(y, x) for y in range(0, H, TILE) for x in range(0, W, TILE) if sup_any[y:y + TILE, x:x + TILE].sum() >= 256]
    cap = CAP.get(rep["objet"]) if rep["role"] == "rejeu" else None
    if cap and len(tiles) > cap:
        tiles = [tiles[i] for i in sorted(rng.choice(len(tiles), cap, replace=False))]
    t0, imgs, masks = time.time(), [], {k: [] for k in lab if k != "val"}
    for y, x in tiles:
        img = read(y, min(H, y + TILE), x, min(W, x + TILE))
        pad = ((0, 0), (0, TILE - img.shape[1]), (0, TILE - img.shape[2]))
        imgs.append(np.pad(img, pad))
        for k in masks:
            m = lab[k][y:y + TILE, x:x + TILE]
            masks[k].append(np.pad(m, pad[1:]))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez(path, img=np.stack(imgs), yx=np.array(tiles, np.int32), shape=np.array([H, W]),
             **{k: np.packbits(np.stack(v), axis=-1) for k, v in masks.items()})
    print(f"train {rep['nom']} : {len(tiles)} tuiles, {np.stack(imgs).shape[1]} couches, "
          f"{int(lab['sup'].sum())} px supervisés, {round(time.time() - t0)} s", flush=True)


def build_eval(rep, out, cache):
    lab = labels_of(rep, cache)
    mask = lab["val"] if rep["role"] == "rejeu" else lab["sup"]
    if not mask.any():
        return
    read, (H, W) = reader_of(rep)
    zones = E.find_zones(mask)
    t0 = time.time()
    for i, (y0, y1, x0, x1) in enumerate(zones):
        path = os.path.join(out, "eval", f"{rep['nom']}_{i:02d}.npz")
        if os.path.exists(path):
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, img=read(y0, y1, x0, x1), roi=np.array([y0, y1, x0, x1]), shape=np.array([H, W]),
                 ink=np.packbits(lab["ink"][y0:y1, x0:x1], axis=-1), mask=np.packbits(mask[y0:y1, x0:x1], axis=-1))
    print(f"eval {rep['nom']} : {len(zones)} zones, {int(mask.sum())} px à noter, {round(time.time() - t0)} s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", choices=["manifest", "train", "eval"], required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default="data/bench")
    a = ap.parse_args()
    if a.what == "manifest":
        return manifest(a.out)
    reps = json.load(open(os.path.join(a.out, "manifest.json")))
    rng = np.random.default_rng(20261122)
    cache = os.path.join(a.out, "cache")
    for rep in reps:
        draw = np.random.default_rng(rng.integers(1 << 31))   # tirage indépendant de l'ordre et de --only
        if a.only and rep["nom"] not in a.only:
            continue
        if a.what == "train" and rep["role"] in ("rejeu", "nouveau"):
            build_train(rep, a.out, cache, draw)
        if a.what == "eval" and (rep["role"] == "eval" or rep["reserve"]):
            build_eval(rep, a.out, cache)


if __name__ == "__main__":
    main()
