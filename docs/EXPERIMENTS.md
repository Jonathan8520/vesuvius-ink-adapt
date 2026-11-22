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
