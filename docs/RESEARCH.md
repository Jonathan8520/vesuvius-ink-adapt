# État de l'art

Une entrée par source : lien, ce que ça apporte, décision (réutiliser, s'en inspirer, écarter).
Dernière mise à jour : 22 novembre 2026 (soir). Ce fichier fusionne `docs/VEILLE-2026-11-22.md` (veille de
Jonathan sur Discord et GitHub), nos lectures du dépôt villa et du site, et la lecture de 25 dépôts
communautaires clonés. Origine de chaque fait : **[V]** veille de Jonathan, **[N]** vérifié par nous sur le code
ou les données, **[L]** lu dans un dépôt cloné ou une page publique (rapport de lecture, à revérifier avant de
citer en public).

## En bref

1. **L'ancien plan (E3 à E6) est entièrement couvert par d'autres.** TENT dégrade (khj1222), le choix de
   profondeur sans étiquette ne bat pas la fenêtre fixe (trois auteurs), les ensembles sont publiés au moins
   trois fois, l'auto-apprentissage entre rouleaux est une PR de novembre (villa #2512), et au moins sept dépôts
   font tourner `ink_9um` sans C++ ou sur CPU.
2. **La référence à 9 µm n'est plus `ink_9um` mais reader-v3** (Domenico Russo, MIT, même réseau, tuiles de 384),
   « now used in the majority of First Letters submissions ».
3. **Les mesures sont limitées par les données de validation, pas par les idées.** Les trois masques publiés
   font 0,66 cm², collés aux pixels d'entraînement (88 à 99 % à moins de deux patchs pour deux d'entre eux), avec
   un bruit entre graines de 0,02 à 0,13. Plusieurs « gains » publiés sont du niveau du bruit.
4. **Trouvaille du jour [N] : les 9 cas réservés ont chacun une zone de validation exclue de l'entraînement, mais
   le dépôt 9 µm n'en publie que 3.** Les 6 autres zones sont publiques sur S3 (étiquettes 2,4 µm du 18/09) et
   n'ont aucun pixel commun avec les masques d'entraînement publiés. Elles pèsent 3,5 cm² (5,3 fois plus) et sont
   loin des pixels d'entraînement. Détail en section 3. À confirmer par un test de mémorisation.
5. **Le jury** : gros montants pour des modèles adoptés et pour le déroulage ; 250 à 1 000 $ pour des correctifs
   fusionnés, des défauts de données et des mesures utiles ; « We discourage standalone analytic, auditing or
   evaluation tools ». Le mainteneur bruniss refuse les contrôles automatiques de « formes d'encre ».
6. **Règle du Discord [V]** : pas de message généré par IA à la place de sa propre participation, sauf dans
   #robots avec une ligne « AI disclosure ».

## 1. Ce que l'équipe a fait sur la généralisation entre rouleaux

