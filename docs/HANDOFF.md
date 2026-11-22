# Passation : état au 23 novembre 2026

## En bref

- **Le sprint Progress Prizes de novembre est arrêté** (décision de Jonathan, 22/11) : tout le plan avait déjà été
  publié par d'autres. Raisons ci-dessous.
- **Nouveau cap, le même soir** : publier d'ici le 31 décembre des étiquettes d'encre vérifiées à la main par
  Jonathan, avec la preuve qu'elles améliorent un modèle, puis viser First Letters. Voir `docs/PLAN.md`.
- **Fait pour ce cap** : vérification d'antériorité en quatre balayages (`docs/RESEARCH.md`, section 10),
  inventaire (`docs/INVENTAIRE.md`), test de mémorisation sur les 9 zones réservées, mesure de la carte du modèle
  2 µm contre les étiquettes humaines (A5), recalage du scan fin vers la surface 9 µm (A7), banc de mesure par
  affinage (données, affineur, script Kaggle), faits pour Discord (`docs/DISCORD-FAITS.md`).
- **Cible révisée** : PHerc0500P2, couches `0` à `4` (les seules sans étiquette humaine). `--1` sert d'étalon.
- **Ce qui reste utilisable de novembre** : une chaîne `ink_9um` validée contre les outils officiels, un lecteur
  des données publiques, des notes de recherche à jour.
- **Calcul** : jeu Kaggle privé `jonathan8520/vesuvius-ink9um-bench` (tuiles et zones du banc, 3,7 Go) ; état des
  runs dans `docs/STATUS.md`.
- À lire : `docs/STATUS.md` (court), `docs/PLAN.md`, `docs/RESEARCH.md` (sections 9 et 10 pour les étiquettes).

## Pourquoi le sprint de novembre a été arrêté

| Étape de l'ancien plan | Déjà fait par | Résultat |
| --- | --- | --- |
| E3, score de référence d'`ink_9um` | DomRusso2/ink9um-dense, khj1222 (docs/14), inkbench, gowtham012 | 14 checkpoints notés sur les 3 masques publiés |
| E4, profondeur sans étiquette | tarikcankorkmaz00, LynnHenry/offset-sweep, villa #1867 | ne bat pas la fenêtre fixe ; oracle à +0,01 |
| E5, TENT | khj1222 (docs/18) | −0,041 de F1, 14 cas sur 14 dégradés |
| E5, ensembles | inkbench, gowtham012 (soumis le 21/11), option `--ensemble-checkpoint` de villa | publié au moins trois fois |
| E5, adaptation sans étiquette à un rouleau cible | TAUIL-Abd-Elilah/ink-adapt-9um, PR villa #2512 | pas mieux que l'ensemble ; créneau pris |
| E6, chaîne sans C++ | ink-cpu, ink-sdk, inkrs, vesuvius-pipeline, villa-apple-silicon | au moins sept dépôts |
| E7, rouleaux non lus | first-letters-survey, spiral-tracks-four-scrolls, fil « 57 bands on 19 unread scrolls » | criblage déjà fait, rien de lisible |

Autres raisons :

- La référence à 9 µm est reader-v3 (Domenico Russo, MIT), plus `ink_9um`. Sur le segment w00 de PHerc0841,
  rouleau jamais vu, les cartes publiées par l'équipe montrent des lignes de lettres avec reader-v3 et argus-v3,
  et presque seulement du bruit avec `ink_9um`.
- First Letters sur PHerc. 1203 est déjà travaillé par des équipes mieux équipées, y compris avec le scan à
  2,4 µm (constat de Jonathan). Notre balayage E2 des 22 surfaces n'avait rien montré.
- Le jury décourage les outils d'évaluation isolés ; sur cet axe les prix vont de 250 à 1 000 $. Le mainteneur
  bruniss refuse les contrôles automatiques de « formes d'encre » (PR villa #2318 et #2349).
