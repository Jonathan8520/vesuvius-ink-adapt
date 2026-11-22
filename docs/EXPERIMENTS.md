# Journal des expériences

Une entrée par expérience : but, données, réglages, résultat chiffré, conclusion, fichiers produits.
Ne jamais noter ici de découverte de lettres sur un rouleau éligible au First Letters (dépôt public).

## Modèle d'entrée

```
### Eᴺ : titre (date)
- But :
- Données :
- Réglages (checkpoint, fenêtre, sens, pas) :
- Résultat :
- Conclusion :
- Fichiers :
```

## E0 : validation de la chaîne (22/11/2026)

- But : vérifier que notre rendu et notre modèle reproduisent les outils officiels.
- Données : PHerc. 211, segment `20261028201525-crop1711-lines123-v9` (public, lettres connues).
- Résultat : rendu r moyen 0,933 sur 28 couches ; modèle r = 0,912 contre la prédiction officielle du même
  checkpoint (seed43, step 20k) ; CPU et GPU identiques (r = 1,0) ; normalisation identique (écart 2,4e-7).
- Conclusion : chaîne fiable. Le sens « direct » et la fenêtre centrée correspondent au réglage officiel.
- Fichiers : `tests/validate_against_official.py`.

## E1 : prédictions publiées de PHerc. 0800 (22/11/2026)

- But : chercher des lettres dans les cartes d'encre déjà publiées par l'équipe pour un rouleau éligible.
- Données : 6 segments `auto_grown` (environ 2 × 2 cm chacun), 3 modèles (ink9um s43-20k, reader-v3, argus-v3).
- Résultat : taches d'environ 1 mm, aucun trait, aucune ligne alignée sur les fibres.
- Conclusion : rien de lisible avec les modèles actuels sur ces segments.

## E2 : balayage complet de PHerc. 1203 (22/11/2026)

- But : explorer des surfaces sans rendu publié.
- Données : 22 surfaces `PHerc1203/segments/raw/auto_grown_*`, volume éligible 9,362 µm (20250820131727).
- Réglages : 28 couches (décalages −14..13) ; s43-20k fenêtres 3, 6, 9 ; s43-60k fenêtre 6 ; s42-75k
  fenêtre 6 ; deux sens ; patchs 128, pas 64 ; moyenne par sens.
- Exécution : notebook Kaggle privé, GPU T4, 83 min, 24,5 Go lus, environ 120 cm² (avec recouvrements).
- Résultat : bruit uniforme sur les 22 surfaces. Classement automatique des fenêtres de 2 × 2 mm par contraste
  (p95 − médiane) : les 4 meilleures sont des faux positifs (zones écrasées, bords de morceaux, trous).
  Le checkpoint s43-60k donne des probabilités plus élevées partout (biais du checkpoint, pas de l'encre).
- Conclusion : pas d'encre lisible avec les modèles publics sur ces surfaces automatiques.
- Fichiers : `kaggle/vesuvius_pherc1203_sweep.py`.

## E0 bis : grille officielle des tuiles (22/11/2026, soir)

- But : expliquer l'écart de 0,912 entre notre inférence et la prédiction officielle.
- Données : PHerc. 211, même segment et même zone que E0 (0:1720 × 4000:4500).
- Réglages : s43-20k, fenêtre centrée 6..22, sens direct ; tuiles sur la grille globale de la surface (0, 64, ...,
  plus une tuile alignée sur le bord), tuiles entièrement vides ignorées, comme `infer.py` de villa.
- Résultat : r = 0,9999, écart maximal 1 niveau sur 255 (256 patchs). Avec la grille locale au recadrage : 0,912
  (180 patchs).
- Conclusion : le modèle réimplémenté est exact. L'écart venait du découpage des tuiles (recadrage à x = 4000,
  hors de la grille de pas 64). `core.infer_roi` ajouté ; la validation exige r > 0,99.