| Source | Ce que ça apporte | Décision |
| --- | --- | --- |
| Page Open Problems, https://scrollprize.org/2026_open_problems [N] | L'essaim d'agents (inspiré de karpathy/autoresearch) a cherché une **recette d'entraînement** : entraîné sur PHerc. 139, validé sur PHerc. 1667, Dice sur pseudo-étiquettes presque doublé. Blocage « Cross-scroll generalization » : ce qui aiderait, « Multi-scroll training, better labels, stronger diagnostics ». | Ne pas refaire une recherche d'architecture. Retenir « better labels » et « stronger diagnostics ». |
| Billet « We are cooking » (19/03/2026), https://scrollprize.substack.com/p/we-are-cooking [L] | « Youssef set up a swarm of automated agents that perform research on ink detection model architectures and training. » Code de l'essaim non publié. Modèle issu : `new_canon_autoresearch_recipe`, publié comme https://huggingface.co/scrollprize/ink_canonical_2um (ResNet-152 3D, tuiles 256, 2,4 µm). | Rien à réutiliser directement. |
| Recette `ink_9um`, https://huggingface.co/scrollprize/ink_9um et `vesuvius/src/vesuvius/ink_detection/` [N] | Le bloc `datasets` du checkpoint liste les 29 représentations, cas réservés compris. Un patch est d'entraînement s'il touche la supervision hors validation. `val_balanced_accuracy` : précision équilibrée à 0,5 sur les patchs des masques de validation, fenêtre centrée. | Métrique de l'équipe conservée. |
| `data/heldout.py` et PR villa #2126 (fusionnée le 01/11) [N][L] | L'équipe reconnaît que la validation en ligne mesure « interpolation inside a segment the model was trained on » : « 233 of 282 validation crops share voxels with a training crop ». Option `"split": "validation"` pour tenir un rouleau entier à l'écart. | Toute mesure doit dire si la zone est isolée ou non. |
| Avis d'un administrateur (sean, #general, 30/10) [V] | Plus à gagner avec des étiquettes qu'avec des agents d'autorecherche sur des données bruitées et clairsemées. | Favoriser une contribution de données. |
| Tickets « help wanted » de villa [V][L] | Les 17 sont fermés (dont #192 « Accurate 3d ink labels » et #193 « Methods for generating surface, fiber, or ink labels », fermés le 01/11). La liste de souhaits est la page Open Problems. | Chercher les besoins dans les tickets ouverts sans libellé. |

## 2. Déjà fait par la communauté, étape par étape de l'ancien plan

### Score de référence (ancien E3)

| Source | Résultat | Décision |
| --- | --- | --- |
| https://github.com/DomRusso2/ink9um-dense (KLAVIS, prix d'août) [L] | Précision équilibrée à 0,5 et AUC des 14 checkpoints sur les 3 masques. s43-20k : 0,763 / 0,761 / 0,821 (w016, 0814, 1667-w029) ; meilleurs : s43-60k et s42-10k. | Référence publiée, à citer. |
| https://github.com/khj1222/vesuvius-challenge docs/14, 15, 17 [L][V] | F1 au seuil optimal : 0,74 à 0,77 dans les 3 masques contre 0,93 à 0,99 sur les pixels d'entraînement (75k). Rouleau jamais vu (réentraînement en laissant un rouleau de côté) : 0,49 à 0,68. Fuite : 58,6 %, 45,0 %, 23,2 % des pixels réservés à moins d'un patch d'un pixel d'entraînement. | Méthode d'audit reprise pour la section 3. |
| https://github.com/DarthCeltic/argus [L] | Contrôle sur un recadrage de w016 : AUC 0,772, AP 0,579. Mise en garde : la seule distance au bord du masque donne AUC 0,689. | Penser aux témoins géométriques. |
| https://github.com/Bullo27/first-letters-survey [L] | `ink_9um` sur PHerc0841 en rendu natif : AUC 0,72 à 0,81, « only as blobs ». 65 patchs sur 21 rouleaux éligibles, rien de lisible. | Couvre notre ancien E7. |
| https://github.com/EhimenNathan/vesuvius-ink-generalization, https://github.com/ArcheyChen/vesuvius-eligible-scouting [L] | AUC d'`ink_9um` sur sources jamais vues : 0841 0,70 à 0,83, 0009B 0,87, 0500P2 0,83 à 0,85, MAN5 0,55 à 0,62, PHerc1447 0,67 à 0,68. | Jeux hors entraînement déjà exploités. |

### Profondeur (ancien E4)

| Source | Résultat | Décision |
| --- | --- | --- |
| https://github.com/tarikcankorkmaz00/ink9um-depth-calibration (14/09) [V] | La meilleure profondeur varie à l'échelle du patch. Aucune règle par rouleau, segment ou bloc ne bat la fenêtre fixe en validation croisée. | Abandonné. |
| https://github.com/LynnHenry/offset-sweep (07/11) [V] | L'accord entre trois modèles retrouve un maillage décalé de 8 voxels, mais fait perdre 0,04 à 0,16 d'AUC sur un maillage publié. Oracle : moins de 0,01 de gain. | Abandonné. |
| Ticket villa #1867, khj1222 docs/30 et 31 [L] | Décaler la fenêtre de 4 plans change l'AUC d'au plus 0,023. À −5 couches : −0,14 à −0,17 de F1 ; à +5 : −0,03. Gain d'un oracle par segment : environ +0,01. | Le plafond est trop bas. |
| https://github.com/pscamillo/ink9-depth-window (prix d'août) [L] | 13 et 9 couches valent 17. « It was never the depth. It was the jitter. » Bruit entre graines : 0,130 (w016), 0,021 (0814), 0,072 (w029). | Chiffre de bruit à retenir. |
| Moyenne de fenêtres : fiche du modèle, inkbench (+0,006), Nieuwlaar (0,840 → 0,855), PR villa #1946 (rien au-dessus du bruit), reader-v2 (0,824 → 0,834) [L] | Gain faible ou nul. | Abandonné. |
| Outils de balayage : PR villa #1872 (fermée), #2551 (ouverte), `ink-sdk battery` [L] | Balayage sans choix automatique. | Couvert. |
| Sens de profondeur sans étiquette : villa #1867 (57 sur 70), `ink-sdk orient` (36 sur 36 par géométrie), khj1222 docs/25 [L] | Couvert. | Abandonné. |
| Recentrage par luminosité (Bullo27) [L] | Négatif : « The ink sits on the sheet's surface, not at its brightness peak ». | Abandonné. |

### Adaptation au moment du test et ensembles (ancien E5)

| Source | Résultat | Décision |
| --- | --- | --- |
| khj1222 docs/18 (30/08) [V][L] | TENT sur les 27 712 paramètres affines des InstanceNorm : −0,041 de F1, 14 cas sur 14 dégradés, AUC 0,66 → 0,48, l'entropie baisse quand même. AdaBN inapplicable. Pseudo-étiquettes : +0,030, niveau du bruit. Non testé : entropie avec terme de diversité. | Abandonné. La littérature va dans le même sens (voir section 6). |
| https://github.com/TAUIL-Abd-Elilah/ink-adapt-9um (08/11) [V] | Élève entraîné sur le consensus de quatre modèles, sans étiquette de la cible : 0,765 contre 0,769 pour la moyenne des enseignants. Nom presque identique au nôtre. | Abandonné. |
| PR villa #2512 (DeepakEz, 12/11, ouverte) [L] | Transfert de type de scan et auto-apprentissage, PHerc 0139 tenu à l'écart : +0,035 d'AUC. Candidat de novembre. | Créneau pris. |
| https://github.com/alexxxmur/ink9um-native116-bench (13/10) [V] | Pseudo-étiquettes sur scans natifs : aucun gain sur un autre rouleau. | Abandonné. |
| Ensembles : https://github.com/Alex55288/inkbench, https://github.com/gowtham012/vesuvius-ink-ensemble (soumis le 21/11), max14vega, option `--ensemble-checkpoint` de villa [V][L] | Moyenne des 14 : AP 0,764 → 0,829 (inkbench), AUC 0,839 → 0,923 (gowtham012) sur les 3 masques. Loin des pixels d'entraînement (1667, plus de 384 px), le gain tombe à +0,026 (inkbench). | Abandonné, mais le gain réel hors fuite reste mal connu. |

### Chaîne sans C++ et matériel gratuit (ancien E6)

- [V] litao-kupia/ink-cpu, jamiejmann/vesuvius-cpu-reader, LimeGS/ink-sdk (20 profils de modèles), praveenperera/inkrs
  (Rust), ismoilovdevml/vesuvius-pipeline (rendu en flux, CPU seul), adrielakak/herculaneum-ink-mps.
- [L] AndreasHad04/villa-apple-silicon : `firstletters/render_tifxyz.py`, rendu Python en flux, r = 0,9999969 avec
  l'outil officiel. PR villa #2521 : inférence 25 % plus rapide.
- Décision : notre chaîne reste un outil interne. Elle n'est plus un livrable.

### Rouleaux non lus (ancien E7)

- [V] Ahggggg/spiral-tracks-four-scrolls, fil Discord « 57 bands on 19 unread scrolls », pscamillo/vesuvius-eligible-meshes,
  mydd7/scrollprize-progress-november-2026 ; [L] Bullo27 (971 cm² criblés).
- Question ouverte sur Discord [V] : les étiquettes manuelles publiques peuvent-elles servir à entraîner un modèle
  pour First Letters ?

## 3. Données de validation publiques

### Les 9 cas réservés d'`ink_9um` : 3 masques publiés, 6 zones oubliées [N]

Mesuré le 22/11 sur les masques seuls (aucun modèle). Repère : étiquettes 9,6 µm. « Proche » : part des pixels de
la zone à moins de 128 px puis 256 px d'un pixel de supervision d'entraînement (méthode de khj1222, docs/17).

| Cas | Masque publié à 9 µm ? | Zone réservée | Recouvrement avec la supervision d'entraînement | Îlots | Proche (128 / 256 px) |
| --- | --- | --- | --- | --- | --- |
| pherc0139-w016 | oui | 178 146 px (0,16 cm²) | 0 | 2 | 59 % / 99 % |
| pherc0814-46527 | oui | 161 051 px (0,15 cm²) | 0 | 1 | 45 % / 88 % |
| pherc1667-w029 | oui | 382 353 px (0,35 cm²) | 0 | 2 | 23 % / 45 % |
| pherc0139-w028 | non (S3) | 226 520 px (0,21 cm²) | 0 | 5 | 0 % / 9 % |
| pherc0139-w029 | non (S3) | 71 807 px (0,07 cm²) | 0 | 5 | 0 % / 0 % |
| pherc1667-w018 | non (S3) | 1 934 776 px (1,78 cm²) | 0 | 6 | 0,2 % / 3,5 % |
| pherc1667-w023 | non (S3) | 589 349 px (0,54 cm²) | 0 | 1 | 0 % / 0 % |
| pherc1667-w028 | non (S3) | 401 932 px (0,37 cm²) | 0 | 11 | 0 % / 0 % |
| pherc1667-w031 | non (S3) | 594 493 px (0,55 cm²) | 0 | 45 | 0 % / 0 % |

- Total publié : 721 550 px (0,66 cm²). Total non publié à 9 µm : 3 818 877 px (3,52 cm²), soit 5,3 fois plus.
- Source des 6 zones : `<segment>/ink-labels/<volume 2,4 µm>/20260918/validation.zarr` sur S3 (Zarr v3, niveau 2,
  même repère que les étiquettes 9,6 µm). Pour les 2 cas publiés qui ont aussi ce fichier, l'IoU avec le masque
  HF est de 0,995.
- Pour les 8 cas présents sur S3 : surface de supervision HF = supervision S3 moins validation S3. Le dépôt 9 µm
  a donc été construit en retirant la zone réservée des 9 cas, et n'a republié le masque que pour les 3 cas
  « online ».
- Les étiquettes d'encre HF couvrent déjà ces zones (part d'encre 21 à 29 %, IoU 0,97 à 0,99 avec S3). Il ne
  manque que le fichier de masque.
