"""Inventaire : rouleaux, scans, surfaces, cartes d'encre et étiquettes d'encre déjà publiées.

But (étape 1 du plan « étiquettes vérifiées à la main ») : savoir, pour chaque objet du bucket public, s'il est
éligible à un prix, s'il a un scan fin et un scan à ~9 µm, combien de segments ont une surface rendue aux deux
résolutions, quelles cartes d'encre l'équipe a publiées, et quelles étiquettes existent déjà (équipe et communauté).

Sources, toutes publiques :
- catalogue du bucket S3 (`metadata.json`, compressé en gzip) ;
- liste des volumes éligibles (`prizeEligibility.json` du dépôt ScrollPrize/villa) ;
- étiquettes de l'équipe : `ink-labels` du catalogue (S3, jeu du 18/09/2026) et dossier `ink_9um/` du bucket Hugging Face ;
- étiquettes de la communauté : reader-v2-labels (Domenico Russo), Studio et Expanded9 (Priyank Aranke),
  ink-8um-pherc1447-surfaces (Youssef Nader).

Usage : python scripts/inventory.py [--eligibility chemin/prizeEligibility.json] [--out docs/INVENTAIRE.md]
Écrit aussi data/inventory/inventory.json (non suivi par git).
"""
import argparse
import csv
import gzip
import io
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vesuvius_ink_adapt import zarrio as Z  # noqa: E402

HF = "https://huggingface.co/"
ELIGIBILITY_URL = "https://raw.githubusercontent.com/ScrollPrize/villa/main/scrollprize.org/src/data/prizeEligibility.json"
FINE_MAX_UM, COARSE_MIN_UM, COARSE_MAX_UM = 5.0, 7.0, 10.0
CACHE = "data/inventory"


def fetch(url, name, binary=False):
    """Télécharge une fois dans data/inventory/, puis relit le fichier local."""
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        data = Z.http_get(url)
        if data is None:
            raise FileNotFoundError(url)
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return data if binary else data.decode("utf-8")


def kind_of(um):
    if um is None:
        return "?"
    if um <= FINE_MAX_UM:
        return "fin"
    if COARSE_MIN_UM <= um <= COARSE_MAX_UM:
        return "9um"
    return "autre"


def cm2(px, um):
    return px * (um * 1e-4) ** 2


def load_catalog(eligibility_path):
    meta = json.loads(fetch(Z.S3 + "metadata.json", "metadata.json"))
    if eligibility_path:
        with open(eligibility_path) as f:
            elig = json.load(f)
    else:
        elig = json.loads(fetch(ELIGIBILITY_URL, "prizeEligibility.json"))
    fl = {e["scroll"] for e in elig["first-letters-2027"]}
    gp = {e["scroll"] for e in elig["grand-prize-2027"]}
    models = {mid: (m.get("suffix") or m.get("long_id") or mid) for mid, m in meta["models"].items()}
    tasks = {mid: (m.get("properties") or {}).get("task") for mid, m in meta["models"].items()}
    out = {}
    for sid, s in meta["samples"].items():
        vols = {}
        for vid, v in s["volumes"].items():
            p = v.get("properties") or {}
            vols[vid] = dict(um=p.get("pixel_size_um"), kev=p.get("energy_keV"), kind=kind_of(p.get("pixel_size_um")))
        segs = {}
        for gid, g in s["segments"].items():
            surf, maps, labels = Counter(), [], []
            for d in g.get("data") or []:
                par = d.get("parameters") or {}
                tv = par.get("target_volume")
                if d["type"] == "layers-zarr" and tv in vols:
                    surf[vols[tv]["kind"]] += 1
                elif d["type"] == "ink-detection" and tasks.get(par.get("model_id")) == "ink-detection":
                    maps.append((models.get(par.get("model_id"), par.get("model_id")), vols.get(tv, {}).get("kind", "?")))
                elif d["type"] == "ink-labels":
                    pr = d.get("properties") or {}
                    labels.append(dict(label_set=pr.get("label_set"), volume=tv, um=vols.get(tv, {}).get("um"),
                                       labelled_px=pr.get("labelled_px"), supervised_px=pr.get("supervised_px"),
                                       annotated_on=pr.get("annotated_on"), registration=pr.get("registration"),
                                       path=d["origins"][0]["path"]))
            segs[gid] = dict(long_id=g.get("long_id"), surfaces=dict(surf), maps=maps, labels=labels)
        out[sid] = dict(type=((s["sample"].get("properties") or {}).get("type")), first_letters=sid in fl,
                        grand_prize=sid in gp, volumes=vols, segments=segs)
    return out, elig


