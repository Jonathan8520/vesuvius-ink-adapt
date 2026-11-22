# CLAUDE.md : vesuvius-ink-adapt

Projet de Jonathan (GitHub : Jonathan8520) pour le Vesuvius Challenge (lecture des rouleaux carbonisés d'Herculanum).

**Objectif (cap du 22 novembre 2026) :** publier d'ici le **31 décembre 2026** des étiquettes d'encre vérifiées à
la main par Jonathan, avec la preuve qu'elles améliorent un modèle, pour la soumission aux **Progress Prizes de
décembre**. Ensuite, utiliser ce modèle pour **First Letters** (50 000 $ par rouleau, jusqu'au 25 juin 2027).

**Répartition :** Jonathan donne 3 à 5 heures par semaine de correction au stylet sur sa tablette Android
(Galaxy Tab S6 Lite). La session fait tout le reste : données, pré-étiquettes, appli, export, entraînement, mesure.

Le sprint de novembre (adaptation sans étiquette d'`ink_9um`) a été arrêté le 22 novembre : tout avait déjà été
publié par d'autres. Ne pas le reprendre.

À lire avant toute chose :
1. `docs/STATUS.md` : le point le plus récent, court.
2. `docs/PLAN.md` : le cap, les étapes, les jalons et les critères d'arrêt.
3. `docs/INVENTAIRE.md` : rouleaux, scans et étiquettes d'encre déjà publiées (régénéré par `scripts/inventory.py`).
4. `docs/RESEARCH.md` : état de l'art (qui a fait quoi), à compléter avant chaque étape.
5. `docs/HANDOFF.md` : ce qui marche, comment c'est vérifié, les leçons.
6. `docs/EXPERIMENTS.md` : le journal des expériences (à tenir à jour à chaque essai).
7. `docs/DISCORD-FAITS.md` : faits préparés pour les messages que Jonathan écrit lui-même.
8. `docs/CONTEXT.md` (règles des prix) et `docs/VEILLE-2026-11-22.md` (veille de Jonathan).

## Règles absolues

- **Commits** : auteur unique `Jonathan8520 <103694268+Jonathan8520@users.noreply.github.com>`.
  Jamais de ligne `Co-Authored-By` ni de lien `Claude-Session` dans les messages de commit.
- **Secrets** : le dépôt est public. Aucun token ni mot de passe dans le code, les notebooks, les logs ou les docs.
  Kaggle : variable `KAGGLE_API_TOKEN` ou fichier `~/.kaggle/access_token`, toujours hors dépôt.
- **Jamais d'étiquettes sur un rouleau éligible à First Letters** (liste : `prizeEligibility.json` de villa,
  reprise en tête de `docs/INVENTAIRE.md`). Ni annotation, ni correction, ni pré-étiquette publiée.
- **Jamais d'étiquette ni d'entraînement dans les 9 zones de validation réservées d'`ink_9um`**, quelle que soit
  la représentation (2,4 µm réduit ou natif) : ce sont nos données de mesure.
- **Règle First Letters** : si des lettres apparaissent sur un rouleau éligible au prix First Letters, ne rien
  committer ni publier (images, coordonnées, noms de segments). Le règlement interdit de rendre une découverte
  publique avant l'annonce officielle. Garder ces résultats hors du dépôt et prévenir Jonathan.
- **Licences** : données CT sous CC BY-NC 4.0 (citer « Vesuvius Challenge - CT Scans of Herculaneum Papyri » ou
  « EduceLab-Scrolls » selon le scan) ; poids `scrollprize/ink_9um` sous licence MIT ; notre code sous MIT.
- **Discord** : aucun message rédigé par la session. Elle prépare les faits et les chiffres dans
  `docs/DISCORD-FAITS.md`, Jonathan écrit et poste lui-même (règle du serveur du 29/07/2026 ; dans #robots,
  ajouter une ligne « AI disclosure »).
- **Communication avec Jonathan** : en français, direct, sans tirets cadratins. Il lit souvent sur téléphone :
  réponses courtes, images utiles plutôt que longs tableaux.

## Méthode de travail

- **Chercher avant de coder.** Avant chaque étape et avant toute nouvelle idée, faire l'état de l'art sur
  Internet : site et blog du challenge (scrollprize.org, page des lauréats, scrollprize.substack.com), dépôt
  ScrollPrize/villa (code, tickets « help wanted », pull requests, `vesuvius/docs/ink_detection.md`),
  Hugging Face `scrollprize`, solutions publiées des compétitions Kaggle Vesuvius (Ink Detection 2023,
  Surface Detection 2026), arXiv (préprint 2606.29085 sur les scans 2026, littérature sur l'adaptation au
  moment du test), dépôts GitHub de la communauté. Ne jamais développer ce qui existe déjà : réutiliser le code
  sous licence permissive en le citant.
- Noter chaque trouvaille utile dans `docs/RESEARCH.md` : lien, ce que ça apporte, ce qu'on en fait.
- La page Open Problems signale qu'un essaim d'agents autonomes (inspiré de karpathy/autoresearch) a déjà fait
  progresser la généralisation d'un rouleau à l'autre : trouver ce qui a été fait et s'en démarquer.
- **Autonomie.** Avancer sans attendre Jonathan : décider, justifier la décision dans les docs, continuer.
  Ne le solliciter que pour : (1) Discord, qu'il lit et où il poste lui-même ; (2) le formulaire de soumission ;
  (3) toute découverte de lettres (règle First Letters) ; (4) toute action irréversible ou payante, ou
  l'usage d'un compte qui n'est pas le sien.
- **Calcul.** Lancer les runs GPU Kaggle le plus tôt possible et préparer la suite pendant l'attente ; préparer
  les données d'évaluation une seule fois dans un dataset Kaggle privé ; garder une version CPU de secours.
- **Compte rendu.** Tenir `docs/EXPERIMENTS.md` à jour à chaque essai et, en fin de journée, écrire un point
  court dans `docs/STATUS.md`, lisible sur téléphone : fait, résultats, prochaine étape, besoins éventuels.

## Conventions techniques validées (ne pas modifier sans relancer la validation)

- **Rendu tifxyz** : pixel (r, c) ↔ grille (r·scale, c·scale), interpolation bilinéaire ;
  normale = −cross(∂/∂col, ∂/∂row) (signe de `vc_render_tifxyz`) ; 28 couches aux décalages −14..13
  (indice 14 = surface) ; échantillonnage trilinéaire du volume en ordre (z, y, x).
- **Modèle** `ink_9um` (pile 3D de fusion en profondeur + U-Net 2D à encodeur résiduel) réimplémenté dans
  `vesuvius_ink_adapt/core.py` ; poids chargés avec `weights_only=True` puis `strict=True`
  (les clés `.all_modules.` sont des doublons et sont ignorées).
- **Inférence** : fenêtre de 17 couches (centrée : couches 2..18 sur 21, 6..22 sur 28, 7..23 sur 31),
  normalisation robuste par patch (clip p1/p99, médiane, 1,4826·MAD), patchs 128, pas 64, fusion par fenêtre de
  Hann, sigmoïde. Affichage conseillé par l'équipe : (p − 0,25) / 0,5.
- **Grille des tuiles** : l'outil officiel pose ses tuiles sur la grille globale de la surface entière (0, 64,
  128, ..., plus une dernière tuile alignée sur le bord) et n'ignore que les tuiles entièrement vides. Pour
  calculer une zone, utiliser `core.infer_roi` (identique à l'officiel) ; `core.infer` part du coin du tableau
  qu'on lui donne et ne coïncide avec l'officiel que sur une surface entière.
- Le sens « direct » correspond aux rendus officiels ; sur nos propres rendus, tester aussi le sens inverse.
- **Report du scan fin vers la surface ~9 µm** : `index_fin = A @ index_natif + t`, `index_fin` au niveau 2 du
  volume fin, affine mesuré sur la texture CT (`vesuvius_ink_adapt/register.py`, sorties dans `data/register/`).
  L'échelle est le rapport des tailles de canevas, pas celui des tailles de voxel ; le décalage vaut 5 à 10 px.
- **Banc de mesure** : tuiles de 256 px (`scripts/build_bench.py`), affinage court d'`ink_9um`
  (`vesuvius_ink_adapt/finetune.py`, recette abrégée), branches `base`, `C`, `T`, `H` (`scripts/run_bench.py`).
  Contrôle : la branche `base` doit redonner 0,810 / 0,720 / 0,937 sur w016 avec s43-75k.
- **Code d'autrui** (villa et dépôts de la communauté) : on le lit et on le cite, on ne l'exécute pas dans la
  session.
- **Validation** : `python tests/validate_against_official.py` doit afficher `VALIDATION OK`
  (rendu ≈ 0,93 ; encre ≈ 0,9999 sur la grille officielle, écart maximal de 1 niveau sur 255).
  À relancer après toute modification de `core.py`.

## Où sont les données

- Bucket public : `s3://vesuvius-challenge-open-data/`, lisible en HTTPS sans compte :
  https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/ (listing S3 avec `?list-type=2&prefix=...`).
- Volumes éligibles aux prix : `scrollprize.org/src/data/prizeEligibility.json` dans le dépôt ScrollPrize/villa.
- Étiquettes d'encre 9 µm de l'équipe : bucket Hugging Face `scrollprize/datasets`, dossier `ink_9um/`
  (API : https://huggingface.co/api/buckets/scrollprize/datasets/tree/ink_9um).
- **Segments réservés** : les 9 `reserved_validation_cases` figurent dans la liste d'entraînement des
  checkpoints. Seule une zone par cas est tenue à l'écart. Le dépôt 9 µm publie le masque de 3 cas
  (0139-w016, 0814-46527, 1667-w029 : 0,66 cm²). Les 6 autres zones (0139-w028, w029 ; 1667-w018, w023, w028,
  w031 : 3,52 cm², loin des pixels d'entraînement) sont publiques dans le repère 2,4 µm : dossier `ink/` du
  bucket Hugging Face (`*_validation_mask_v2.tif`, depuis le 07/07/2026) et S3
  (`<segment>/ink-labels/<volume 2,4 µm>/20260918/validation.zarr`, niveau 2 = repère des étiquettes 9,6 µm).
  Trois d'entre elles (0139-w028, w029, 1667-w028) ont été supervisées par pseudo-étiquettes dans la lignée
  ink9um-dense (reader-v2, reader-v3, argus). Audit : `scripts/audit_reserved_validation.py`.
- Étiquettes 2,4 µm de l'équipe republiées sur S3 le 18/09/2026 : `<segment>/ink-labels/<volume>/20260918/`
  (`inklabels`, `supervision`, `validation`, Zarr v3 shardé, 2D, 6 niveaux).
- Étiquettes de la communauté : `paranke/vesuvius-814-841-9b-studio-training-data` (corrigées à la main, 0814,
  0841, 0009B), `domenicor046/reader-v2-labels` (sorties de modèle, 6 objets), voir `docs/INVENTAIRE.md`.
- Catalogue du bucket S3 : `metadata.json` à la racine (compressé en gzip) : scans, segments, surfaces, cartes
  d'encre et étiquettes par objet.
- Checkpoints : https://huggingface.co/scrollprize/ink_9um (seed42 et seed43, steps 10k à 75k).
- Code de référence de l'équipe : https://github.com/ScrollPrize/villa (dossiers `vesuvius/`, `vc_reader/`).

## Calcul

- Pas de GPU dans les sessions Claude : le calcul lourd passe par Kaggle (GPU T4, quota de 30 h par semaine sur
  le compte de Jonathan, téléphone vérifié, Internet activé).
- Lancer : copier `kaggle/kernel-metadata.example.json` en `kernel-metadata.json` dans le dossier à pousser,
  puis `kaggle kernels push -p <dossier>` ; suivre avec `kaggle kernels status`, récupérer avec
  `kaggle kernels output <id> -p <dossier> --file-pattern '<regex>'`.
- La file d'attente GPU peut durer plusieurs heures. Une version CPU démarre tout de suite (plus lente).
- Les logs Kaggle ne sont lisibles qu'à la fin d'un run : écrire un `log.txt` et un `resume.json` dans
  `/kaggle/working`.
