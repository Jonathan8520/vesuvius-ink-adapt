# État de l'art

Une entrée par source : lien, ce que ça apporte, décision (réutiliser, s'en inspirer, écarter).
Dernière mise à jour : 22 novembre 2026 (nuit). Pour le cap « étiquettes vérifiées à la main », aller
directement à la section 9. Ce fichier fusionne `docs/VEILLE-2026-11-22.md` (veille de
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
4. **Constat du jour [N] : les 9 cas réservés ont chacun une zone de validation exclue de l'entraînement, mais
   le dossier 9 µm n'en publie que 3.** Les 6 autres masques sont publics dans le repère 2,4 µm (dossier `ink/`
   du bucket Hugging Face depuis le 07/07, S3 depuis le 18/09, recensés par nestorvfx le 24/09) et
   n'ont aucun pixel commun avec les masques d'entraînement publiés. Elles pèsent 3,5 cm² (5,3 fois plus) et sont
   loin des pixels d'entraînement. Le test de mémorisation le confirme sur les 6 zones. Détail en section 3.
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

### Les 9 cas réservés d'`ink_9um` : 3 masques dans le dossier 9 µm, 6 absents [N]

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
- Antériorité (correction du 22/11, 21 h 40 UTC) : ces masques sont aussi dans le dossier `ink/` du bucket
  Hugging Face `scrollprize/datasets` depuis le 07/07/2026 (`ink/<objet>/<segment>/<segment>_validation_mask_v2.tif`,
  15 segments dont les 9 cas, vérifié par listing). L'audit de nestorvfx du 24/09
  (https://huggingface.co/datasets/nestorvfx/vesuvius-ink-training, `records/validation_audit.json`) fait la
  correspondance entre ces 15 fichiers et les `validation.zarr` de S3, avec les décalages de canevas (environ 20 px
  pour PHerc1667 ; 0139/w028 republié « without provenance », IoU 0,9884 au décalage [-460, -83]). Il ne dit pas
  que 6 masques manquent dans `ink_9um/labels`. Ce n'est donc pas une découverte de données : c'est un trou dans
  le dossier 9 µm, plus nos mesures (recouvrement, distance, mémorisation).
- Contamination par pseudo-étiquettes : `domenicor046/ink9um-dense-labels` (7 segments, 288,7 M px) définit
  `supervision_mask = render-valid AND NOT validation_mask` et ne retire que les 3 masques publiés. Ses jeux pour
  pherc0139-w028 (canevas couvert à 88,8 %), pherc0139-w029 (88,2 %) et pherc1667-w028 (81,8 %) couvrent donc
  très probablement leurs zones réservées. Les modèles qui en descendent (reader-v2, reader-v3, argus-v3) ne sont
  pas propres sur ces 3 zones. Restent propres pour tous : 1667-w018, w023, w031 (2,87 cm²). Déduit de la fiche.
- Pour les 8 cas présents sur S3 : surface de supervision HF = supervision S3 moins validation S3. Le dépôt 9 µm
  a donc été construit en retirant la zone réservée des 9 cas, et n'a republié le masque que pour les 3 cas
  « online ».
- Les étiquettes d'encre HF couvrent déjà ces zones (part d'encre 21 à 29 %, IoU 0,97 à 0,99 avec S3). Il ne
  manque que le fichier de masque.
- Jumeau natif : le cas pherc0139-w028 est le segment physique w044, présent à l'entraînement en version native.
  Sa supervision native ne touche pas la zone réservée (recouvrement nul, distance médiane 522 px).
- Aucune des sources lues ne mentionne ces 6 zones : toutes écrivent que seuls 3 masques sont tenus à l'écart.
- Test de mémorisation (s43-75k) fait sur les 9 cas : F1 de 0,44 à 0,74 dans les 6 zones non publiées, de 0,71 à
  0,76 dans les 3 zones publiées, de 0,91 à 0,99 sur les pixels d'entraînement des mêmes segments. AUC moyenne
  pondérée par pixel : 0,83 (non publiées) contre 0,92 (publiées). Tableau : `docs/HANDOFF.md`.

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

## 8. Besoin non couvert : décision

Le balayage lancé le 22/11 a été interrompu par l'arrêt du sprint. Le nouveau cap (étiquettes vérifiées à la
main) est décrit dans `docs/PLAN.md` ; l'état de l'art qui le concerne est en section 9.

