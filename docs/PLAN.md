# Plan : étiquettes d'encre vérifiées à la main (cap du 22 novembre 2026, révisé le 23/11)

Ce plan remplace celui du sprint de novembre, arrêté le 22/11 (ancien texte dans l'historique git, raisons dans
`docs/HANDOFF.md`). Révision du 23/11 : après la vérification d'antériorité approfondie (`docs/RESEARCH.md`,
section 10) et les mesures A5 à A7 (`docs/EXPERIMENTS.md`).

## But

1. **D'ici le 31 décembre 2026** : publier des étiquettes d'encre à ~9 µm vérifiées à la main par Jonathan, dans le
   format de l'équipe, avec la preuve chiffrée qu'elles améliorent un modèle. Soumission aux Progress Prizes de
   décembre (échéances mensuelles ; celle de novembre est le 30/11, celle de décembre est attendue le 31/12).
2. **Ensuite, jusqu'au 25 juin 2027** : utiliser le modèle obtenu pour First Letters (50 000 $ par rouleau).

Répartition : Jonathan corrige au stylet 3 à 5 heures par semaine sur sa tablette (Galaxy Tab S6 Lite), par
séances de 20 minutes. La session fait le reste.

## Ce que la vérification a montré

Détail et sources : `docs/RESEARCH.md`, sections 9 et 10.

**Déjà fait par d'autres :**

- Priyank Aranke : la méthode visée, sur PHerc0814, 0841 et 0009B (environ 260 cm², ses surfaces, son format).
- jeff-j-chen : étiquettes dessinées à la main en PNG sur les surfaces natives de l'équipe, dont trois couches de
  PHerc0500P2 (`front`, `--1`, `--2`) et le seul segment lisible de PHerc0343P. Clairsemées, sans fond certifié.
- L'équipe : PHerc0139 natif (5 segments), et, sur le scan fin seulement, PHerc0841, 0009B et 0500P2 `--1`.
- Le passage du scan fin à la surface 9 µm : formule exacte publiée (tifxyz-canvas-map) et outil de l'équipe.
- L'écart entre la carte du modèle 2 µm et les étiquettes humaines : consigné par l'équipe dans son catalogue.

**Pas fait, et vérifié par quatre balayages :**

1. Des étiquettes vérifiées à la main au format d'entraînement de l'équipe, sur ses surfaces natives publiques,
   pour un autre rouleau que PHerc0139.