- Jumeau natif : le cas pherc0139-w028 est le segment physique w044, présent à l'entraînement en version native.
  Sa supervision native ne touche pas la zone réservée (recouvrement nul, distance médiane 522 px).
- Aucune des sources lues ne mentionne ces 6 zones : toutes écrivent que seuls 3 masques sont tenus à l'écart.
- Reste à faire : test de mémorisation (un checkpoint tardif doit y avoir le score d'une zone jamais vue, pas
  celui d'un pixel d'entraînement), et recherche d'antériorité.

### Jeux étiquetés hors entraînement d'`ink_9um`

| Jeu | Où | Remarques |
| --- | --- | --- |
| PHerc0841 : w00 et deux `auto_grown` | S3 `PHerc0841/segments/*/ink-labels/2.403um-volume-20260319124803/20260918/` | Segments entièrement en validation chez l'équipe. 3,4 cm² supervisés. Surface native 28 couches et prédictions de 4 modèles publiées dans `ink-detection/`. Recalage natif à vérifier (6 à 8 px) [L]. |
| PHerc0009B : 1 segment | S3 `PHerc0009B/segments/20250919125754-…/ink-labels/2.401um-volume-20250820154339/20260918/` | 2,6 cm² supervisés. Natif à 8,64 µm (31 couches). |
| PHerc0500P2 (fragment) | S3 `PHerc0500P2/segments/20250825181859--1/ink-labels/2.215um-volume-20250526151718/20260918/` [L] | 118 couches à 2,215 µm. |
| PHerc1447 : w058, w060 | HF `YoussefMoNader/ink-8um-pherc1447-surfaces` [V][L] | Étiquettes communautaires, CC BY-NC 4.0. |
| PHerc0343 | boîtes de lettres d'Erwin Nieuwlaar [V] | |
| MAN5 | HF `ink/man5/MAN5_outer_3/` [L] | Tous les modèles entre 0,50 et 0,62 d'AUC. |
| ScrollGT | https://github.com/jonmarrs/scrollgt [V] | Vérité terrain recalée ; scores d'avant le 07/08 faux. |