## 9. Étiquettes d'encre à ~9 µm : qui publie quoi (cap du 22 novembre)

Chiffres par objet : `docs/INVENTAIRE.md` (`scripts/inventory.py`).

### La méthode de Priyank Aranke (First Letters PHerc. 211) [N]

- Billet du 15/11/2026 : https://scrollprize.substack.com/p/first-letters-emerge-from-pherc-211
- Ce qu'il écrit : « the training data mattered much more » que l'architecture. Il a comparé les rouleaux par un
  DINO 3D auto-supervisé : « PHerc0009B and PHerc0841 ranked in the top three ink-bearing scrolls for all 23 unread
  scrolls, and PHerc0814 usually came fourth or fifth (while the already-deciphered scrolls were almost always among
  the least similar) ». Puis : « I then ran the team's published 2 µm ink model on the high-resolution scans of the
  same papyrus, and transferred its predictions, together with the team's released 2 µm labels, onto the ~9 µm
  segments, where they seeded sparse ink/background labels that I checked and corrected by hand. Distilling the
  high-resolution ink onto these low-resolution segments was likely the single biggest driver in improving the
  quality of ink detection. »
- Concurrence : « In total we received 37 submissions on PHerc. 211 from 15 individual contestants and teams. »
- Publié : code MIT https://github.com/priyankaranke/vesuvius-studio-multiscroll-cpt ; modèle et données sous
  CC BY-NC 4.0 ; fork de VC3D (GPL-3.0) https://github.com/priyankaranke/vc3d-manual. Son outil d'étiquetage
  (« Donor Studio ») et le dépôt d'entraînement d'Expanded9 ne sont pas publics.
- Moyens : entraînement sur une GH200 (96 Go de mémoire GPU), toutes les tuiles gardées sur le GPU.
- Décision : ne pas refaire ses trois objets. Reprendre sa méthode là où elle n'a pas été appliquée, et publier
  l'outil qui lui manque.

### Jeux d'étiquettes publiés

| Jeu | Contenu | Vérifié à la main ? | Format et licence | Décision |
| --- | --- | --- | --- | --- |
| https://huggingface.co/datasets/paranke/vesuvius-814-841-9b-studio-training-data [N] | PHerc0814 (69 segments, 82 cm²), PHerc0841 (81, 120 cm²), PHerc0009B (60, 48 cm²) : 98,6 millions de pixels d'encre et 196 millions de fond, sur les surfaces de l'auteur (spirales et croissance de surface) | oui : pré-étiquettes du modèle 2 µm et de ses propres modèles, corrigées à la main (médiane de 21 révisions par segment) | tuiles `npy` 512 × 512 × 16, étiquette 0 inconnu / 1 fond / 2 encre ; CC BY-NC 4.0 | ne pas refaire ; à utiliser comme données d'entraînement de comparaison |
| https://huggingface.co/datasets/paranke/vesuvius-expanded9-training-data [N] | 113 représentations de 12 groupes de rouleaux : reprise des étiquettes `ink_9um` de l'équipe, des fragments exposés, de la reproduction du Grand Prize, et de ses jeux 0814, 0841, 0009B | « not an independently certified ground-truth collection » | tuiles Blosc ; CC BY-NC 4.0 | pas d'étiquette nouvelle pour les autres rouleaux |
| https://huggingface.co/datasets/domenicor046/reader-v2-labels [N] | 70 segments natifs de 6 objets : PHerc0139 (20), 0814 (8), 0500P2 (18), 0009B (14), 0343P (6), 0172 (4) | non : « the teacher maps are model outputs, not human annotations » ; encre si carte ≥ 128, fond si ≤ 64, bande intermédiaire hors supervision | format des dossiers `ink_9um` (Zarr v2, plan médian) ; MIT | point de départ de nos pré-étiquettes ; notre apport est la vérification humaine |
| Étiquettes de l'équipe sur S3, jeu `20260918` [N] | 33 entrées : PHercParis4 (8 segments, 82 cm²), 1667 (6, 28,7 cm²), 0139 (8 à 2,4 µm et 5 natifs), 0841 (3), 0009B (1), 0500P2 (1), 0814 (1) | oui (annotation de l'équipe, affinée par pseudo-étiquetage) | Zarr v3 2D, 6 niveaux, `inklabels`, `supervision`, `validation` | référence et zones de mesure |
| `ink_9um` de l'équipe (Hugging Face) [N] | 24 segments 2,4 µm réduits et 5 natifs (0139) | oui | Zarr v2, 21 ou 28 couches | format cible de notre export |
| https://huggingface.co/datasets/YoussefMoNader/ink-8um-pherc1447-surfaces [L] | PHerc1447 : w058, w060 | oui (auteur) | couches TIFF et PNG ; CC BY-NC 4.0 | hors de notre périmètre (rouleau du Grand Prize) |

