# Plan du sprint : 23 au 30 novembre 2026

> **Sprint arrêté le 22 novembre 2026 (décision de Jonathan). Ce plan n'est plus à exécuter.**
> Les étapes E3 à E7 ont déjà été faites par d'autres, souvent avec un résultat négatif, et First Letters sur
> PHerc. 1203 est déjà travaillé par des équipes mieux équipées. Conclusion : `docs/STATUS.md`. Détail :
> `docs/VEILLE-2026-11-22.md`, `docs/RESEARCH.md`, `docs/HANDOFF.md`. Le texte ci-dessous est conservé pour mémoire.
> Attention : son hypothèse de départ est fausse. Les 9 segments « réservés » figurent dans la liste
> d'entraînement des checkpoints ; seule une zone par segment est tenue à l'écart.

**But :** prouver un gain mesurable de détection d'encre sur des rouleaux que le modèle n'a jamais vus, sans
aucune annotation sur le rouleau cible, et le livrer sous forme d'outil utilisable sur un GPU gratuit.

Problèmes ouverts visés (page « 2026 Open Problems », tableau des blocages) : **Cross-scroll generalization**
et **Data scale**.

## Métrique

- **Précision équilibrée** (moyenne du rappel encre et du rappel non-encre), seuil 0,5 : c'est la métrique de
  sélection des checkpoints de l'équipe (`best_checkpoint_metric = val_balanced_accuracy`).
- En complément, sans seuil : AUC-PR et F0.5 sur les pixels annotés.
- Évaluer seulement dans `supervision_mask`, et dans `validation_mask` pour les 3 segments qui en ont un.

## Données d'évaluation

Segments réservés par l'équipe (`reserved_validation_cases` dans la config des checkpoints) :
`pherc0139-w016`, `w028`, `w029` ; `pherc0814-46527` ; `pherc1667-w018`, `w023`, `w028`, `w029`, `w031`.

- **Étiquettes** : bucket Hugging Face `scrollprize/datasets`, dossier
  `ink_9um/labels/aligned-scrollprizeorg-21slices/<segment>/` (`_inklabels.zarr`, `_supervision_mask.zarr`,
  `_validation_mask.zarr`). 21 couches, annotées seulement à Z = 10.
- **Entrées** : surfaces à 2,399 µm sur S3 (chemins exacts dans `ink_9um/README.md` du bucket), à ramener à
  environ 9,6 µm : niveau 2 en XY puis moyenne de 4 couches en Z (comme `prepare_9um_isotropic_input.py`).
- Environ 900 millions de pixels au total : ne lire que les boîtes englobantes des zones annotées.
  `pherc1667-w018` fait à lui seul 10 595 × 24 525 px au niveau 2.

## Étapes

- [ ] **E3 (lundi 23 et mardi 24)** : score de référence du modèle officiel (s43-20k, fenêtre centrée, sens
      direct) sur les 9 segments. Vérifier d'abord l'alignement étiquettes / entrées en les superposant.
- [ ] **E4 (mercredi 25)** : choix de la profondeur sans étiquette, zone par zone. Critères à comparer :
      confiance moyenne, entropie, contraste de la carte. Comparer à la fenêtre fixe et à la moyenne des fenêtres.
- [ ] **E5 (jeudi 26)** : adaptation au moment du test sans étiquette (par exemple ajuster les paramètres
      affines des InstanceNorm en minimisant l'entropie, à la manière de TENT) ; ensembles de checkpoints.
- [ ] **E6 (vendredi 27)** : publication. README avec les chiffres, notebook Kaggle public, message Discord
      rédigé pour Jonathan.
- [ ] **E7 (samedi 28 et dimanche 29)** : appliquer la meilleure méthode aux rouleaux non lus (PHerc. 0800,
      1203, etc.) **en privé** (règle First Letters), figures, documentation.
- [ ] **Soumission** : formulaire des Progress Prizes avant le 30/11 à 23 h 59 heure du Pacifique.

## Critères de réussite

- Gain net sur au moins 2 des 3 rouleaux réservés (0139, 0814, 1667) par rapport à la fenêtre fixe.
- Gain qui tient avec les deux graines (seed42 et seed43).
- Sans gain : soumettre quand même la chaîne (rendu et modèle sans C++, GPU gratuit) au titre du blocage
  « Data scale ».

## Idées en réserve

- Pseudo-étiquettes sur le rouleau cible à partir des zones les plus confiantes, puis réentraînement court.
- Utiliser le scan à 2,4 µm de PHerc. 1203 (volume 20260319130212) pour repérer l'encre, puis vérifier sur le
  volume éligible à 9,362 µm (20250820131727).
- Proposer l'amélioration directement à l'équipe (pull request sur ScrollPrize/villa) si elle s'intègre dans
  leur `infer.py`.
