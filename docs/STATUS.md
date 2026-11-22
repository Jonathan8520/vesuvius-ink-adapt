# Point du 22 novembre 2026 (nuit) : nouveau cap, étiquettes vérifiées à la main

## Où on en est

- Le sprint de novembre est arrêté (tout avait déjà été publié par d'autres).
- Nouveau cap : publier d'ici le 31 décembre des étiquettes d'encre vérifiées à la main par toi, avec la preuve
  qu'elles améliorent un modèle, puis viser First Letters. Plan : `docs/PLAN.md`.

## Fait ce soir

- Lu le billet sur PHerc. 211 et les dépôts de Priyank Aranke.
- Inventaire des rouleaux, scans et étiquettes existantes : `docs/INVENTAIRE.md`.
- `CLAUDE.md` mis à jour, veille corrigée, plan réécrit avec jalons et critères d'arrêt.
- Test de mémorisation terminé sur les 9 zones réservées.
- Faits prêts pour tes deux messages Discord : `docs/DISCORD-FAITS.md`.

## Ce qu'il faut savoir

1. **La méthode visée est déjà publiée pour les trois objets les plus utiles.** Priyank Aranke a mis en ligne
   environ 250 cm² d'étiquettes corrigées à la main sur PHerc0814, 0841 et 0009B, avec code et modèle. On ne les
   refait pas.
2. **Ce qui reste libre est étroit.** On ne peut corriger à la main que là où la carte du modèle 2 µm est
   lisible. Sur les couches cachées de PHerc0343P, elle ne montre que des taches : inutilisable.
3. **Cible de départ : PHerc0500P2**, ses 8 couches numérotées. La carte 2 µm y montre des lignes de lettres, et
   7 couches n'ont aucune étiquette humaine à ~9 µm. La 8e (`--1`), annotée par l'équipe, servira d'étalon.
   Aussi libres : son outil d'étiquetage (non publié) et la mesure du gain par heure de correction.
4. **Les 6 zones de validation cachées sont confirmées** : le checkpoint tardif y obtient un F1 de 0,44 à 0,74,
   contre 0,91 à 0,99 sur ses pixels d'entraînement. Elles sont aussi plus difficiles que les 3 masques publiés
   (AUC 0,83 contre 0,92), ce qui en fait une mesure plus honnête.

## Prochaine étape

- Étape 2 : pré-étiquettes pour les 8 couches de PHerc0500P2 (recalage, carte de reader-v3 à calculer).
- Étape 3 : l'appli au stylet, après vérification qu'aucun outil existant ne convient.
- Jalon : première séance de 20 minutes sur ta tablette le 29/11 (couche `--1`, en aveugle).

## Ce que j'attends de toi

- Écrire et poster les deux messages Discord (faits dans `docs/DISCORD-FAITS.md`).
- Me dire si la cible de départ (PHerc0500P2) te convient, ou attendre la réponse de l'équipe.
- Me dire si je peux pousser sur `main` comme la dernière fois. Pour l'instant tout est sur la branche
  `claude/jolly-shannon-2xycqz`.

## Kaggle

Aucun run lancé. Quota GPU restant : 28,6 h jusqu'au 28/11.