def community_labels():
    """Étiquettes publiées hors du bucket S3, résumées par objet. Clés : nom d'objet du bucket (PHercXXXX)."""
    out = defaultdict(list)
    # 1. ink_9um (équipe, Hugging Face) : 24 segments 2,4 µm réduits + 5 natifs
    for folder, what in (("aligned-scrollprizeorg-21slices", "2,4 µm réduit à 9,6 µm"),
                         ("native9-scrollprizeorg-21slices", "natif 9,362 µm")):
        txt = fetch(Z.HF_TREE + f"ink_9um/labels/{folder}?recursive=false&limit=1000", f"hf_ink9um_{folder}.json")
        names = [e["path"].split("/")[-1] for e in json.loads(txt) if e["type"] == "directory"]
        per = Counter()
        for n in names:
            key = {"pherc0139": "PHerc0139", "pherc0814": "PHerc0814", "pherc1667": "PHerc1667",
                   "phercparis4": "PHercParis4"}.get(n.split("-")[0], "PHerc0139")  # les natifs wNNN sont PHerc0139
            per[key] += 1
        for key, n in per.items():
            out[key].append(dict(jeu="ink_9um (équipe)", segments=n, resolution=what, main="oui (annotation de l'équipe)",
                                 licence="voir dl.ash2txt.org/LICENSE.txt", url=HF + "buckets/scrollprize/datasets/tree/ink_9um"))
    # 2. reader-v2-labels (Domenico Russo) : sorties du modèle 2 µm reportées sur scans natifs, non vérifiées
    rows = list(csv.DictReader(io.StringIO(fetch(HF + "datasets/domenicor046/reader-v2-labels/resolve/main/manifest.csv",
                                                 "reader-v2-manifest.csv"))))
    per = defaultdict(lambda: [0, 0])
    for r in rows:
        key = "PHerc" + r["object"]
        per[key][0] += 1
        per[key][1] += int(r["supervised_px"])
    for key, (n, px) in per.items():
        out[key].append(dict(jeu="reader-v2-labels (D. Russo)", segments=n, supervised_px=px, resolution="natif 8 à 9 µm",
                             main="non (cartes du modèle 2 µm de l'équipe, seuillées)", licence="MIT",
                             url=HF + "datasets/domenicor046/reader-v2-labels"))
    # 3. Studio (Priyank Aranke) : pré-étiquettes du modèle 2 µm reportées à ~9 µm puis vérifiées à la main
    d = json.loads(fetch(HF + "datasets/paranke/vesuvius-814-841-9b-studio-training-data/resolve/main/"
                         "donor-studio-resunet-scratch-20260926/data.json", "paranke-studio-data.json"))
    per = defaultdict(lambda: [0, 0, []])
    for s in d["segments"]:
        p = per[s["scroll"]]
        p[0] += 1
        p[1] += int(s.get("supervised_ink") or 0) + int(s.get("supervised_background") or 0)
        p[2].append(int(s.get("revision") or 0))
    for key, (n, px, revs) in per.items():
        out[key].append(dict(jeu="Studio (P. Aranke)", segments=n, supervised_px=px, resolution="natif ~9 µm, surfaces de l'auteur",
                             main=f"oui (corrigé à la main, médiane {sorted(revs)[len(revs) // 2]} révisions par segment)",
                             licence="CC BY-NC 4.0", url=HF + "datasets/paranke/vesuvius-814-841-9b-studio-training-data"))
    # 4. Expanded9 (Priyank Aranke) : rassemble des étiquettes existantes de 12 groupes de rouleaux
    d = json.loads(fetch(HF + "datasets/paranke/vesuvius-expanded9-training-data/resolve/main/data.json", "expanded9-data.json"))
    per = defaultdict(Counter)
    for s in d["segments"]:
        src = str(s.get("source"))
        src = "ink_9um de l'équipe" if "scrollprize" in src else src
        per[s["scroll"]][src] += 1
    for key, c in per.items():
        out[key].append(dict(jeu="Expanded9 (P. Aranke)", segments=sum(c.values()), resolution="~9 µm",
                             main="reprise d'étiquettes existantes : " + ", ".join(f"{k} ×{v}" for k, v in c.items()),
                             licence="CC BY-NC 4.0", url=HF + "datasets/paranke/vesuvius-expanded9-training-data"))
    # 5. PHerc1447 (Youssef Nader)
    out["PHerc1447"].append(dict(jeu="ink-8um-pherc1447-surfaces (Y. Nader)", segments=2, resolution="natif 8,64 µm",
                                 main="oui (étiquettes de l'auteur)", licence="CC BY-NC 4.0",
                                 url=HF + "datasets/YoussefMoNader/ink-8um-pherc1447-surfaces"))
    return dict(out)