### Ce qui manque [N]

Corrigé le 22/11 dans la nuit, après quatre balayages (section 10) :

- Aucune étiquette vérifiée à la main **au format d'entraînement de l'équipe, sur ses surfaces natives ~9 µm
  publiques**, pour un rouleau autre que PHerc0139 (5 segments).
- Sur **PHerc0500P2**, les couches `0`, `1`, `2`, `3`, `4` n'ont aucune étiquette humaine. `--1` a celles de
  l'équipe (scan fin), `--2` et `front` celles de jeff-j-chen (PNG, clairsemées). Sur **PHerc0343P**, le seul
  segment lisible (`20250511003658`) a déjà une étiquette de l'équipe (encre seule, `ink/unused/P343p`) et des
  tracés de jeff-j-chen.
- Aucun outil d'étiquetage d'encre utilisable au stylet sur tablette. Trois tentatives côté bureau ou navigateur
  n'ont pas été fusionnées dans villa (PR #2219, #1714 fermées ; #2532 en brouillon).
- Aucune comparaison d'entraînements « étiquettes corrigées à la main contre étiquettes du modèle seules, sur les
  mêmes pixels ». Aucun temps de correction par cm².

### Essai de faisabilité sur PHerc0343P [N]

Segment `20250902170435--5_b2`, cartes publiées par l'équipe (aucun calcul de modèle de notre côté) :

- la carte du modèle 2 µm (12 800 × 9 440 px) et les cartes à 8,64 µm (3 280 × 2 420 px) partagent le même repère
  (rapport 3,902 pour 3,901 attendu) ; le meilleur recalage est un décalage de (−1, −8) px ;
- corrélation avec la carte 2 µm ramenée à 8,64 µm : reader-v3 0,57, argus-v3 0,52, `ink_9um` s43-20k 0,06 ;
  reader-v3 et argus-v3 entre eux : 0,93 ;
- pré-étiquette selon la règle de reader-v2-labels : encre 0,23 cm² (5,8 %), fond 3,45 cm², bande incertaine
  0,22 cm² (5,7 %) ; désaccords avec les modèles 9 µm : 0,21 cm² ;
- 69 tuiles de 256 px sur 89 contiennent plus de 1 000 pixels à revoir : l'incertitude est répartie partout, il
  faudra la montrer à l'intérieur de chaque tuile plutôt que trier les tuiles.
- Ordre de grandeur : environ 0,4 cm² à revoir par segment.

### Tri de lisibilité des cartes 2 µm [N]

Regardé sur les planches réduites publiées par l'équipe (`ink-detection/downsampled`), objets non éligibles :

- PHerc0343P : seul `20250511003658-tifxyz` montre des lettres (trois lignes). Les 7 couches `_b2` ne montrent que
  des taches : rien à vérifier à la main.