- Fichiers : `vesuvius_ink_adapt/core.py`, `tests/validate_against_official.py`.

## E3 : abandonné avant exécution (22/11/2026)

- But prévu : score de référence d'`ink_9um` sur les 9 segments réservés.
- Pourquoi : ces scores sont déjà publiés (DomRusso2/ink9um-dense, khj1222 docs/14, inkbench, gowtham012), et les
  9 segments figurent dans la liste d'entraînement des checkpoints. Voir `docs/RESEARCH.md`.
- Fait à la place : les audits A1 et A2 ci-dessous. E4 à E7 n'ont pas été commencés. Sprint arrêté le soir même.

## A1 : audit des zones de validation réservées, masques seuls (22/11/2026, soir)

- But : savoir quels pixels des 9 cas réservés n'ont jamais servi à l'entraînement d'`ink_9um`.
- Données : masques de supervision et de validation du dépôt 9 µm (Hugging Face, `ink_9um/`), masques
  `validation.zarr` du bucket S3 (`ink-labels/<volume>/20260918/`, niveau 2), étiquettes natives du segment w044.
- Réglages : aucun modèle. Distance aux pixels d'entraînement calculée par îlot.
- Résultat : 3 zones publiées à 9 µm (721 550 px, 0,66 cm²) et 6 zones absentes du dossier 9 µm (3 818 877 px,
  3,52 cm²). Recouvrement avec la supervision d'entraînement : 0 pixel pour les 9. Part des pixels à moins de
  256 px d'un pixel d'entraînement : 99 %, 88 %, 45 % pour les zones publiées (w016, 0814, 1667-w029) ; 9 %, 0 %,
  3,5 %, 0 %, 0 %, 0 % pour les autres (0139-w028, 0139-w029, 1667-w018, w023, w028, w031). Le jumeau natif w044
  ne couvre pas la zone réservée de 0139-w028 (distance médiane 522 px). Tableau complet dans `docs/RESEARCH.md`.
- Correction du 22/11 (21 h 40 UTC) : ces 6 masques sont aussi dans le dossier `ink/` du bucket Hugging Face
  depuis le 07/07/2026 (`*_validation_mask_v2.tif`, vérifié par listing), et l'audit de nestorvfx du 24/09 les
  recense. Ils ne manquent que dans `ink_9um/labels`.
- Contrôle : sur les 3 masques publiés, on retrouve l'audit de khj1222 (59,3 %, 45,0 %, 23,2 % à moins de 128 px ;
  publié 58,6 %, 45,0 %, 23,2 %). Notre masque de w016 compte 178 146 px, le sien 175 222 : écart non expliqué.
- Conclusion : la validation tenue à l'écart d'`ink_9um` est 5,3 fois plus grande que ce que le dépôt 9 µm laisse
  voir, et les zones non publiées sont isolées des pixels d'entraînement. Antériorité non vérifiée à fond.
- Fichiers : `scripts/audit_reserved_validation.py`.

## A2 : test de mémorisation sur les 9 zones réservées (22/11/2026, nuit)

- But : vérifier par le modèle que les zones non publiées à 9 µm n'ont pas servi à l'entraînement.
- Données : entrées 2,4 µm réduites à 21 couches (niveau 2, moyenne de 4 plans), lues sur S3 autour de chaque zone.
- Réglages : s43-75k, fenêtre centrée 2..18, sens direct, patchs 128, pas 64, grille globale (`core.infer_roi`).
  Mesures dans la zone réservée, puis sur les pixels de supervision d'entraînement du même segment (6 îlots tirés
  au hasard au plus). Précision équilibrée à 0,5 / F1 à 0,5 / AUC. Durée : 19 min sur CPU pour les 9 cas.
- Résultat :