2. Une comparaison d'entraînements : mêmes pixels, étiquettes humaines contre carte du modèle seule. C'est ce que
   le mainteneur de villa demande avant d'accepter un outil d'étiquetage (PR #2381).
3. Un outil d'étiquetage au stylet, et le temps de correction par cm².

**Ce que nos mesures ajoutent :**

- La carte du modèle 2 µm seuillée ne recouvre les étiquettes humaines qu'à 60 à 85 % (A5). La correction humaine
  a donc de la matière. Mais la plupart des désaccords sont hors de la « bande incertaine » 64 à 128.
- Le report du scan fin vers la surface 9 µm est réglé à moins d'un pixel (A7).
- Les 9 zones réservées d'`ink_9um` sont une bonne mesure pour la lignée `ink_9um` (A2).

**Ce qui joue contre nous :**

- Les comparaisons publiées donnent l'avantage à la quantité d'étiquettes (cartes denses du modèle) sur leur
  pureté. Le gain d'une correction humaine n'est donc pas acquis.
- Trois essais publics trouvent que les zones « incertaines » ne valent pas mieux que des zones au hasard.
- En 2026, l'équipe a primé des modèles (reader-v2, reader-v3), pas des jeux d'étiquettes, et décourage les outils
  d'audit seuls. Il faudra présenter un jeu de données et un modèle amélioré, mesuré sur les jeux publics.

## Règles

- Jamais d'étiquettes sur un rouleau éligible à First Letters (liste en tête de `docs/INVENTAIRE.md`). Par
  prudence, pas non plus sur PHerc1447 et PHerc0211, qui restent éligibles au Grand Prize (à confirmer par Jonathan).
- Jamais d'étiquette ni d'entraînement dans les 9 zones de validation réservées d'`ink_9um`, quelle que soit la
  représentation. PHerc0841 reste un jeu de mesure : ni étiquettes nouvelles, ni entraînement.
- Si des lettres apparaissent sur un rouleau éligible : rien dans le dépôt, prévenir Jonathan.
- Rien n'est copié du dépôt jeff-j-chen/HercUeNet en dehors de ses fichiers de PHerc0500P2, lus pour la mesure A6 :
  ce dépôt contient des étiquettes sur un rouleau éligible.
- Discord : la session prépare les faits (`docs/DISCORD-FAITS.md`), Jonathan écrit et poste.
- Licences : nos étiquettes sous CC BY-NC 4.0 (licence des scans), code sous MIT. Ne pas republier d'étiquettes
  dérivées de celles de l'équipe (reports sur le canevas natif, masques de validation) avant sa réponse sur la
  licence : son README renvoie à une ancienne licence qui restreint la redistribution.
- Code d'autrui : on le lit et on le cite, on ne l'exécute pas dans la session.
- Publier tôt : une première version du jeu et de l'appli dès qu'elles servent.

## Cible des étiquettes

On ne peut corriger à la main que là où la carte du modèle 2 µm est lisible (lignes et formes de lettres).

| Candidat | Étiquettes humaines existantes | Verdict |
| --- | --- | --- |
| **PHerc0500P2, couches `0`, `1`, `2`, `3`, `4`** (9,362 µm à 113 keV, scan fin à 2,215 µm) | aucune | **cible de production** |
| PHerc0500P2, couche `--1` | équipe (scan fin, 2,2 cm²), reprise par jeff-j-chen | **étalon** : première séance en aveugle |
| PHerc0500P2, couches `--2` et `front` | jeff-j-chen, clairsemées | plus tard : compléter en dense |
| PHerc0139 natif, 30 segments sans étiquette humaine | 5 segments de l'équipe | réserve, pour étaler sur beaucoup de segments |
| PHerc0343P, segment `20250511003658` | équipe (encre seule) et jeff-j-chen | écarté |
| PHerc0343P autres segments ; PHerc0500P2 `z_dbg_gen` | aucune, cartes illisibles | écartés |
| PHerc0814, 0009B, 0841 | Priyank Aranke | écartés (0841 : mesure seulement) |

Pourquoi PHerc0500P2 : cartes lisibles, même réglage de scan que 10 rouleaux éligibles, et `ink_9um` y est faible
(AUC 0,86 sur la partie annotée de `--1`, d'après ibarapascal/ink-disagree). Les couches `0` à `4`, `--1` et `--2` ne sont pas dans les étiquettes
de reader-v2, donc pas dans l'entraînement de reader-v3. À confirmer par la réponse de l'équipe (message n° 2).

## Étapes

- [x] **0. Vérification d'antériorité** (22 et 23/11).
- [x] **1. Inventaire** (22/11) : `scripts/inventory.py` → `docs/INVENTAIRE.md`.
- [ ] **2. Pré-étiquettes.**
      - [x] a. Tri de lisibilité (22/11).
      - [x] b. Recalage du scan fin vers la surface 9 µm : `scripts/register_fine_to_native.py`, résidu médian
            0,4 px sur les 8 couches de PHerc0500P2 (A7).
      - [x] c. Pré-étiquette : carte du modèle 2 µm reportée (`scripts/make_prelabels.py`, faite pour les 8
            couches), encre si ≥ 128, fond si ≤ 64 (le meilleur seuil mesuré sur `--1` est 121).
            Reste à faire : carte de reader-v3 pour comparaison.
      - [ ] d. Choix des tuiles : moitié par incertitude (confiance du modèle 2 µm), moitié au hasard parmi les
            tuiles qui contiennent de l'encre. On mesure laquelle sert le plus : c'est une question ouverte.
- [ ] **3. Appli web au stylet.** Version 0.1 écrite et essayée dans un navigateur de test (`app/index.html`,
      journal A9), publiée en page privée avec le lot d'étalonnage. Reste à faire : l'essai sur la tablette.
      Page statique sans serveur (rien d'existant ne convient) : canvas 2D
      et Pointer Events, le stylet peint, deux doigts déplacent, trois états (encre, fond, je ne sais pas),
      couches CT et carte du modèle à bascule, minuteur de 20 minutes, sauvegarde locale, export à chaque fin de
      séance, journal des traits (preuve de la vérification humaine et mesure du temps).
      Consigne reprise de l'équipe : ne valider que les traits nets et répétables, toujours avec du fond supervisé
      autour, laisser le douteux en « je ne sais pas ».
      Première séance : étalonnage en aveugle sur `--1`, pour chiffrer l'accord avec l'équipe.
- [ ] **4. Export au format de l'équipe.** Paire d'images `<segment>_inklabels.png` et
      `<segment>_supervision_mask.png` (0 ou 255, taille du canevas natif), puis Zarr v2 à la profondeur du volume
      de surface (28 plans, annotation au plan 14, 6 niveaux), relisible par l'entraîneur de villa ancien et
      récent. Manifeste de provenance sur le modèle des fiches du catalogue S3. Dépôt sur Hugging Face.
- [ ] **5. Mesure du gain.**
      - [x] a. Test de mémorisation sur les 9 zones réservées (A2).
      - [ ] b. **Pré-test sans Jonathan** : affinage d'`ink_9um` avec, sur les mêmes pixels de PHerc0009B et de
            PHerc0500P2 `--1`, soit les étiquettes humaines de l'équipe, soit la carte du modèle 2 µm seuillée,
            soit rien (témoin). Mesure sur les 9 zones réservées et sur PHerc0841. Au moins 3 graines.
            Données : `scripts/build_bench.py`. Affineur : `vesuvius_ink_adapt/finetune.py` (recette abrégée,
            la même pour toutes les branches).
            **Règle de lecture, écrite le 22/11 à 22 h 30 UTC, avant tout résultat :**
            - mesure principale : AUC au pas 1 000, écart `H − T` apparié par graine, moyenne sur les segments
              d'un groupe ; deux groupes : les 9 cas réservés (rouleaux vus) et PHerc0841 (rouleau jamais vu) ;
            - incertitude : bootstrap par blocs de 128 px (les mêmes blocs tirés pour toutes les branches) et
              par graines, 2 000 tirages, intervalle à 95 % ;
            - « l'humain fait mieux » : borne basse au-dessus de 0 sur au moins un groupe, et estimation non
              négative sur l'autre ; « la carte fait mieux » : l'inverse ; sinon « pas de différence mesurable » ;
            - contrôles : la branche `base` redonne les chiffres connus ; le témoin `C` ne perd pas plus de 0,02
              d'AUC par rapport à `base` (sinon la recette est trop brutale : relancer avec un taux plus bas) ;
            - lectures secondaires, sans poids dans la décision : précision équilibrée au seuil 0,5, écarts
              `H − C` et `T − C`, notations à 250 et 500 pas.
      - [ ] c. La même comparaison avec les étiquettes de Jonathan, tuiles « incertaines » contre tuiles au hasard.
      - [ ] d. Courbe du gain en fonction des heures de correction.
      - [ ] e. Si le gain est là : affiner reader-v3 avec ces étiquettes et mesurer sur PHerc0841 et PHerc1447
            (pour reader-v3, seules 3 des 6 zones réservées non publiées sont propres).

## Jalons

| Date | Jalon | Critère |
| --- | --- | --- |
| 24/11 | Messages Discord postés par Jonathan | faits prêts dans `docs/DISCORD-FAITS.md` |
| 27/11 | Résultat du pré-test (5b), avant la remise à zéro du quota Kaggle du 28/11 | écart entre branches et bruit entre graines chiffrés |
| 29/11 | Première séance de 20 minutes sur la tablette : `--1` en aveugle | l'appli charge, le stylet peint, l'export se relit, accord avec l'équipe chiffré |
| 06/12 | Version 0.1 publiée : appli, premières étiquettes d'une couche | relues par `create_label_zarrs` sans erreur |
| 13/12 | Première mesure avec les étiquettes de Jonathan | écart et bruit chiffrés |
| 20/12 | Couches `0` à `4` entamées toutes les cinq ; courbe gain par heure | |
| 27/12 | Jeu figé, documentation, notebook Kaggle public | |
| 31/12 | Soumission Progress Prizes par Jonathan : jeu, modèle affiné, mesure | |
| fin janvier | Bilan : gain mesurable ou arrêt | voir critères d'arrêt |

## Critères d'arrêt

- **L'équipe répond que ces étiquettes ne lui servent pas** : on arrête, ou on change de cible si elle en indique
  une autre.
- **Le pré-test (5b) ne montre aucun avantage des étiquettes humaines sur la carte seule** (écart inférieur au
  bruit entre graines sur toutes les mesures) : on en parle avant que Jonathan n'aille au-delà de la séance
  d'étalonnage. Issues possibles : viser les endroits où la carte se trompe le plus, ou s'arrêter.
- **Aucun gain mesurable fin janvier** avec les étiquettes de Jonathan.
- **La cible est déjà couverte** : quelqu'un publie des étiquettes vérifiées à la main sur les couches `0` à `4`
  avant nous (à revérifier avant chaque publication).
- **Débit trop faible** : après trois séances, moins de 1 cm² vérifié par heure. On revoit l'appli ou le choix
  des tuiles.

## Risques connus

- Volume : 15 à 25 heures de correction d'ici fin décembre. Notre intérêt n'est pas la surface, mais des objets
  sans étiquette humaine, le format de l'équipe, l'outil et la mesure.
- Mesure : le bruit entre graines publié (0,06 à 0,13 sur w016) est du même ordre que les gains attendus (environ
  0,04). D'où des comparaisons appariées, plusieurs graines, et les 9 zones plutôt que 3.
- Style d'étiquetage : un modèle entraîné sur des étiquettes « à la manière de l'équipe » est avantagé quand on le
  note sur des étiquettes de l'équipe. À signaler dans tout résultat ; noter aussi avec une tolérance aux bords.
- Calcul : pas de recette complète sur T4 (environ 78 000 pas). On affine un checkpoint publié sur 1 000 à 2 000
  pas. L'entraîneur de l'équipe demande Python 3.14 et des modules C++ hors PyPI : on utilise notre affineur.
- Fenêtre First Letters : 7 prix restants pour 19 volumes, et reader-v3 sert déjà à la majorité des soumissions.
- Un humain non papyrologue peut valider de fausses lettres : d'où la séance d'étalonnage et la consigne prudente.

## Après décembre : First Letters

À planifier quand la mesure sera faite. Acquis : entraîner sur des données 2 µm est admis si le modèle est appliqué
au volume éligible à 9 µm (réponse de l'équipe, ticket villa #1739) ; le règlement refuse toute annotation manuelle
de la zone revendiquée ; le Grand Prize exige la publication de chaque jeu d'entraînement. La question « étiquettes
manuelles publiques d'autres rouleaux » posée sur Discord le 22/11 reste sans réponse. Rien dans le dépôt si des
lettres apparaissent sur un rouleau éligible.