- PHerc0500P2 : les 8 couches numérotées (`500P2_front`, `--1`, `0`, `--2`, `1`, `2`, `3`, `4`) montrent des lignes de
  lettres, nettes sur `front`, `--1` et `--2`, partielles ailleurs. Les segments `z_dbg_gen` regardés ne montrent que
  des taches. Or reader-v2-labels couvre `front` et 17 segments `z_dbg_gen`, mais aucune des 7 autres couches
  numérotées ; l'équipe n'a annoté que `--1`.
- PHerc0139 : lignes de texte sur les 6 segments regardés.
- Décision : cible de départ PHerc0500P2, couches numérotées.

## 10. Vérification d'antériorité approfondie (22 novembre, nuit)

Quatre balayages indépendants (Hugging Face, lauréats First Letters, outils d'annotation, pratique de l'équipe),
puis vérification à la source des points qui décident du plan. [B] = lu par un balayage, [N] = vérifié par nous.

### Qui a déjà des étiquettes faites à la main à ~9 µm

| Auteur | Objets hors concours | Nature | Format et licence | Ce que nous avons vérifié |
| --- | --- | --- | --- | --- |
| Priyank Aranke, https://huggingface.co/datasets/paranke/vesuvius-814-841-9b-studio-training-data | PHerc0814, 0841, 0009B (environ 260 cm² supervisés) | cartes du modèle 2 µm reportées puis corrigées à la main | `npy` maison, ses propres surfaces ; CC BY-NC 4.0 | fiche et manifeste [N] |
| jeff-j-chen, https://github.com/jeff-j-chen/HercUeNet | PHerc0500P2 (`front`, `--1`, `--2`), 0343P (`20250511003658`), 0009B (4 segments), 0841 w00, 0814, 0139 (w041, titre) | PNG dessinés à la main, clairsemés (encre sûre, fond non certifié), sur les volumes de surface natifs de l'équipe | PNG 0/255 ; MIT | arbre du dépôt, README, et mesure sur PHerc0500P2 (journal A6) [N] |
| Équipe (S3 `ink-labels` 20260918, dossier `ink/` du bucket) | PHerc0841 (3 segments, 3,4 cm²), 0009B (1, 2,6 cm²), 0500P2 `--1` (2,2 cm²) | annotations de l'équipe, repère du scan fin seulement | Zarr v3 2D | lu et mesuré (journal A5) [N] |
| Équipe, `ink_9um/labels/native9` | PHerc0139 (5 segments, 4,4 cm²) | annotées sur le scan natif | Zarr v2, 28 plans | [N] |
| Youssef Nader, https://huggingface.co/datasets/YoussefMoNader/ink-8um-pherc1447-surfaces et `ink-8um-v8-patchpack` | PHerc1447 w058, w060 (rouleau du Grand Prize) ; patchs 64 × 64 × 24 de 0139, 0814, 0500P2 `front`, 0009B | annotations de l'équipe | PNG et `npy` ; CC BY-NC 4.0 | [B] |
| Nicola Bodill, https://github.com/Bodillium/Herculaneum-Scroll-Labels | PHerc0172 | formes de lettres, 2024 | CC BY-NC-SA 4.0 | [B] |

Le dépôt de jeff-j-chen contient aussi des étiquettes sur un rouleau éligible à First Letters : on n'en copie rien
et on ne s'en sert pas pour entraîner.

### Ce que d'autres ont déjà mesuré, et que nous ne refaisons pas