| Cas | Publié à 9 µm ? | Zone réservée | Pixels d'entraînement |
| --- | --- | --- | --- |
| pherc0139-w016 | oui | 0,810 / 0,720 / 0,937 | 0,975 / 0,955 / 0,994 |
| pherc0814-46527 | oui | 0,773 / 0,712 / 0,863 | 0,992 / 0,988 / 0,9998 |
| pherc1667-w029 | oui | 0,838 / 0,758 / 0,930 | 0,989 / 0,983 / 0,9996 |
| pherc0139-w028 | non | 0,731 / 0,610 / 0,841 | 0,989 / 0,980 / 0,9995 |
| pherc0139-w029 | non | 0,783 / 0,700 / 0,879 | 0,936 / 0,911 / 0,976 |
| pherc1667-w018 | non | 0,734 / 0,600 / 0,830 | 0,944 / 0,909 / 0,986 |
| pherc1667-w023 | non | 0,643 / 0,439 / 0,769 | 0,980 / 0,966 / 0,998 |
| pherc1667-w028 | non | 0,818 / 0,737 / 0,926 | 0,992 / 0,987 / 0,9996 |
| pherc1667-w031 | non | 0,687 / 0,539 / 0,810 | 0,986 / 0,976 / 0,9992 |

- Contrôle : les 3 zones publiées redonnent les chiffres de DomRusso2 pour s43-75k (0,810 / 0,937, 0,772 / 0,863,
  0,837 / 0,930 en précision équilibrée et AUC).
- Conclusion : les 6 zones non publiées se comportent comme des zones jamais vues. AUC moyenne pondérée par pixel :
  0,83 dans ces 6 zones, 0,92 dans les 3 zones publiées. Les 9 zones deviennent nos données de mesure.
- Fichiers : `scripts/audit_reserved_validation.py --memo s43-75k`.

## A3 : inventaire des rouleaux, scans et étiquettes (22/11/2026, nuit)

- But : étape 1 du plan « étiquettes vérifiées à la main ».
- Données : catalogue du bucket S3 (`metadata.json`), `prizeEligibility.json`, fiches des jeux d'étiquettes publiés.
- Résultat : 39 objets ont un scan ; 10 objets hors First Letters ont un scan fin et un scan à ~9 µm (PHerc0009B,
  0139, 0332, 0343P, 0500P2, 0814, 0841, 1451, 1667, Paris4). Étiquettes vérifiées à la main à ~9 µm : 0814, 0841,
  0009B (Priyank Aranke, 250 cm²), 5 segments de 0139 (équipe). Sorties de modèle seulement : 0343P, 0500P2,
  le reste de 0139. Aucune surface à ~9 µm publiée : 1667, Paris4.
- Fichiers : `scripts/inventory.py`, `docs/INVENTAIRE.md`.

## A4 : faisabilité des pré-étiquettes et tri de lisibilité (22/11/2026, nuit)

- But : savoir si la carte du modèle 2 µm se reporte sur la surface à ~9 µm, et où un humain peut la vérifier.
- Données : cartes d'encre publiées par l'équipe (aucun calcul de modèle de notre côté). PHerc0343P, segment
  `20250902170435--5_b2` pour le recalage ; planches réduites (`ink-detection/downsampled`) de PHerc0343P (7
  segments), PHerc0500P2 (16 segments) et PHerc0139 (6 segments) pour la lisibilité. Aucun rouleau éligible.
- Résultat, recalage : même repère pour la carte 2 µm et les cartes 8,64 µm (rapport 3,902), meilleur décalage
  (−1, −8) px. Corrélation avec la carte 2 µm ramenée à 8,64 µm : reader-v3 0,57, argus-v3 0,52, `ink_9um` 0,06.
  Bande 64 à 128 : 5,7 % de la surface, surtout le contour des taches.