- Règle du Discord (#rules, 29/07/2026) : pas de message généré par IA à la place de sa propre participation,
  sauf dans #robots avec une ligne « AI disclosure ».

## Ce qui marche, et comment on l'a vérifié

Test reproductible : `python tests/validate_against_official.py` (segment public PHerc. 211, environ 1 min sur CPU).

| Élément | Vérification | Résultat |
| --- | --- | --- |
| Modèle `ink_9um` réimplémenté et inférence `core.infer_roi` | contre la prédiction officielle publiée (seed43, step 20k), zone 0:1720 × 4000:4500 | r = 0,9999, écart maximal 1 niveau sur 255 |
| Rendu `core.render` | contre la surface officielle (`vc_render_tifxyz`), 28 couches | r moyen 0,933 (min 0,871), non corrigé |
| Lecteur `zarrio.RemoteArray` | Zarr v2 brut (surfaces S3), Zarr v2 Blosc (étiquettes HF), Zarr v3 shardé (étiquettes S3) | lectures cohérentes entre elles (IoU 0,96 à 0,99 entre les étiquettes d'encre HF et S3) |
| Entrée « 2,4 µm réduite à 21 couches » + inférence + métriques | contre les chiffres publiés par Domenico Russo (s43-75k) | w016 : 0,810 et 0,937 (publié 0,810 et 0,937) ; 0814 : 0,773 et 0,863 (publié 0,772 et 0,863) |
| Recalage du scan fin vers la surface ~9 µm (`register.py`) | texture CT ; report indépendant de jeff-j-chen sur PHerc0500P2 `--1` ; étiquettes de l'équipe publiées dans les deux repères (PHerc0139, 5 segments) | résidu médian 0,3 à 0,8 px ; IoU 0,992 ; IoU 0,956 à 0,986 |
| Banc de mesure (`build_bench.py`, `finetune.py`, `run_bench.py`) | notation du checkpoint s43-75k sur les zones du banc, sur CPU | w016 : 0,8100 / 0,7200 / 0,9365 ; 0814 : 0,7731 / 0,7124 / 0,8628 (identiques à l'audit) |
| Audit des masques (`scripts/audit_reserved_validation.py`) | contre l'audit de khj1222 (docs/17) sur les 3 masques publiés | 59,3 %, 45,0 %, 23,2 % à moins d'un patch (publié : 58,6 %, 45,0 %, 23,2 %) |

Ce qui a changé le 22/11 au soir :

- **L'écart de 0,91 est expliqué.** L'outil officiel pose ses tuiles sur la grille globale de la surface (0, 64,
  128, ..., plus une tuile alignée sur le bord). Notre test recadrait hors de cette grille. `core.infer_roi`
  imite l'officiel ; `core.infer` reste valable sur une surface entière.
- **Le rendu à 0,93 a une explication probable, non vérifiée** : `vc_render_tifxyz` centre ses couches sur
  (N − 1) / 2 (28 couches : −13,5 à +13,5, pas −14 à +13), prend le centre du pixel et interpole la surface en
  bicubique. D'autres rendus Python atteignent 0,9999 avec ces conventions (AndreasHad04/villa-apple-silicon).
- `imagecodecs` ajouté aux dépendances (les TIFF officiels sont compressés en LZW).

## Les 9 zones de validation réservées (nos données de mesure)

Les checkpoints `ink_9um` déclarent 9 `reserved_validation_cases`. Les sources que nous avons lues (veille de
Jonathan, 25 dépôts) écrivent toutes que seuls 3 masques de validation sont tenus à l'écart (0,66 cm²), et
plusieurs montrent qu'ils sont collés aux pixels d'entraînement.

Ce que nous avons mesuré sur les masques publics (aucun modèle) :

- Les 9 cas ont chacun une zone réservée. Le dépôt 9 µm (Hugging Face, `ink_9um/`) ne publie le masque que pour
  3 cas. Les 6 autres zones sont publiques dans le repère 2,4 µm : dossier `ink/` du même bucket
  (`*_validation_mask_v2.tif`, depuis le 07/07/2026, recensés par nestorvfx le 24/09) et S3
  (`<segment>/ink-labels/<volume 2,4 µm>/20260918/validation.zarr`, niveau 2, même repère que les étiquettes
  9,6 µm). Ce n'est donc pas une découverte de masques : ce qui manque, c'est leur version dans `ink_9um/labels`.
- Ces 6 zones n'ont **aucun pixel commun** avec les masques de supervision d'entraînement publiés. Elles pèsent
  3 818 877 px (3,52 cm²) contre 721 550 px (0,66 cm²) pour les 3 masques publiés, soit 5,3 fois plus.
- Elles sont **loin des pixels d'entraînement** : 0 à 9 % de leurs pixels à moins de 256 px d'un pixel
  d'entraînement, contre 45 à 99 % pour les 3 masques publiés.
- Les étiquettes d'encre du dépôt 9 µm couvrent déjà ces zones. Il ne manque que le fichier de masque.
- Le jumeau natif du cas pherc0139-w028 (segment w044) ne couvre pas sa zone réservée.

Test de mémorisation (checkpoint s43-75k, fenêtre centrée, sens direct), terminé le 22/11 sur les 9 cas.
Un checkpoint tardif retrouve presque parfaitement ses pixels d'entraînement ; une zone jamais vue reste bien
en dessous. Colonnes : précision équilibrée à 0,5 / F1 à 0,5 / AUC.

| Cas | Masque publié à 9 µm ? | Zone réservée | Pixels d'entraînement du même segment |
| --- | --- | --- | --- |
| pherc0139-w016 | oui | 0,810 / 0,720 / 0,937 | 0,975 / 0,955 / 0,994 |
| pherc0814-46527 | oui | 0,773 / 0,712 / 0,863 | 0,992 / 0,988 / 0,9998 |
| pherc1667-w029 | oui | 0,838 / 0,758 / 0,930 | 0,989 / 0,983 / 0,9996 |
| pherc0139-w028 | non (S3) | 0,731 / 0,610 / 0,841 | 0,989 / 0,980 / 0,9995 |
| pherc0139-w029 | non (S3) | 0,783 / 0,700 / 0,879 | 0,936 / 0,911 / 0,976 |
| pherc1667-w018 | non (S3) | 0,734 / 0,600 / 0,830 | 0,944 / 0,909 / 0,986 |
| pherc1667-w023 | non (S3) | 0,643 / 0,439 / 0,769 | 0,980 / 0,966 / 0,998 |
| pherc1667-w028 | non (S3) | 0,818 / 0,737 / 0,926 | 0,992 / 0,987 / 0,9996 |
| pherc1667-w031 | non (S3) | 0,687 / 0,539 / 0,810 | 0,986 / 0,976 / 0,9992 |

Lecture : les 6 zones non publiées ont le score d'une zone jamais vue (F1 de 0,44 à 0,74, AUC de 0,77 à 0,93),
très loin des pixels d'entraînement des mêmes segments (F1 de 0,91 à 0,99). En moyenne pondérée par pixel, l'AUC
vaut 0,83 dans les 6 zones non publiées contre 0,92 dans les 3 zones publiées : les zones isolées de
l'entraînement sont plus difficiles. C'est un indice de fuite sur les 3 masques publiés, pas une preuve (ce ne
sont pas les mêmes zones).

Contrôle : sur les 3 masques publiés, on retrouve les chiffres de Domenico Russo pour s43-75k (0,810 / 0,937,
0,772 / 0,863, 0,837 / 0,930 en précision équilibrée et AUC).

Limites à garder en tête :

- Un seul checkpoint testé (s43-75k). Les pixels d'entraînement sont un échantillon de 6 îlots au plus par segment.
- La recherche d'antériorité n'a rien trouvé dans les 25 sources lues, mais n'est pas exhaustive.
- Ces zones ne sont tenues à l'écart que pour la recette `ink_9um`. Les modèles distillés (reader-v2, reader-v3,
  hecate) ont appris sur des cartes couvrant des segments entiers.
- Elles restent dans des rouleaux vus à l'entraînement : ce n'est pas une mesure de généralisation entre rouleaux.
- Règle du projet : jamais d'étiquette ni d'entraînement dans ces 9 zones.

Reproduire : `python scripts/audit_reserved_validation.py` (masques seuls, quelques minutes sur CPU), puis
`--memo s43-75k` pour le test de mémorisation (environ 20 min sur CPU).

## Ce qu'on a appris d'autre

- **Chercher avant de coder.** Le plan du sprint a été écrit avant la veille. Une soirée de lecture (Discord,
  GitHub, 25 dépôts) l'a invalidé. La règle est maintenant dans `CLAUDE.md`.
- **Les 9 segments « réservés » sont dans la liste d'entraînement** des checkpoints. Un score dans leur masque de
  supervision mesure la mémorisation.
- **Des étiquettes publiques existent sur des rouleaux jamais vus par `ink_9um`** : PHerc0841 (3 segments),
  PHerc0009B, PHerc0500P2, PHerc1447, MAN5. La communauté les utilise déjà. Chemins dans `docs/RESEARCH.md`.
- **Défaut de données connu et non corrigé** (ticket villa #2107) : dans le bucket Hugging Face, dossier `ink/`,
  18 volumes sur 33 ont des niveaux réduits tronqués en profondeur. Les surfaces du bucket S3 sont saines.
- **Bruit de mesure** : 0,02 à 0,13 entre les deux graines sur les 3 masques publiés. Beaucoup de gains publiés
  sont en dessous.

## Leçons pratiques

- **Kaggle** : le GPU et Internet exigent un numéro de téléphone vérifié. File d'attente GPU de 6 h 30 le dimanche
  après-midi. Statuts QUEUED, RUNNING, COMPLETE ou ERROR ; `kaggle quota` donne le quota restant. La ligne de
  commande n'a pas de commande d'annulation (commandes : list, files, get, init, push, pull, output, status,
  logs, update, delete, topics) : un run en cours s'annule sur le site.
- **Lecture S3** : environ 100 Mo/s depuis une session cloud. Un bloc de surface 2,4 µm au niveau 2 pèse 1,8 Mo.
- **Hugging Face** : lister d'abord (l'API `tree` donne la taille et l'empreinte de chaque chunk), ne télécharger
  que les chunks non vides. 120 000 fichiers listés en 9 s.
- **GitHub** : l'API est fermée pour ScrollPrize/villa dans une session cloud. Le dépôt se clone en lecture
  seule ; les tickets et PR se lisent par leurs pages web.
- **Mémoire** : une session partage 15 Go entre toutes ses tâches. Une transformée de distance sur un segment
  entier de PHerc. 1667 (260 millions de pixels) la sature : travailler par îlot.
- **Agents en parallèle** : 2 à la fois au plus sur une machine à 4 coeurs.
- **Mémoire, encore** : trois calculs lourds en même temps font tuer le plus gros (15 Go partagés). Lire les
  volumes par bandes ; un chunk de surface contient tous les plans.
- **Code d'autrui** : la session ne peut pas exécuter le code d'un dépôt cloné (refus de l'environnement, à
  raison). L'entraîneur de l'équipe demande en plus Python 3.14 et des modules C++ hors PyPI. D'où notre affineur.
- **Jeu Kaggle privé** : `kaggle datasets create -p <dossier> -r tar` envoie 3,7 Go en 2 minutes. Les commandes
  `datasets files` répondent 403 avec notre jeton ; `datasets status` et `datasets list --mine` marchent.
- **Dépôts tiers à contenu sensible** : cloner sans les blobs (`--filter=blob:none --no-checkout`), lister avec
  `git ls-tree -r --name-only` (sans `-l`, qui télécharge tout), et ne lire que les fichiers nécessaires.

## Fichiers

- `vesuvius_ink_adapt/core.py` : lecture du scan, rendu, modèle, inférence (`infer`, `infer_roi`). Source de vérité.
- `vesuvius_ink_adapt/zarrio.py` : lecture de tableaux Zarr distants (v2 brut ou Blosc, v3 shardé), listing du
  bucket Hugging Face.
- `vesuvius_ink_adapt/evalset.py` : segments étiquetés publics, étiquettes, découpage en zones, entrées réduites
  à 21 couches. **Expérimental.**
- `vesuvius_ink_adapt/register.py`, `scripts/register_fine_to_native.py` : recalage affine du canevas du scan
  fin vers le canevas natif ~9 µm, sur la texture CT ; fonctions de report d'images entre les deux.
- `scripts/teacher_vs_team.py` : carte du modèle 2 µm contre étiquettes de l'équipe (A5).
- `scripts/build_bench.py` : tuiles d'entraînement (corpus de l'équipe et segments nouveaux, deux versions
  d'étiquettes) et zones d'évaluation du banc.
- `vesuvius_ink_adapt/finetune.py`, `scripts/run_bench.py`, `kaggle/bench/` : affinage court d'`ink_9um`,
  notation, branches `base`, `C`, `T`, `H`, et script Kaggle.
- `app/index.html` : l'appli d'étiquetage au stylet (page statique). Publiée en artifact privé
  https://claude.ai/artifact/KkqKvAT9n2jTRyAqYhKrh9 (seul Jonathan peut l'ouvrir), avec le lot `etalon-m1` ; ses
  étiquettes arrivent dans la base de l'artifact, collection `etiquettes`.
- `scripts/make_prelabels.py`, `scripts/make_app_tiles.py`, `scripts/read_app_labels.py` : cartes de
  pré-étiquettes sur le canevas natif, tuiles de l'appli, relecture et score des étiquettes rendues.
- `scripts/audit_reserved_validation.py` : audit des zones réservées et test de mémorisation.
- `scripts/inventory.py` : inventaire des scans, surfaces, cartes d'encre et étiquettes publiées, écrit
  `docs/INVENTAIRE.md`.
- `scripts/build_evalset.py` : construction de zones d'évaluation. **Expérimental**, essayé sur deux segments.
- `scripts/` (autres) : outils CPU d'origine (listing S3, rendu CPU, inférence CPU).
- `kaggle/vesuvius_pherc1203_sweep.py` : script du balayage E2. Il n'a pas `infer_roi` et n'en a pas besoin
  (surfaces entières).
- `tests/validate_against_official.py` : la validation ci-dessus.

## Pistes notées, hors du plan actuel

- Tickets ouverts de villa repérés et non étudiés : #1481 (zéros de remplissage dans la normalisation robuste de
  l'inférence), #1845 (maillage grossier, −0,04 d'AUC), #2627 (profondeur inversée du modèle 2,4 µm).
- Corriger les conventions du rendu (centre du pixel, couches centrées sur (N − 1) / 2) et relancer la validation.

## Comptes et accès

- **Kaggle** : compte `jonathan8520`. Aucun run lancé le 22/11 au soir. Quota GPU restant : 28,6 h jusqu'au
  28/11 à 00 h UTC. Le token se fournit par variable d'environnement, jamais dans le dépôt.
- **Notebooks Kaggle existants** (privés, terminés) : `jonathan8520/vesuvius-pherc1203-ink-sweep` (GPU) et
  `jonathan8520/vesuvius-pherc1203-ink-sweep-cpu` (CPU).
