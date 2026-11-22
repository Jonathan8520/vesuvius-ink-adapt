# Inventaire : rouleaux, scans et étiquettes d'encre existantes

Produit par `python scripts/inventory.py` à partir du catalogue du bucket public (`metadata.json`), de la liste
des volumes éligibles (`prizeEligibility.json` de villa) et des fiches des jeux d'étiquettes publiés.
« Fin » : voxel de 5 µm ou moins. « ~9 µm » : voxel entre 7 et 10 µm.

Liste First Letters (19 rouleaux) : 0125, 0175A, 0175B, 0191, 0257, 0268, 0358, 0483A, 0483B, 0490A, 0490B, 0800, 0813, 0826, 0846A, 0846B, 1203, 1218, 1545.
Liste Grand Prize (13 rouleaux) : 0125, 0191, 0211, 0257, 0268, 0358, 0800, 0813, 0826, 1203, 1218, 1447, 1545.

## 1. Objets hors First Letters qui ont un scan fin et un scan à ~9 µm

Ce sont les seuls où une carte du modèle 2 µm peut servir de pré-étiquette pour une surface à ~9 µm.

| Objet | Grand Prize ? | Scans | Segments (surface fine / ~9 µm / les deux) | Carte du modèle fin | Étiquettes de l'équipe sur S3 | Étiquettes déjà publiées à ~9 µm |
| --- | --- | --- | --- | --- | --- | --- |
| PHerc0009B | non | 2.401 µm (77 keV), 8.64 µm (116 keV) | 19 (18 / 18 / 18) | 18 seg. | 1 seg., 2.6 cm² supervisés | reader-v2-labels (D. Russo) : 14 seg., 236 cm² ; vérifié à la main : non (cartes du modèle 2 µm de l'équipe, seuillées)<br>Studio (P. Aranke) : 60 seg., 48 cm² ; vérifié à la main : oui (corrigé à la main, médiane 11 révisions par segment)<br>Expanded9 (P. Aranke) : 13 seg. ; vérifié à la main : reprise d'étiquettes existantes : reference_814_841_9B ×13 |
| PHerc0139 | non | 1.129 µm (59 keV), 2.399 µm (78 keV), 2.403 µm (77 keV), 9.362 µm (113 keV) | 39 (38 / 38 / 38) | 38 seg. | 8 seg., 11.2 cm² supervisés | ink_9um (équipe) : 9 seg. ; vérifié à la main : oui (annotation de l'équipe)<br>ink_9um (équipe) : 5 seg. ; vérifié à la main : oui (annotation de l'équipe)<br>reader-v2-labels (D. Russo) : 20 seg., 819 cm² ; vérifié à la main : non (cartes du modèle 2 µm de l'équipe, seuillées)<br>Expanded9 (P. Aranke) : 14 seg. ; vérifié à la main : reprise d'étiquettes existantes : official_ink9 ×14 |
| PHerc0332 | non | 2.399 µm (78 keV), 3.24 µm (53 keV), 3.24 µm (70 keV), 7.91 µm (53 keV) | 2 (0 / 0 / 0) | 0 seg. | aucune | aucune |
| PHerc0343P | non | 2.215 µm (111 keV), 8.64 µm (116 keV) | 8 (8 / 8 / 8) | 8 seg. | aucune | reader-v2-labels (D. Russo) : 6 seg., 22 cm² ; vérifié à la main : non (cartes du modèle 2 µm de l'équipe, seuillées) |
| PHerc0500P2 | non | 0.55 µm (65.35 keV), 2.215 µm (111 keV), 4.317 µm (111 keV), 9.362 µm (113 keV) | 46 (46 / 46 / 46) | 46 seg. | 1 seg., 2.2 cm² supervisés | reader-v2-labels (D. Russo) : 18 seg., 100 cm² ; vérifié à la main : non (cartes du modèle 2 µm de l'équipe, seuillées)<br>Expanded9 (P. Aranke) : 1 seg. ; vérifié à la main : reprise d'étiquettes existantes : official_ink_bucket ×1 |
| PHerc0814 | non | 1.129 µm (59 keV), 2.399 µm (78 keV), 9.362 µm (113 keV) | 19 (19 / 19 / 19) | 19 seg. | 1 seg., 0.5 cm² supervisés | ink_9um (équipe) : 1 seg. ; vérifié à la main : oui (annotation de l'équipe)<br>reader-v2-labels (D. Russo) : 8 seg., 249 cm² ; vérifié à la main : non (cartes du modèle 2 µm de l'équipe, seuillées)<br>Studio (P. Aranke) : 69 seg., 82 cm² ; vérifié à la main : oui (corrigé à la main, médiane 38 révisions par segment)<br>Expanded9 (P. Aranke) : 11 seg. ; vérifié à la main : reprise d'étiquettes existantes : reference_814_841_9B ×10, official_ink9 ×1 |
| PHerc0841 | non | 2.403 µm (77 keV), 9.366 µm (113 keV) | 3 (3 / 3 / 3) | 3 seg. | 3 seg., 3.4 cm² supervisés | Studio (P. Aranke) : 81 seg., 120 cm² ; vérifié à la main : oui (corrigé à la main, médiane 17 révisions par segment)<br>Expanded9 (P. Aranke) : 19 seg. ; vérifié à la main : reprise d'étiquettes existantes : reference_814_841_9B ×19 |
| PHerc1451 | non | 2.399 µm (78 keV), 8.64 µm (116 keV) | 0 (0 / 0 / 0) | 0 seg. | aucune | aucune |
| PHerc1667 | non | 1.129 µm (59 keV), 2.399 µm (78 keV), 3.24 µm (88 keV), 7.91 µm (53 keV) | 20 (19 / 0 / 0) | 19 seg. | 6 seg., 28.7 cm² supervisés | ink_9um (équipe) : 6 seg. ; vérifié à la main : oui (annotation de l'équipe)<br>Expanded9 (P. Aranke) : 7 seg. ; vérifié à la main : reprise d'étiquettes existantes : official_exposed_fragment ×1, official_ink9 ×6 |
| PHercParis4 | non | 1.129 µm (78 keV), 2.4 µm (78 keV), 2.4 µm (137 keV), 7.91 µm (54 keV), 45.532 µm (74 keV), 45.532 µm (110 keV) | 82 (80 / 0 / 0) | 80 seg. | 8 seg., 82.0 cm² supervisés | ink_9um (équipe) : 8 seg. ; vérifié à la main : oui (annotation de l'équipe)<br>Expanded9 (P. Aranke) : 29 seg. ; vérifié à la main : reprise d'étiquettes existantes : official_ink9 ×8, vesuvius-reproduction ×21 |

## 2. Autres objets

| Objet | First Letters ? | Grand Prize ? | Scans | Segments | Étiquettes publiées |
| --- | --- | --- | --- | --- | --- |
| PHerc0125 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0172 | non | non | 7.91 µm (53 keV) | 53 | reader-v2-labels (D. Russo) : 4 seg. ; Expanded9 (P. Aranke) : 13 seg. |
| PHerc0175A | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0175B | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0191 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0211 | non | oui | 9.362 µm (113 keV) | 1 | aucune |
| PHerc0257 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0268 | **oui** | oui | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0306B | non | non | 8.64 µm (116 keV) | 1 | aucune |
| PHerc0343 | non | non | 8.64 µm (116 keV) | 1 | aucune |
| PHerc0358 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0483A | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0483B | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0490A | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0490B | **oui** | non | 8.64 µm (116 keV) | 0 | aucune |
| PHerc0800 | **oui** | oui | 8.64 µm (116 keV) | 6 | aucune |
| PHerc0813 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0826 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHerc0846A | **oui** | non | 2.403 µm (77 keV), 9.362 µm (113 keV) | 0 | aucune |
| PHerc0846B | **oui** | non | 9.362 µm (113 keV) | 0 | aucune |
| PHerc1203 | **oui** | oui | 2.403 µm (77 keV), 9.362 µm (113 keV) | 0 | aucune |
| PHerc1218 | **oui** | oui | 8.64 µm (116 keV) | 0 | aucune |
| PHerc1299 | non | non | 2.399 µm (78 keV) | 0 | aucune |
| PHerc1447 | non | oui | 8.64 µm (116 keV) | 18 | ink-8um-pherc1447-surfaces (Y. Nader) : 2 seg. |
| PHerc1545 | **oui** | oui | 9.362 µm (113 keV) | 0 | aucune |
| PHercMAN5 | non | non | 2.399 µm (78 keV) | 1 | Expanded9 (P. Aranke) : 1 seg. |
| PHercMANB | non | non | 2.399 µm (78 keV) | 0 | aucune |
| PHercMANBp | non | non | 1.129 µm (59 keV), 2.399 µm (78 keV) | 11 | aucune |
| PHercParis3 | non | non | 2.4 µm (78 keV) | 0 | aucune |

## 3. Cartes d'encre publiées par l'équipe sur les surfaces à ~9 µm (nombre de segments par modèle)

| Objet | Modèles |
| --- | --- |
| PHerc0009B | argus-v3 ×18, ink9um-hybrid3d2d-s43-20k ×18, reader-v3 ×18 |
| PHerc0172 | timesformer_scroll5_july_retreat ×54, timesformer_scroll5_november19 ×54 |
| PHerc0211 | argus-v3 ×1, ink9um-hybrid3d2d-s43-20k ×1, reader-v3 ×1 |
| PHerc0306B | argus-v3 ×1, ink9um-hybrid3d2d-s43-20k ×1, reader-v3 ×1 |
| PHerc0343 | argus-v3 ×1, ink9um-hybrid3d2d-s43-20k ×1, reader-v3 ×1 |
| PHerc0343P | argus-v3 ×8, ink9um-hybrid3d2d-s43-20k ×8, reader-v3 ×8 |
| PHerc0800 | argus-v3 ×6, ink9um-hybrid3d2d-s43-20k ×6, reader-v3 ×6 |
| PHerc0814 | argus-v3 ×12, ink9um-hybrid3d2d-s43-20k ×12, reader-v3 ×12 |
| PHerc0841 | argus-v3 ×3, ink9um-hybrid3d2d-s43-20k ×3, reader-v3 ×3 |
| PHerc1447 | argus-v3 ×18, ink9um-hybrid3d2d-s43-20k ×18, reader-v3 ×18 |

## 4. Étiquettes de l'équipe republiées sur S3 (`ink-labels`), segment par segment

Surfaces en cm² au pas du scan annoté. « Encre » : pixels étiquetés encre. Chemin : `<segment>/ink-labels/<volume>/<jeu>/`.

| Objet | Segment | Jeu | Scan | Supervisé | Encre | Recalage |
| --- | --- | --- | --- | --- | --- | --- |
| PHerc0009B | 20250919125754-auto_grown_20250919055754487_inp_hr | 20260918 | 2.401 µm | 2.55 cm² | 0.57 cm² | transferred |
| PHerc0139 | 20250108000005-w030_2025010818 | 20260918 | 2.399 µm | 0.70 cm² | 0.22 cm² | transferred |
| PHerc0139 | 20250831000000-w040_2025083102 | 20260918 | 2.399 µm | 1.42 cm² | 0.65 cm² | transferred |
| PHerc0139 | 20250831000000-w040_2025083102 | 20260918 | 9.362 µm | 1.43 cm² | 0.65 cm² | native |
| PHerc0139 | 20260108000000-w041_2026010816 | 20260918 | 2.399 µm | 0.48 cm² | 0.20 cm² | transferred |
| PHerc0139 | 20260108000000-w041_2026010816 | 20260918 | 9.362 µm | 0.49 cm² | 0.20 cm² | native |
| PHerc0139 | 20260112000000-w043_2026011217 | 20260918 | 2.399 µm | 0.40 cm² | 0.18 cm² | transferred |
| PHerc0139 | 20260115000000-w044_2026011522 | 20260918 | 2.399 µm | 1.82 cm² | 0.47 cm² | transferred |
| PHerc0139 | 20260115000000-w044_2026011522 | 20260918 | 9.362 µm | 1.04 cm² | 0.40 cm² | native |
| PHerc0139 | 20260126000000-w045_2026012619 | 20260918 | 2.399 µm | 0.50 cm² | 0.13 cm² | transferred |
| PHerc0139 | 20260302000000-w039_2026030210 | 20260918 | 2.399 µm | 0.50 cm² | 0.16 cm² | transferred |
| PHerc0139 | 20260302000000-w039_2026030210 | 20260918 | 9.362 µm | 0.51 cm² | 0.16 cm² | native |
| PHerc0139 | 20260317000000-w035_2026031718 | 20260918 | 2.399 µm | 0.93 cm² | 0.35 cm² | transferred |
| PHerc0139 | 20260317000000-w035_2026031718 | 20260918 | 9.362 µm | 0.94 cm² | 0.35 cm² | native |
| PHerc0500P2 | 20250825181859--1 | 20260918 | 2.215 µm | 2.22 cm² | 0.47 cm² | transferred |
| PHerc0814 | 20260226000000-46527_2um_try2 | 20260918 | 2.399 µm | 0.54 cm² | 0.17 cm² | transferred |
| PHerc0841 | 20260220213127-w00 | 20260918 | 2.403 µm | 1.41 cm² | 0.36 cm² | transferred |
| PHerc0841 | 20260220214732-auto_grown_20260220144552896 | 20260918 | 2.403 µm | 0.86 cm² | 0.28 cm² | transferred |
| PHerc0841 | 20260221022814-auto_grown_20260220174252405 | 20260918 | 2.403 µm | 1.12 cm² | 0.26 cm² | transferred |
| PHerc1667 | 20240304141531-w013_20240304141531_flatboi | 20260918 | 2.399 µm | 3.08 cm² | 0.92 cm² | transferred |
| PHerc1667 | 20240304144031-w018_20240304144031_flatboi | 20260918 | 2.399 µm | 14.55 cm² | 3.27 cm² | transferred |
| PHerc1667 | 20240304161941-w023_20240304161941_flatboi | 20260918 | 2.399 µm | 5.50 cm² | 1.30 cm² | transferred |
| PHerc1667 | 20251208130119-w028_20251208130119156_flatboi | 20260918 | 2.399 µm | 1.15 cm² | 0.31 cm² | transferred |
| PHerc1667 | 20251212185248-w029_20251212185248662_flatboi | 20260918 | 2.399 µm | 1.46 cm² | 0.40 cm² | transferred |
| PHerc1667 | 20251223230000-w031_2025122323_flatboi | 20260918 | 2.399 µm | 2.96 cm² | 0.79 cm² | transferred |
| PHercParis4 | 20230702185753 | 20260918 | 2.4 µm | 7.60 cm² | 1.97 cm² | transferred |
| PHercParis4 | 20230929220926 | 20260918 | 2.4 µm | 4.82 cm² | 1.36 cm² | transferred |
| PHercParis4 | 20231007101619 | 20260918 | 2.4 µm | 14.71 cm² | 4.67 cm² | transferred |
| PHercParis4 | 20231012184424 | 20260918 | 2.4 µm | 29.40 cm² | 6.12 cm² | transferred |
| PHercParis4 | 20231016151002 | 20260918 | 2.4 µm | 5.33 cm² | 1.22 cm² | transferred |
| PHercParis4 | 20231031143852 | 20260918 | 2.4 µm | 4.27 cm² | 1.00 cm² | transferred |
| PHercParis4 | 20231106155351 | 20260918 | 2.4 µm | 5.67 cm² | 1.95 cm² | transferred |
| PHercParis4 | 20231210121321 | 20260918 | 2.4 µm | 10.18 cm² | 3.23 cm² | transferred |