- Résultat, lisibilité : PHerc0343P, 1 segment lisible sur 8 (`20250511003658-tifxyz`), les couches `_b2` ne
  montrent que des taches. PHerc0500P2 : les 8 couches numérotées montrent des lignes de lettres (nettes sur
  `front`, `--1`, `--2`), les segments `z_dbg_gen` regardés seulement des taches. PHerc0139 : lignes de texte sur les
  6 segments regardés.
- Conclusion : la cible de départ passe de PHerc0343P à PHerc0500P2 (couches numérotées). Le recalage est à faire
  sur la texture CT, pas sur les modèles. Les zones à montrer à Jonathan ne peuvent pas être la seule bande 64 à 128.
- Fichiers : aucun dans le dépôt (sondes dans le dossier temporaire de la session).

## A5 : carte du modèle 2 µm contre étiquettes humaines de l'équipe (22/11/2026, nuit)

- But : savoir combien une correction humaine peut changer par rapport à la carte du modèle 2 µm seuillée (règle
  de reader-v2-labels : encre si carte ≥ 128, fond si ≤ 64).
- Données : les 28 segments hors concours qui ont des étiquettes de l'équipe sur S3 (`ink-labels/.../20260918`) et
  la carte `new_canon_autoresearch_recipe` du même volume fin. Comparaison au niveau 2 (pas de 8,9 à 9,6 µm), carte
  moyennée 4 × 4. Aucun calcul de modèle de notre côté.
- Résultat (moyennes pondérées par pixel) :

| Objet | Pixels supervisés | AUC | F1 au seuil 128 | F1 au meilleur seuil | Encre humaine que la carte dit fond | Fond humain que la carte dit encre |
| --- | --- | --- | --- | --- | --- | --- |
| PHerc0500P2 (`--1`, jamais vu par le modèle 2 µm) | 2,8 M | 0,975 | 0,84 | 0,84 | 8 % | 4 % |
| PHerc0841 (3 segments, jamais vus) | 3,7 M | 0,924 | 0,76 | 0,77 | 12 % | 10 % |
| PHerc0009B (1 segment) | 2,8 M | 0,95 à 0,96 | 0,81 à 0,82 | 0,82 | 11 à 13 % | 5 à 6 % |
| PHerc0814 (1 segment) | 0,6 M | 0,94 à 0,97 | 0,84 à 0,85 | 0,85 | 3 à 6 % | 11 % |
| PHercParis4 (8 segments) | 88,9 M | 0,942 | 0,80 | 0,80 | 12 % | 8 % |
| PHerc1667 (6 segments) | 31,2 M | 0,91 à 0,92 | 0,74 à 0,76 | 0,74 à 0,77 | 19 % | 6 à 8 % |
| PHerc0139 (8 segments) | 7,3 M | 0,87 à 0,91 | 0,60 à 0,73 | 0,68 à 0,78 | 22 à 33 % | 7 à 10 % |

- Lecture : la carte seuillée et les étiquettes humaines ne se recouvrent qu'à 60 à 85 % (F1). Sur `--1`, pas de
  décalage entre les deux (≤ 1 px) et même part d'encre (21 %) : l'écart est un vrai désaccord sur les traits, pas
  un problème de seuil. Sur PHerc0139, le seuil 128 est trop haut (meilleur seuil entre 39 et 130).
- Pas de trace de mémorisation : dans les zones de validation et dans le reste de la supervision, les scores sont
  les mêmes. La carte publiée ne recopie donc pas les étiquettes.
- La bande 64 à 128 couvre 4 à 8 % de la surface et ne contient que 5 à 12 % de l'encre humaine. Les désaccords
  (carte au seuil 128 contre étiquette humaine) couvrent 7 à 16 % de la surface, et seulement 14 à 24 % d'entre eux
  tombent dans la bande (18 % tous rouleaux confondus) : montrer seulement cette bande à Jonathan en manquerait
  l'essentiel.
