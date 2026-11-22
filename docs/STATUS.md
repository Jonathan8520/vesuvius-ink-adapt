# Point du 22 novembre 2026 (nuit) : sprint arrêté

## Décision

Jonathan arrête le sprint Progress Prizes de novembre. Pas de soumission. Plus aucun calcul lancé.

## Pourquoi on s'arrête

- **Tout notre plan a déjà été fait par d'autres**, souvent avec un résultat négatif : score de référence
  d'`ink_9um`, choix de profondeur sans étiquette, TENT, ensembles de checkpoints, chaîne sans C++.
  Liens et chiffres : `docs/VEILLE-2026-11-22.md` et `docs/RESEARCH.md`.
- **La référence à 9 µm a changé** : c'est reader-v3 (Domenico Russo), plus `ink_9um`.
- **First Letters sur PHerc. 1203** : déjà travaillé par des équipes mieux équipées, y compris avec le scan à
  2,4 µm (constat de Jonathan). Notre balayage des 22 surfaces n'avait rien montré.
- **Gain espéré faible** : sur cet axe, le jury donne 250 à 1 000 $ et décourage les outils d'évaluation isolés.

## Ce qui marche (vérifié le 22/11)

- `python tests/validate_against_official.py` : `VALIDATION OK`. Rendu 0,933. Encre **0,9999** contre la sortie
  officielle (c'était 0,912 : l'écart venait seulement du découpage des tuiles, corrigé par `core.infer_roi`).
- Lecture des données publiques sans dépendance : `vesuvius_ink_adapt/zarrio.py` (étiquettes Hugging Face et S3).
- Notre chaîne retrouve les chiffres publiés par d'autres : s43-75k sur le masque de w016, précision équilibrée
  0,810 et AUC 0,937 (Domenico Russo : 0,810 et 0,937).

## Ce qu'on a appris

1. **Chercher avant de coder.** Une soirée de veille a invalidé une semaine de plan.
2. **Les 9 segments « réservés » ne sont pas des rouleaux jamais vus** : ils sont dans la liste d'entraînement.
   Seule une zone par segment est tenue à l'écart.
3. **Observation nouvelle (à notre connaissance)** : le dépôt 9 µm ne publie la zone tenue à l'écart que pour
   3 des 9 segments. Les 6 autres zones existent sur S3, n'ont aucun pixel commun avec les masques d'entraînement
   publiés, et pèsent 5 fois plus (3,5 cm² contre 0,66 cm²), loin des pixels d'entraînement. Test de
   mémorisation : voir `docs/HANDOFF.md` pour les segments vérifiés.
4. **Les « gains » publiés sur 3 petits masques sont souvent du niveau du bruit** (0,02 à 0,13 entre graines).

## Kaggle

- Aucun run lancé le 22/11 au soir, aucun en file, aucun en cours. Rien à annuler.
- Les deux notebooks privés existants sont terminés. Quota GPU restant : 28,6 h jusqu'au 28/11.

## Besoins éventuels

- Aucun. Une seule chose à décider si tu le souhaites : signaler à l'équipe les 6 masques de validation absents
  du dépôt 9 µm (ticket sur villa ou message sur Discord, écrit par toi). Tout est dans `docs/HANDOFF.md`.