| Source | Résultat | Conséquence pour nous |
| --- | --- | --- |
| Catalogue S3, champ `creation_info.quality` des jeux `ink-labels` [N] | L'équipe consigne l'accord entre ses étiquettes et « the independent ink prediction » : Dice au seuil 128 de 0,653 à 0,888 sur 24 jeux, médiane 0,815 (`--1` : 0,837) | Notre mesure A5 (F1 0,60 à 0,85 avec la carte publiée) confirme. La carte du modèle ne vaut pas une étiquette humaine |
| https://github.com/ibarapascal/ink-disagree (23/09) [N] | Recensement des 13 masques `validation` du jeu S3 : 9 blocs tenus à l'écart et 4 « surface entière » (PHerc0841 × 3, 0500P2 `--1`). Sur ces 4, noter sur `validation ∩ supervision`. La confiance calibrée du modèle 2 µm repère mieux ses erreurs (AUC 0,798) que le désaccord avec un second modèle (0,762). `ink_9um` sur PHerc0841 et 0500P2 : AP 0,69, AUC 0,85 | Antériorité pour le message Discord 1. Définir « incertain » par la confiance du modèle 2 µm. PHerc0500P2 est un rouleau où `ink_9um` est faible |
| https://github.com/slchicoineau-creator/tifxyz-canvas-map (19/10, MIT) [N] | Formule exacte entre canevas fin et natif d'un même segment : `p_natif = (p_fin + 10,5) × n_natif / n_fin − 10,5`. Résidu après formule : 0,5 à 1,5 px natifs (affine entre scans), un seul affine par segment suffit sauf sur PHerc0139 (limite) | Notre recalage A7 retrouve l'échelle (rapport des tailles de canevas) et mesure le résidu. À citer ; pas une nouveauté |
| khj1222, docs/33, et ticket villa #2243 [B] | Une carte du scan fin redimensionnée par aire tombe à environ 7 px du canevas natif ; concerne reader-v2-labels ; effet sur les modèles « unclear » (0,004 à 0,009 d'AUC) | Recaler avant de montrer quoi que ce soit à Jonathan |
| ChaseHendrick, kit `altrain` (03/11) [B] | Ronde d'étiquetage simulée : les tuiles choisies par incertitude ne battent pas les tuiles au hasard, à aucun budget | Le ciblage par incertitude est une hypothèse, pas un acquis |
| khj1222, docs/20 et docs/15 [B] | À budget fixe, le sous-ensemble où le modèle est le moins incertain gagne sur 7 segments sur 7. La moitié de l'annotation d'un segment garde 89 % du bénéfice, un cinquième 71 % | Peu d'étiquettes sur beaucoup de segments, plutôt qu'un segment entier |
| Domenico Russo, Erwin Nieuwlaar [B] | Cartes denses du modèle 2 µm contre étiquettes manuelles clairsemées : +0,03 à +0,10 de précision équilibrée, +4 points d'AUC | La densité a compté plus que la pureté des étiquettes. Notre comparaison doit donc se faire à surface égale |
| Liam Warner et Nicola Bodill, PHerc. 306B [B] | Tracés à la main d'un autre rouleau ajoutés 300 pas : +0,04 d'AP, intervalle au-dessus de 0 | Ordre de grandeur réaliste d'un gain |

### Outils d'étiquetage : rien d'utilisable au stylet [B]

- VC3D n'a pas de peinture d'étiquettes d'encre. PR villa #2532 (brouillon du 13/11), #2219 (fermée le 19/11),
  prototype navigateur #1714 (fermé le 22/09) : aucune fusionnée.
- Crackle Viewer, Kintsugi, khartes, outils napari : bureau seulement. Label Studio, CVAT, webKnossos : serveur à
  héberger, tactile peu fiable ou licence lourde. Klecks (MIT) : appli de peinture web avec stylet, généraliste.
- « Donor Studio » de Priyank Aranke n'est pas publié. L'équipe renvoie à GIMP ou Photoshop.
- Décision : écrire une petite page statique (canvas 2D, Pointer Events, sans framework), tuiles pré-découpées,
  stockage IndexedDB, export de la paire d'images de l'équipe, journal des traits. Le bucket S3 autorise le CORS.
- Pièges stylet relevés : `pointercancel` à traiter, deux doigts pour naviguer, bouton du S Pen non fiable côté
  web, HTTPS requis pour les événements fusionnés, 4 Go de mémoire sur la tablette. À valider sur l'appareil.

### Pratique et attentes de l'équipe [N] sauf mention