def summarize(cat, comm):
    rows = []
    for sid, s in sorted(cat.items()):
        if not s["volumes"]:
            continue
        kinds = Counter(v["kind"] for v in s["volumes"].values())
        segs = s["segments"].values()
        both = sum(1 for g in segs if g["surfaces"].get("fin") and g["surfaces"].get("9um"))
        fine_map = sum(1 for g in segs if any(k == "fin" for _, k in g["maps"]))
        coarse_models = Counter(m for g in segs for m, k in g["maps"] if k == "9um")
        labs = [lab for g in segs for lab in g["labels"]]
        rows.append(dict(
            objet=sid, type=s["type"], first_letters=s["first_letters"], grand_prize=s["grand_prize"],
            scans=sorted({(v["um"], v["kev"]) for v in s["volumes"].values() if v["um"]}),
            scan_fin=kinds.get("fin", 0) > 0, scan_9um=kinds.get("9um", 0) > 0, segments=len(s["segments"]),
            seg_surface_fine=sum(1 for g in segs if g["surfaces"].get("fin")),
            seg_surface_9um=sum(1 for g in segs if g["surfaces"].get("9um")), seg_deux_surfaces=both,
            seg_carte_modele_fin=fine_map, cartes_9um=dict(coarse_models),
            etiquettes_s3=dict(segments=len({lab["path"].split("/")[2] for lab in labs}),
                               supervised_cm2=round(sum(cm2(lab["supervised_px"] or 0, lab["um"] or 0) for lab in labs), 1),
                               labelled_cm2=round(sum(cm2(lab["labelled_px"] or 0, lab["um"] or 0) for lab in labs), 1),
                               jeux=sorted({str(lab["label_set"]) for lab in labs})),
            etiquettes_s3_detail=sorted(labs, key=lambda lab: lab["path"]), communaute=comm.get(sid, [])))
    return rows


def fmt_scans(scans):
    return ", ".join(f"{um:g} µm" + (f" ({kev:g} keV)" if kev else "") for um, kev in scans)