- Antériorité (trouvée après coup) : le catalogue S3 consigne déjà cet accord pour 24 jeux (champ
  `creation_info.quality`, Dice au seuil 128 de 0,653 à 0,888, médiane 0,815 ; `--1` : 0,837 contre 0,844 chez
  nous), et ibarapascal/ink-disagree (23/09) a audité le même modèle contre les mêmes étiquettes. Notre mesure
  confirme ; ce qu'elle ajoute : la séparation validation / reste et la part des désaccords hors de la bande.
- Image : `docs/img/pherc0500p2_m1_carte_vs_humain.png` (carte et étiquettes de l'équipe, dérivées de « Vesuvius
  Challenge - CT Scans of Herculaneum Papyri », CC BY-NC 4.0 ; PHerc0500P2 n'est éligible à aucun prix).
- Fichiers : `scripts/teacher_vs_team.py`, résultats dans `data/teacher/teacher_vs_team.json` (hors dépôt).

## A6 : étiquettes de jeff-j-chen sur PHerc0500P2 (22/11/2026, nuit)

- But : savoir ce que couvrent les étiquettes PNG du dépôt jeff-j-chen/HercUeNet (MIT) sur notre cible.
- Données : ses fichiers `dilated_inklabels`, `train_masks` et `masks` pour les couches `front`, `--1` et `--2`
  (rouleau hors concours ; aucun autre fichier de ce dépôt n'a été téléchargé), étiquettes de l'équipe sur `--1`,
  cartes du modèle 2 µm. Tout est ramené dans un même repère par le recalage de A7.
- Résultat :
  - `--1` : dans la zone supervisée par l'équipe, ses étiquettes sont celles de l'équipe (IoU 0,992 après report,
    un décalage d'un pixel fait baisser le score). Son masque d'entraînement est deux fois plus grand (5,7 M px
    contre 2,8 M), avec 8 % d'encre.
  - `--2` : étiquettes à lui, clairsemées. 7 % d'encre dans son masque, contre 14 % pour la carte 2 µm au seuil
    128 ; IoU 0,40 avec la carte ; 78 % de son encre est à moins de 3 px d'encre de la carte, mais seulement 51 % de
    l'encre de la carte est proche de la sienne. Il marque les traits sûrs et laisse le reste sans le certifier
    comme fond (son entraînement traite le reste en « non étiqueté »).
  - `front` : étiquettes proches de la carte (IoU 0,68), avec des négatifs durs peints (0,7 M px). Son journal dit
    « Clear labels transferred from 2.215µm ».
- Conclusion : sur PHerc0500P2, `front`, `--1` et `--2` ont déjà des étiquettes faites à la main (denses de l'équipe
  sur `--1`, clairsemées de jeff-j-chen sur `--2`). Les couches `0`, `1`, `2`, `3`, `4` n'ont aucune étiquette
  humaine. Aucun de ces jeux n'est au format de l'équipe.
- Ce dépôt contient aussi des étiquettes sur un rouleau éligible à First Letters : on n'en copie rien.

## A7 : recalage du scan fin vers la surface ~9 µm par la texture CT (22/11/2026, nuit)

- But : reporter sur le canevas natif ~9 µm les cartes et les étiquettes posées sur le scan fin (étape 2b).
- Méthode : moyenne de 4 couches natives autour de la surface et de la même épaisseur dans le volume fin (niveau
  2), filtre passe-haut, corrélation par tuiles de 384 px, puis ajustement affine robuste
  (`index_fin = A @ index_natif + t`).
- Résultat : les deux canevas ne se déduisent pas du seul rapport des tailles de voxel. Écart d'échelle d'environ
  0,4 % et décalage constant de 5 à 10 px. Après ajustement affine :

| Objet | Segments | Échelle mesurée (nominale) | Résidu médian | Résidu p90 |
| --- | --- | --- | --- | --- |
| PHerc0500P2 | 8 couches numérotées | 1,051 à 1,055 (1,0567) | 0,36 à 0,43 px | 0,66 à 1,22 px |
| PHerc0841 | 3 | 0,974 à 0,975 (0,9744) | 0,55 à 0,58 px | 1,28 à 1,38 px |
| PHerc0009B | 1 | 0,900 (0,8996) | 0,78 px | 1,63 px |
| PHerc0814 | 1 (46527) | 0,970 à 0,977 (0,9755) | 0,26 px | 1,26 px |
| PHerc0139 | w035, w039, w040, w041, w044 | 0,971 à 0,974 (0,9755) | 0,59 à 0,78 px | 1,1 à 1,9 px |

- Contrôles : (1) corrélation de texture natif contre fin reporté, médiane 0,94 sur `--1` ; (2) étiquettes de
  l'équipe reportées sur `--1` contre le report indépendant de jeff-j-chen (SIFT et champ de déplacement) : IoU
  0,992 ; (3) PHerc0139, 5 segments où l'équipe publie des étiquettes dans les deux repères : IoU de l'encre
  0,956 à 0,986 (0,988 à 0,991 avec un décalage d'un pixel pour w035, w039, w040, w041), IoU des masques de
  supervision 0,992 à 0,995 pour ces quatre-là. Pour w044, les deux jeux ne couvrent pas la même région (le jeu
  du scan fin est le cas `pherc0139-w028`), d'où un IoU de supervision de 0,57 qui n'est pas un défaut de recalage.
- Antériorité : l'outil officiel est `vesuvius.tifxyz_label_transfer` de villa (report par la géométrie 3D des
  maillages, cas général). Notre affine ne vaut que pour deux canevas issus du même maillage aplati, ce qui est le
  cas des 132 segments hors concours qui ont les deux volumes de surface sur S3.
  Trouvé après coup : slchicoineau-creator/tifxyz-canvas-map (MIT, 19/10) donne la formule exacte
  `p_natif = (p_fin + 10,5) × n_natif / n_fin − 10,5` et mesure le même résidu (0,5 à 1,5 px, un affine par segment,
  limite sur PHerc0139). Notre échelle mesurée est bien le rapport des tailles de canevas (1,0527 pour `--1`), et
  notre décalage (9,3 ; 7,6) s'écarte de celui de la formule (8,1 ; 8,0) d'environ 1 px : c'est ce résidu. Notre
  recalage n'est donc pas une nouveauté ; il sert de contrôle indépendant et corrige le résidu.
- Fichiers : `vesuvius_ink_adapt/register.py`, `scripts/register_fine_to_native.py`, sorties dans `data/register/`.

## A8 : banc de mesure par affinage, mise au point et pré-test (22 et 23/11/2026)

- But : savoir, avant toute correction par Jonathan, si des étiquettes humaines font mieux que la carte du modèle
  2 µm seuillée quand on les pose sur les mêmes pixels (étape 5b du plan).
- Données (`scripts/build_bench.py`, jeu Kaggle privé `jonathan8520/vesuvius-ink9um-bench`, 3,7 Go) :
  - rejeu : les 29 représentations du corpus `ink_9um` en tuiles de 256 px (2 191 tuiles ; au plus 150 par
    segment de PHercParis4 et 120 par segment de PHerc1667, tirage fixe) ; étiquettes du dépôt 9 µm pour les 9 cas
    réservés, niveau 2 des étiquettes S3 pour les autres segments alignés, étiquettes natives S3 pour PHerc0139 ;
  - segments nouveaux, canevas natif : PHerc0500P2 `--1` (71 tuiles, 2,5 M px supervisés) et PHerc0009B
    `ag487` (68 tuiles, 3,4 M px), chacun avec deux versions d'étiquettes sur les mêmes pixels : `h` (étiquettes
    de l'équipe reportées par le recalage A7) et `t` (carte du modèle 2 µm reportée, encre si ≥ 128, fond si
    ≤ 64, bande hors supervision) ;
  - évaluation : les 9 zones réservées (4,5 M px) et les 3 segments de PHerc0841 (3,8 M px, canevas natif).
- Contrôles avant lancement : aucun pixel supervisé à l'entraînement dans une zone d'évaluation ; les branches
  `T` et `H` de même graine tirent exactement les mêmes patchs (les étiquettes diffèrent sur 6 % des pixels des
  segments nouveaux) ; PHerc0841 absent de l'entraînement.
- Réglages (`vesuvius_ink_adapt/finetune.py`, recette abrégée) : départ s43-75k, SGD de Nesterov, momentum 0,99,
  taux 0,002, échauffement 100 pas, cosinus, lot de 64, précision mixte, BCE lissée 0,5 plus Dice. Quotas par
  lot : témoin `C` 29 / 22 / 11 / 2 (recette de l'équipe) ; `T` et `H` 20 / 15 / 8 / 1 plus 10 + 10 pour les
  segments nouveaux (31 %).
- Contrôle du banc (branche `base`, aucun pas) : w016 0,8100 / 0,7200 / 0,9365 et 0814 0,7731 / 0,7124 / 0,8628
  (précision équilibrée, F1, AUC), sur CPU et sur T4 : identiques à l'audit A2 et aux chiffres de Domenico Russo.
- Essai court sur Kaggle (2 × T4, 30 pas, 160 s en tout) : 0,90 s par pas, mémoire suffisante au lot de 64.
- Pré-test lancé le 22/11 à 22 h 16 UTC : kernel `jonathan8520/vesuvius-ink9um-bench-pretest`, branches `base`,
  `C`, `T`, `H`, graines 0 à 4, 1 000 pas, notations à 250, 500 et 1 000 pas, histogrammes par bloc de 128 px
  pour un bootstrap par blocs. Durée attendue : 2 h 30. **Résultat : à venir.**
- Limites connues : recette abrégée (augmentations réduites), rejeu partiel de PHercParis4 et PHerc1667, étiquettes
  de test dessinées par l'équipe comme celles de la branche `H` (avantage de style possible).
- Fichiers : `scripts/build_bench.py`, `vesuvius_ink_adapt/finetune.py`, `scripts/run_bench.py`,
  `kaggle/bench/bench_kernel.py`.

## A9 : appli au stylet, version 0.1, et lot d'étalonnage (22 et 23/11/2026)

- But : étape 3 du plan. Une page que Jonathan ouvre sur sa tablette pour vérifier les pré-étiquettes, et un
  premier lot en aveugle sur la couche `--1` de PHerc0500P2, déjà annotée par l'équipe.
- Tuiles (`scripts/make_app_tiles.py`) : 6 tuiles sans recouvrement, chacune de 1 536 px natifs de côté (14,4 mm),
  travaillées à demi-résolution (768 px, 18,7 µm par pixel) pour voir plusieurs lettres et deux ou trois lignes à
  la fois. Par tuile : une planche JPEG de 7 panneaux (composite CT, 5 couches CT, carte du modèle 2 µm reportée)
  et une pré-étiquette PNG (encre si carte ≥ 128, fond si ≤ 64, « je ne sais pas » entre les deux, hors papyrus
  verrouillé). 8,1 Mo en tout. Le lot couvre 2,46 cm² supervisés par l'équipe ; les étiquettes de l'équipe ne sont
  pas dans le lot. La zone montrée dans `docs/img/pherc0500p2_m1_carte_vs_humain.png` est retirée du score.
- Appli (`app/index.html`, page statique sans dépendance) : le stylet ou la souris peint, deux doigts déplacent et
  zooment, trois classes, pinceaux de trois tailles, « Remplir » pour accepter ou rejeter une tache entière,
  annuler et rétablir, bascule carte ou couches CT, contour franc et remplissage translucide réglable, minuteur de
  20 minutes de travail effectif, reprise là où l'on s'est arrêté, journal des traits. « Valider » signifie que
  toute la tuile a été regardée : est supervisé tout ce qui n'est pas « je ne sais pas ».
- Stockage : base de l'artifact (collection `etiquettes`, un document par tuile, étiquettes codées en plages,
  environ 23 Ko), copie locale dans le navigateur dans tous les cas, « copie de secours » à copier si la base ne
  répond pas.
- Essais (Chromium sans écran, 1 333 × 800, tactile) : trait à la souris, annulation, remplissage, trait au stylet
  (événement `pointerType: pen`), zoom à deux doigts, changement de vue, validation, rechargement avec reprise à
  la tuile suivante, largeur de téléphone sans défilement horizontal, aucune erreur de console. Base de
  l'artifact : écriture, lecture et suppression d'un document d'essai par la session.
- Pas encore essayé : l'écriture par la page elle-même dans la base (seulement dans le visualiseur de claude.ai),
  et le stylet réel de la Galaxy Tab S6 Lite. C'est l'objet de la première séance.
- Relecture et score (`scripts/read_app_labels.py`) : décode les documents, compare aux étiquettes de l'équipe
  (IoU, précision, rappel, part laissée en doute), et donne le débit en cm² par heure. Contrôle : sur une tuile non
  corrigée, la pré-étiquette obtient un IoU de 0,68 avec l'équipe (précision 0,72, rappel 0,93).
- Fichiers : `app/index.html`, `scripts/make_app_tiles.py`, `scripts/make_prelabels.py`, `scripts/read_app_labels.py`.

## A10 : premier essai de l'appli par Jonathan, et plafond d'un tri « tache par tache » (22/11/2026, 22 h 45 UTC)

- Essai : Jonathan a ouvert l'appli sur sa tablette (affichage correct, lot `etalon-m1`, tuile 1 sur 6) et s'est
  arrêté au bout d'une minute et demie : il ne sait pas quoi juger. Il ne connaît pas les formes des lettres
  grecques, et l'appli ne lui montrait aucun exemple corrigé.
- Question posée ensuite : ce qu'un non-spécialiste peut faire (garder ou rejeter une tache entière) rapproche-t-il
  la pré-étiquette des étiquettes de l'équipe ?
- Données : les 6 tuiles du lot d'étalonnage (couche `--1` de PHerc0500P2), vérité de l'équipe, zone déjà montrée
  exclue. Chiffres agrégés seulement, sans regarder les images de vérité.
- Résultat :

| Étiquette comparée à celle de l'équipe | IoU de l'encre |
| --- | --- |
| Pré-étiquette brute (carte du modèle 2 µm ≥ 128) | 0,719 |
| Tri parfait des taches entières (oracle : 17 taches rejetées sur 39) | 0,736 |
| Tri parfait des taches, plus bande 64 à 128 tranchée pixel par pixel | 0,804 |

  La pré-étiquette manque 15,8 % de l'encre de l'équipe et pose 77 553 px de fausse encre, dont 16 % seulement
  disparaissent en rejetant des taches entières. Le reste des écarts est dans la forme des traits : épaisseur,
  raccords, découpe.
- Conclusion : ce qui sépare les étiquettes de l'équipe de la carte, c'est le redessin des traits en lettres. Cela
  demande de connaître les formes des lettres. Un tri tache par tache, seule tâche accessible sans cette
  connaissance, gagne au mieux 0,017 d'IoU. Le temps de Jonathan au stylet n'est donc pas le bon levier.
- Décision : séances au stylet suspendues. On attend le pré-test A8, qui dit si les étiquettes humaines de l'équipe
  apportent quelque chose à l'entraînement. La session ne remplace pas Jonathan pour le redessin : ce ne seraient
  plus des étiquettes vérifiées à la main, et un modèle qui « complète » des lettres dans des taches fabriquerait
  des étiquettes plausibles, ce que l'équipe demande justement d'éviter.