Aucun de ces rouleaux n'est sur la liste First Letters (`prizeEligibility.json`, 19 rouleaux), sauf mention
contraire à vérifier pour PHerc0343 (prix déjà attribué).

### Défauts de données connus

- Ticket villa #2107 (ouvert, sans réponse de l'équipe) [L] : dans le bucket HF, dossier `ink/`, 18 volumes sur 33
  ont des niveaux réduits tronqués (niveau 2 : les 17 premières couches sur 65, au lieu d'une réduction en
  profondeur). `ink_9um` y tombe à 0,54 d'AUC sur 1667 contre 0,91 à 0,93 avec une entrée reconstruite. Les
  surface-volumes S3 sont sains (109 couches à tous les niveaux) [N][L].
- Ticket villa #1481 (ouvert) [L] : l'inférence compte les zéros de remplissage dans la normalisation robuste.
- Ticket villa #1845 [L] : un maillage grossier coûte 0,04 d'AUC.
- Ticket villa #2627 (20/11) [L] : inverser la profondeur d'`ink_canonical_2um` décorrèle les sorties.

## 4. Modèles d'encre à 9 µm

| Modèle | Entrée | Données | Résultat publié | Licence |
| --- | --- | --- | --- | --- |
| `scrollprize/ink_9um` | 17 × 128 × 128 | 24 segments 2,4 µm réduits + 5 natifs, 4 rouleaux, étiquettes manuelles | 0841 natif : AUC 0,68 à 0,78 | MIT |
| reader-v2, https://github.com/DomRusso2/reader-v2 | 17 × 128 × 128, même réseau | corpus `ink_9um` + 70 segments natifs, distillation des cartes 2,4 µm de l'équipe ; 0841 exclu | 0841 : AUC 0,824 | MIT |
| reader-v3, https://github.com/DomRusso2/reader-v3 | 17 × 384 × 384 | reader-v2 poursuivi à 256 puis 384 px | 0841 : 0,848 ; 1447 : 0,807 | MIT |
| rectina, https://huggingface.co/evilaliv3/rectina | 17 × 384 × 384 | 87 segments, 8 rouleaux | 0,861 contre 0,856 pour reader-v3 sur 14 unités | poids CC BY-NC |
| hecate (équipe), https://huggingface.co/scrollprize/hecate | 16 × 64 × 64 à 9,6 µm | distillé du modèle 2,4 µm | 0841 : 0,857 | MIT |

