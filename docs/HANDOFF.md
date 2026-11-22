# Passation : état au 22 novembre 2026 (soir)

## En bref

- **Chaîne complète validée** : reconstruction de surface (rendu `tifxyz`) et modèle d'encre `ink_9um`,
  sans dépendances C++, sur CPU ou sur GPU (Kaggle).
- **Deux rouleaux éligibles explorés, rien de lisible** : PHerc. 0800 (prédictions publiées par l'équipe) et
  PHerc. 1203 (notre balayage complet des 22 surfaces brutes).
- **Prochaine étape** : expérience E3, score de référence sur les 9 segments réservés à la validation
  (voir `docs/PLAN.md`).

## Ce qui marche, et comment on l'a vérifié

Test reproductible : `python tests/validate_against_official.py` (segment public PHerc. 211 « crop1711-lines123-v9 »).

| Élément | Vérification | Résultat |
| --- | --- | --- |
| Rendu `core.render` | contre la surface officielle (`vc_render_tifxyz`), zone 600:856 × 4400:4656, 28 couches | r moyen 0,933 (min 0,871) |
| Modèle `ink_9um` réimplémenté | contre la prédiction officielle publiée avec le même checkpoint (seed43, step 20k), zone 0:1720 × 4000:4500 | r = 0,912 |
| Version CPU contre version GPU du code | même entrée | r = 1,0 |
| Normalisation torch contre numpy | patchs réels | écart max 2,4e-7 |

L'écart restant (0,91 au lieu de 1,0) vient probablement de détails de l'inférence officielle que nous ne
reproduisons pas exactement (précision mixte, bords et découpage des tuiles, quantification 8 bits du TIFF publié).
Il ne change pas la lecture des cartes.

## Explorations faites (détails dans `docs/EXPERIMENTS.md`)

- **E1, PHerc. 0800** (éligible) : 6 segments `auto_grown` publiés avec leurs surfaces et les prédictions de
  3 modèles (ink9um s43-20k, reader-v3, argus-v3). Résultat : taches d'environ 1 mm, aucun trait, aucune ligne.
- **E2, PHerc. 1203** (éligible) : 22 surfaces brutes publiées (`segments/raw/auto_grown_*`, uniquement des
  `tifxyz`, aucun rendu publié). Rendues par nous puis 10 passages chacune : s43-20k (fenêtres 3, 6, 9),
  s43-60k (fenêtre 6), s42-75k (fenêtre 6), dans les deux sens. Environ 120 cm² avec recouvrements,
  83 min sur un T4, 24,5 Go lus. Résultat : bruit uniforme ; les 4 fenêtres les plus contrastées sont des faux
  positifs (zones écrasées où la surface saute d'une couche à l'autre, bords de morceaux, trous).
- **Calibrage** : sur PHerc. 211, reader-v3 et argus-v3 montrent des lettres nettes ; ink9um (s43-20k) donne une
  carte plus bruitée sur la même zone.

## Leçons pratiques

- **Kaggle** : le GPU et Internet exigent un numéro de téléphone vérifié. Sans lui, la session tourne sans GPU
  ni réseau, sans message d'erreur clair (échec DNS dans le log).
- **File d'attente GPU** : 6 h 30 d'attente le dimanche 22/11 après-midi. Lancer tôt, ou prévoir la version CPU.
- **Suivi** : statuts QUEUED, RUNNING, COMPLETE ou ERROR ; `kaggle quota` donne le quota restant ;
  les logs ne sont lisibles qu'à la fin du run.
- **Lecture S3** : environ 1 Go lu par 5 cm² de surface rendue (chunks 128³ non compressés) ; un cache LRU de
  3000 chunks en mémoire suffit si on traite les surfaces voisines à la suite.
- Le script principal s'arrête désormais s'il n'a pas de GPU (sécurité ajoutée après le premier échec).
- La liste des souhaits de l'équipe (tickets « help wanted » de ScrollPrize/villa) n'était pas lisible depuis la
  session cloud précédente : la consulter via l'API GitHub ou un navigateur.

## Fichiers

- `vesuvius_ink_adapt/core.py` : le coeur, source de vérité.
- `kaggle/vesuvius_pherc1203_sweep.py` : script autonome lancé sur Kaggle (copie du coeur et boucle principale).
  À garder synchronisé avec `core.py`.
- `scripts/` : outils CPU (listing S3, rendu CPU avec scipy, inférence CPU).
- `tests/validate_against_official.py` : la validation ci-dessus.

## Comptes et accès

- **Kaggle** : compte `jonathan8520`, quota GPU de 30 h par semaine (environ 28,5 h restantes jusqu'au
  28/11 à 00 h UTC). Le token se fournit par variable d'environnement ou secret réseau, jamais dans le dépôt.
- **Notebooks Kaggle existants** (privés) : `jonathan8520/vesuvius-pherc1203-ink-sweep` (GPU, terminé) et
  `jonathan8520/vesuvius-pherc1203-ink-sweep-cpu` (CPU, devenu inutile).
