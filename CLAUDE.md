# CLAUDE.md : vesuvius-ink-adapt

Projet de Jonathan (GitHub : Jonathan8520) pour le Vesuvius Challenge (lecture des rouleaux carbonisés d'Herculanum).

**Objectif du sprint :** une soumission aux **Progress Prizes de novembre 2026** (meilleure soumission du mois : 20 000 $).
**Date limite : 30 novembre 2026 à 23 h 59, heure du Pacifique** (1er décembre à 8 h 59 à Paris).

**État au 22 novembre 2026 : sprint arrêté par Jonathan.** Lire `docs/STATUS.md` avant toute chose. Ne pas
reprendre `docs/PLAN.md` ni lancer de calcul sans nouvelle consigne.

À lire avant toute chose :
1. `docs/HANDOFF.md` : ce qui est fait, ce qui marche, les chiffres de validation, les leçons.
2. `docs/PLAN.md` : le plan du sprint, jour par jour, avec les critères de réussite.
3. `docs/CONTEXT.md` : les règles du prix et ce que le jury favorise.
4. `docs/EXPERIMENTS.md` : le journal des expériences (à tenir à jour à chaque essai).

## Règles absolues

- **Commits** : auteur unique `Jonathan8520 <103694268+Jonathan8520@users.noreply.github.com>`.
  Jamais de ligne `Co-Authored-By` ni de lien `Claude-Session` dans les messages de commit.
- **Secrets** : le dépôt est public. Aucun token ni mot de passe dans le code, les notebooks, les logs ou les docs.
  Kaggle : variable `KAGGLE_API_TOKEN` ou fichier `~/.kaggle/access_token`, toujours hors dépôt.
- **Règle First Letters** : si des lettres apparaissent sur un rouleau éligible au prix First Letters, ne rien
  committer ni publier (images, coordonnées, noms de segments). Le règlement interdit de rendre une découverte
  publique avant l'annonce officielle. Garder ces résultats hors du dépôt et prévenir Jonathan.
- **Licences** : données CT sous CC BY-NC 4.0 (citer « Vesuvius Challenge - CT Scans of Herculaneum Papyri » ou
  « EduceLab-Scrolls » selon le scan) ; poids `scrollprize/ink_9um` sous licence MIT ; notre code sous MIT.
- **Communication avec Jonathan** : en français, direct, sans tirets cadratins. Il lit souvent sur téléphone :
  réponses courtes, images utiles plutôt que longs tableaux.

## Méthode de travail

- **Chercher avant de coder.** Avant chaque étape et avant toute nouvelle idée, faire l'état de l'art sur
  Internet : site et blog du challenge (scrollprize.org, page des lauréats, scrollprize.substack.com), dépôt
  ScrollPrize/villa (code, tickets « help wanted », pull requests, `ink-detection/configs/README.md`),
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
- **Validation** : `python tests/validate_against_official.py` doit afficher `VALIDATION OK`
  (rendu ≈ 0,93 ; encre ≈ 0,9999 sur la grille officielle, écart maximal de 1 niveau sur 255).
  À relancer après toute modification de `core.py`.

## Où sont les données

- Bucket public : `s3://vesuvius-challenge-open-data/`, lisible en HTTPS sans compte :
  https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/ (listing S3 avec `?list-type=2&prefix=...`).
- Volumes éligibles aux prix : `scrollprize.org/src/data/prizeEligibility.json` dans le dépôt ScrollPrize/villa.
- Étiquettes d'encre 9 µm (dont les 9 segments réservés à la validation) : bucket Hugging Face
  `scrollprize/datasets`, dossier `ink_9um/` (API : https://huggingface.co/api/buckets/scrollprize/datasets/tree/ink_9um).
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