- Format lu par l'entraînement : `<segment>_inklabels[_vN].zarr`, `<segment>_supervision_mask[_vN].zarr`,
  `<segment>_validation_mask[_vN].zarr` (facultatif), Zarr v2 3D, annotation sur le plan médian (`Z // 2`). Trois
  variantes : alignée (21 plans), native (28 plans, 0/255, 6 niveaux) et sortie de `create_label_zarrs` (65 plans),
  lue par l'entraînement 21 et 28 couches seulement depuis la PR #2206 du 01/11 [B]. Pour rester compatible avec
  les forks plus anciens : écrire à la profondeur du volume de surface.
- Chaîne de l'équipe : images retouchées (`_inklabels.tif`, `_supervision_mask.tif`), puis
  `vesuvius.ink_detection.preprocessing.create_label_zarrs`. Report entre scans : `vesuvius.tifxyz_label_transfer`
  (géométrie 3D des maillages). Documentation : `vesuvius/docs/ink_detection.md` dans villa.
- Consigne d'étiquetage (tutoriel 5) : « Labeling is conservative: only regions where strokes are clearly and
  repeatably visible get labeled. » Encre et fond supervisé vont ensemble, le douteux reste hors supervision.
- Le mainteneur bruniss a fermé la PR villa #2381 (« suggest where to label next, from where the predictions are
  least sure ») le 01/11 : « without a training run comparison we'd prefer this one stay in a separate repo and
  linked in community projects ». C'est une demande faite à l'auteur de la PR, pour son outil : pas une demande de
  notre comparaison. La nôtre est une comparaison d'entraînements sur une question voisine (la source des
  étiquettes).
- Ticket villa #1638 (khj1222, 29/08) sur les 3 masques de validation collés à l'entraînement : fermé « not
  planned » et verrouillé le jour même par pmh47 : « "validation mask is disjoint from the supervision mask" --
  indeed, so there is no actual issue. » Présenter les 6 autres masques comme une ressource, pas comme un défaut.
- Le schéma du catalogue prévient que le sens de `validation` n'est pas uniforme d'un jeu à l'autre [B].
- Progress Prizes (page des prix) : « We discourage standalone analytic, auditing or evaluation tools, and
  instead encourage work that directly advances unwrapping or ink detection. » Un jeu de données et un modèle
  comptent ; un audit seul, non. Échéances mensuelles (prochaine : 30/11/2026).
- Ce que l'équipe a primé en 2026 autour de l'encre [B] : reader-v2 et reader-v3 (5 000 $ chacun), banc de
  checkpoints (1 000 $), pseudo-étiquettes denses (500 $), Rectina (250 $). Aucun jeu d'étiquettes vérifiées à la
  main en 2026 ; 1 000 à 2 500 $ pour des jeux d'étiquettes en 2023 et 2024.
- L'équipe reprend des modèles communautaires dans son catalogue (reader-v3, argus-v3), mais aucune étiquette
  communautaire [B]. Le chemin vers l'adoption passe par un modèle meilleur.
- First Letters : ticket villa #1739, réponse de pmh47 : entraîner sur du 2 µm est admis si le modèle est appliqué
  au volume éligible à 9 µm [B]. Le règlement refuse toute annotation manuelle de la zone revendiquée, même
  mémorisée par un modèle, et tout recouvrement entre entraînement et prédiction.
- Licence : la racine du bucket S3 est sous CC BY-NC 4.0, mais le README du jeu `ink-labels` renvoie à l'ancienne
  licence `dl.ash2txt.org/LICENSE.txt`, qui restreint la redistribution et vise les « ink label images » [B]. À
  demander avant de republier des étiquettes dérivées de celles de l'équipe.

### Ce qui reste libre, et ce que nous en faisons

1. Des étiquettes vérifiées à la main, au format de l'équipe, sur ses surfaces natives : cible PHerc0500P2,
   couches `0` à `4`.
2. La comparaison d'entraînements que les mainteneurs demandent : mêmes pixels, étiquettes humaines contre carte
   seule. Faisable dès maintenant avec les étiquettes humaines existantes (PHerc0009B, PHerc0500P2 `--1`), avant
   que Jonathan n'y passe du temps.