def write_markdown(rows, elig, path):
    L = ["# Inventaire : rouleaux, scans et étiquettes d'encre existantes", "",
         "Produit par `python scripts/inventory.py` à partir du catalogue du bucket public (`metadata.json`), de la liste",
         "des volumes éligibles (`prizeEligibility.json` de villa) et des fiches des jeux d'étiquettes publiés.",
         "« Fin » : voxel de 5 µm ou moins. « ~9 µm » : voxel entre 7 et 10 µm.", "",
         f"Liste First Letters ({len(elig['first-letters-2027'])} rouleaux) : "
         + ", ".join(sorted(e["scroll"].replace("PHerc", "") for e in elig["first-letters-2027"])) + ".",
         f"Liste Grand Prize ({len(elig['grand-prize-2027'])} rouleaux) : "
         + ", ".join(sorted(e["scroll"].replace("PHerc", "") for e in elig["grand-prize-2027"])) + ".", ""]
    cand = [r for r in rows if not r["first_letters"] and r["scan_fin"] and r["scan_9um"]]
    L += ["## 1. Objets hors First Letters qui ont un scan fin et un scan à ~9 µm", "",
          "Ce sont les seuls où une carte du modèle 2 µm peut servir de pré-étiquette pour une surface à ~9 µm.", "",
          "| Objet | Grand Prize ? | Scans | Segments (surface fine / ~9 µm / les deux) | Carte du modèle fin | Étiquettes de l'équipe sur S3 | Étiquettes déjà publiées à ~9 µm |",
          "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in cand:
        e = r["etiquettes_s3"]
        um9 = next(um for um, _ in r["scans"] if COARSE_MIN_UM <= um <= COARSE_MAX_UM)  # pas du scan à ~9 µm de l'objet
        comm = "<br>".join(
            f"{c['jeu']} : {c['segments']} seg."
            + (f", {cm2(c['supervised_px'], um9):.0f} cm²" if c.get("supervised_px") else "")
            + f" ; vérifié à la main : {c['main']}" for c in r["communaute"]) or "aucune"
        L.append(f"| {r['objet']} | {'oui' if r['grand_prize'] else 'non'} | {fmt_scans(r['scans'])} | "
                 f"{r['segments']} ({r['seg_surface_fine']} / {r['seg_surface_9um']} / {r['seg_deux_surfaces']}) | "
                 f"{r['seg_carte_modele_fin']} seg. | "
                 + (f"{e['segments']} seg., {e['supervised_cm2']} cm² supervisés" if e["segments"] else "aucune") + f" | {comm} |")
    others = [r for r in rows if r not in cand]
    L += ["", "## 2. Autres objets", "",
          "| Objet | First Letters ? | Grand Prize ? | Scans | Segments | Étiquettes publiées |", "| --- | --- | --- | --- | --- | --- |"]
    for r in others:
        e = r["etiquettes_s3"]
        lab = [f"équipe (S3) : {e['segments']} seg."] if e["segments"] else []
        lab += [f"{c['jeu']} : {c['segments']} seg." for c in r["communaute"]]
        L.append(f"| {r['objet']} | {'**oui**' if r['first_letters'] else 'non'} | {'oui' if r['grand_prize'] else 'non'} | "
                 f"{fmt_scans(r['scans'])} | {r['segments']} | {' ; '.join(lab) or 'aucune'} |")
    L += ["", "## 3. Cartes d'encre publiées par l'équipe sur les surfaces à ~9 µm (nombre de segments par modèle)", "",
          "| Objet | Modèles |", "| --- | --- |"]
    for r in rows:
        if r["cartes_9um"]:
            L.append(f"| {r['objet']} | " + ", ".join(f"{m} ×{n}" for m, n in sorted(r["cartes_9um"].items())) + " |")
    L += ["", "## 4. Étiquettes de l'équipe republiées sur S3 (`ink-labels`), segment par segment", "",
          "Surfaces en cm² au pas du scan annoté. « Encre » : pixels étiquetés encre. Chemin : `<segment>/ink-labels/<volume>/<jeu>/`.", "",
          "| Objet | Segment | Jeu | Scan | Supervisé | Encre | Recalage |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        for lab in r["etiquettes_s3_detail"]:
            L.append(f"| {r['objet']} | {lab['path'].split('/')[2]} | {lab['label_set']} | {lab['um']:g} µm | "
                     f"{cm2(lab['supervised_px'] or 0, lab['um']):.2f} cm² | {cm2(lab['labelled_px'] or 0, lab['um']):.2f} cm² | "
                     f"{lab['registration']} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eligibility")
    ap.add_argument("--out", default="docs/INVENTAIRE.md")
    a = ap.parse_args()
    cat, elig = load_catalog(a.eligibility)
    rows = summarize(cat, community_labels())
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, "inventory.json"), "w") as f:
        json.dump(dict(rows=rows, catalog=cat), f, indent=1, ensure_ascii=False, default=list)
    write_markdown(rows, elig, a.out)
    cand = [r for r in rows if not r["first_letters"] and r["scan_fin"] and r["scan_9um"]]
    print(f"{len(rows)} objets avec scan ; {len(cand)} hors First Letters avec scan fin et scan ~9 µm : "
          + ", ".join(r["objet"] for r in cand))


if __name__ == "__main__":
    main()
