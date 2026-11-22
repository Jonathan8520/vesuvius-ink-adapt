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
- Résultat : 3 zones publiées à 9 µm (721 550 px, 0,66 cm²) et 6 zones présentes seulement sur S3 (3 818 877 px,
  3,52 cm²). Recouvrement avec la supervision d'entraînement : 0 pixel pour les 9. Part des pixels à moins de
  256 px d'un pixel d'entraînement : 99 %, 88 %, 45 % pour les zones publiées (w016, 0814, 1667-w029) ; 9 %, 0 %,
  3,5 %, 0 %, 0 %, 0 % pour les autres (0139-w028, 0139-w029, 1667-w018, w023, w028, w031). Le jumeau natif w044
  ne couvre pas la zone réservée de 0139-w028 (distance médiane 522 px). Tableau complet dans `docs/RESEARCH.md`.
- Contrôle : sur les 3 masques publiés, on retrouve l'audit de khj1222 (59,3 %, 45,0 %, 23,2 % à moins de 128 px ;
  publié 58,6 %, 45,0 %, 23,2 %). Notre masque de w016 compte 178 146 px, le sien 175 222 : écart non expliqué.
- Conclusion : la validation tenue à l'écart d'`ink_9um` est 5,3 fois plus grande que ce que le dépôt 9 µm laisse
  voir, et les zones non publiées sont isolées des pixels d'entraînement. Antériorité non vérifiée à fond.
- Fichiers : `scripts/audit_reserved_validation.py`.

## A2 : test de mémorisation sur les zones réservées (22/11/2026, soir), interrompu

- But : vérifier par le modèle que les zones non publiées n'ont pas servi à l'entraînement.
- Données : entrées 2,4 µm réduites à 21 couches (niveau 2, moyenne de 4 plans), lues sur S3 autour de chaque zone.
- Réglages : s43-75k, fenêtre centrée 2..18, sens direct, patchs 128, pas 64, grille globale (`core.infer_roi`).
  Mesures dans la zone réservée, puis sur les pixels de supervision d'entraînement du même segment (6 zones tirées
  au hasard au plus). Précision équilibrée à 0,5 / F1 à 0,5 / AUC.
- Résultat (segments terminés avant l'arrêt) : voir le tableau de `docs/HANDOFF.md`. Zones publiées : w016 0,810 /
  0,720 / 0,937 et 0814 0,773 / 0,712 / 0,863, identiques aux chiffres de DomRusso2 (0,810 / 0,937 et 0,772 / 0,863).
  Zones non publiées : 0139-w028 0,731 / 0,610 / 0,841 et 0139-w029 0,783 / 0,700 / 0,879. Pixels d'entraînement des
  mêmes segments : 0,936 à 0,992 / 0,911 à 0,988 / 0,976 à 0,9998.
- Conclusion : les deux zones non publiées testées ont le score d'une zone jamais vue. Les 4 zones de PHerc. 1667
  n'ont pas été testées.
- Fichiers : `scripts/audit_reserved_validation.py --memo s43-75k`.