Les modèles distillés (reader, hecate) ont vu des cartes d'encre couvrant des segments entiers : les zones
réservées d'`ink_9um` ne sont probablement pas tenues à l'écart pour eux. À vérifier avant toute comparaison.

## 5. Ce que les mainteneurs acceptent et refusent [L]

- Refusé par bruniss : PR #2318 et #2349 (contrôles automatiques de formes d'encre : « consistently fail to do
  anything useful », « we will not be merging any tools of this sort »), #2012 (« we dont recommend binarizing
  ink predictions »), #1946 (moyennes sans gain au-dessus du bruit), #2385 (`--tta-shift`, retirée).
- Fusionné : #2004 (`--ensemble-checkpoint`), #2126 (validation sur jeux entiers), #2521 (vitesse, résultat
  identique à l'octet), correctifs de plateforme et de bugs réels.
- Retour d'expérience de khj1222 (notes publiées dans son dépôt) : en octobre, ses notes de mesure n'ont rien
  reçu, seul un correctif fusionné a été primé ; ce qui dépasse 2 500 $ est du logiciel que d'autres font tourner
  tous les jours.

## 6. Littérature

- Préprint arXiv:2606.29085 (27/06/2026) : lecture complète de PHerc. 1667, modèle ResNet3D-50 à 2,4 µm,
  pseudo-étiquetage itératif. Aucun modèle à 9 µm, aucune métrique entre rouleaux.
- Adaptation au moment du test : TENT (2006.10726), EATA (2204.02610), SAR (2302.12400), MEMO (2110.09506),
  CoTTA (2203.13591), RDumb (2306.05401). En segmentation binaire déséquilibrée, l'entropie s'effondre :
  BAPA (2609.21743), MedSeg-TTA (2512.02497, 13 méthodes sur 20 dégradent), MuVi (MICCAI 2025, MEMO sans effet sur
  nnU-Net à InstanceNorm). Cohérent avec le résultat de khj1222.
- Choix sans étiquette : la confiance mesure l'assurance, pas la justesse (2108.10860) ; l'accord entre vues ou
  entre modèles est le critère le moins mauvais (2503.00450, 2206.13089).
- Kaggle Ink Detection 2023 : pooling en profondeur et décalage aléatoire de ±2 couches, déjà dans `ink_9um`.

## 7. Leçons techniques pour notre chaîne

- **Grille des tuiles [N]** : l'outil officiel pose ses tuiles sur la grille globale de la surface. En l'imitant
  (`core.infer_roi`), la corrélation avec la prédiction officielle passe de 0,912 à 0,9999. tarikcankorkmaz00 a
  mesuré qu'une origine hors grille de 8 px coûte 0,005 à 0,032 d'AUC [V].
- **Rendu [L], à vérifier** : `vc_render_tifxyz` centre ses couches sur (N − 1) / 2 (pour 28 couches : −13,5 à
  +13,5, pas −14 à +13), prend le centre du pixel ((c + 0,5) · scale) et interpole la surface en bicubique sur
  main. C'est l'explication probable de notre parité de 0,93 quand d'autres obtiennent 0,9999.
- **Étiquettes HF** : les dossiers natifs ont un fichier `.zattrs` par niveau, à ne pas confondre avec un chunk.
- **Mémoire** : les transformées de distance sur un segment entier de 1667 (260 Mpx) dépassent la mémoire
  partagée ; travailler par îlot.

## 8. Besoin non couvert : candidats et décision

Voir `docs/PLAN.md` (section « Décision du 23 novembre »).