3. Un outil au stylet, et le temps de correction par cm².


## 11. Antériorité de la comparaison « étiquettes humaines contre carte du modèle » (24 novembre)

Question : quelqu'un a-t-il déjà publié un affinage où seule la source des étiquettes change, humaines contre
sorties de modèle ? Lu : dépôts déjà clonés et remis à jour le 24/11 (khj1222, ChaseHendrick/Scrolls,
ibarapascal/ink-disagree, DomRusso2, Nieuwlaar, SirProdigle, Jashann), deux dépôts trouvés par recherche web
(moisescorreo/vesuvius-uncertainty-bench, protonjls/vesuvius-first-letters), et les balayages du 22/11 (section 10).

| Source | Ce qui est comparé | Résultat publié | Différence avec la nôtre |
| --- | --- | --- | --- |
| https://github.com/moisescorreo/vesuvius-uncertainty-bench (29/08), section « 3b. The controlled experiment » [N] | affinage, même recette, étiquettes « model-generated » à 113/116 keV (la même carte `new_canon_autoresearch_recipe`, reportée en aval) contre étiquettes humaines à 54 keV (Scroll 1) | « letter form is learnable from human labels and not from model-generated labels » ; avec les étiquettes du modèle, chaque branche finit sous le checkpoint gelé | pas les mêmes pixels : les deux sources sont sur des scans, des énergies et des segments différents ; son propre audit signale un décalage de la carte d'environ 138 µm sur PHerc0343P ; notation contre des étiquettes dérivées du même générateur |
| khj1222, `submission/2026-09_progress_prize.md` et docs/18, primé 500 $ en septembre [N] | auto-apprentissage (pseudo-étiquettes du modèle 9 µm lui-même) contre une annotation humaine du même segment | « self-training gains +0.030 F1 … against +0.320 for a human annotation on the same segment » | maître faible (le modèle lui-même), sur le rouleau cible ; nous : maître fort (modèle 2 µm sur le scan fin), segments donneurs, notation sur zones tenues à l'écart et sur un rouleau jamais vu |
| protonjls/vesuvius-first-letters, `scroll_adapt/` (22/11) [N] | affinage de reader-v3 sur des pseudo-étiquettes de consensus de deux modèles 9 µm, sans humain | ne bat pas ses maîtres ; s'éloigne des étiquettes humaines de PHerc1447 | auto-apprentissage transductif, pas de comparaison appariée avec des étiquettes humaines |
| PR villa #2512 (DeepakEz) [B, recherche web] | auto-apprentissage et transfert de type de scan | petits gains | même remarque |
| Domenico Russo (ink9um-dense), Erwin Nieuwlaar (dense-native) [N, 22/11] | cartes denses du modèle 2 µm contre étiquettes manuelles clairsemées | +0,03 à +0,10 pour les cartes denses | surfaces supervisées différentes (dense contre clairsemé) |
| ChaseHendrick, kit `altrain` ; khj1222, docs/20 [N, 22/11] | où étiqueter (incertitude contre hasard) | le ciblage par incertitude ne gagne pas | autre question |

Conclusion : personne n'a publié la même comparaison (mêmes pixels, seule la source change, maître sur le scan
fin recalé au pixel près). Le résultat le plus proche (moisescorreo) conclut l'inverse du nôtre avec la même carte
du modèle, mais sans appariement et avec une carte décalée. D'où la branche `S` du banc (carte reportée sans
recalage, mêmes pixels), lancée le 24/11 pour tester si le recalage explique l'écart.

Autre point à citer dans la soumission (ChaseHendrick, `docs/FINDINGS.md`, finding 5) : deux des trois segments
étiquetés de PHerc0841 (w00 et ag896) sont le même papyrus (distance médiane 81 µm sur 98 % de 12,7 cm²). Notre
groupe « PHerc0841 » compte donc deux observations à peu près indépendantes, pas trois.
