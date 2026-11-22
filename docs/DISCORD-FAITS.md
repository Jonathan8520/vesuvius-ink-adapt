# Faits pour deux messages Discord (à écrire par Jonathan)

Règle du serveur (#rules, 29/07/2026) : pas de message généré par IA à la place de sa propre participation.
Ce fichier ne contient donc que des faits, des chiffres et des chemins. Les messages sont à écrire toi-même.
Si tu postes dans #robots, ajoute une ligne « AI disclosure ». Les identifiants entre accents graves sont à
recopier tels quels (ils sont en anglais dans les données).

## Message 1 : six masques de validation absents du dossier d'étiquettes 9 µm

**Corrigé le 22/11 à 21 h 40 UTC, complété le 23/11.** La première version disait que les 6 zones n'existaient
que sur S3 : c'est faux. Ne pas présenter ces masques comme une découverte. Ce qui est nouveau, c'est qu'ils
manquent dans le dossier 9 µm, et les mesures ci-dessous.

**Ton à tenir.** Un signalement voisin a été mal reçu : le ticket villa #1638 (khj1222, 29/08/2026, « all three
shipped _validation_mask splits cut through annotated regions ») a été fermé « not planned » et verrouillé le
jour même par pmh47, avec cette réponse : « "validation mask is disjoint from the supervision mask" -- indeed,
so there is no actual issue. » et « Provided one interprets results carefully in terms of what is intra-segment /
inter-segment / inter-scroll results (which one always should!), and does not make overly broad claims, there is
no problem. » Donc : présenter les 6 masques comme une ressource utile qui manque dans un dossier, pas comme un
défaut de la validation. Dire que toutes ces mesures sont intra-segment (mêmes rouleaux que l'entraînement).

### L'essentiel

- Les checkpoints `scrollprize/ink_9um` listent 9 `reserved_validation_cases` et 3 `online_validation_cases`
  (champ `data_provenance` de la config embarquée, vérifié dans `hybrid_3d2d-seed43/step-020000.pth`).
- Le dossier d'étiquettes 9 µm (bucket Hugging Face `scrollprize/datasets`, dossier
  `ink_9um/labels/aligned-scrollprizeorg-21slices/`) ne contient un `_validation_mask.zarr` que pour les 3 cas
  « online » : `pherc0139-w016`, `pherc0814-46527`, `pherc1667-w029`.
- Les masques des 6 autres cas sont publics, mais seulement dans le repère du scan 2,4 µm :
  - dossier `ink/` du même bucket Hugging Face : `ink/<objet>/<segment>/<segment>_validation_mask_v2.tif`,
    en ligne depuis le 7 juillet 2026 (15 segments ont ce fichier, dont les 9 cas réservés) ;
  - S3, depuis le 18/09/2026 : `<segment>/ink-labels/<volume 2,4 µm>/20260918/validation.zarr`. Son niveau 2 a
    exactement la forme des étiquettes 9,6 µm du dossier `ink_9um` (même repère).
- Antériorité, à citer :
  - l'audit de nestorvfx du 24/09/2026 (`nestorvfx/vesuvius-ink-training`, fichier
    `records/validation_audit.json`) recense ces 15 masques et leur republication sur S3 ;
  - ibarapascal/ink-disagree (23/09/2026) recense les 13 masques `validation` du jeu S3 : 9 blocs tenus à l'écart
    (PHerc0139 × 2, PHerc1667 × 5, PHerc0814, PHerc0009B) et 4 « surface entière » (PHerc0841 × 3, PHerc0500P2) ;
  - le schéma du catalogue S3 prévient que le sens de `validation` n'est pas le même d'un jeu à l'autre.
  Aucun des deux ne dit que 6 masques manquent dans `ink_9um/labels`. Nous n'avons trouvé personne qui le dise.
- Ces 6 zones n'ont aucun pixel commun avec le `_supervision_mask` d'entraînement publié. Elles font 5,3 fois la
  surface des 3 masques publiés, et elles sont loin des pixels d'entraînement.
- Conséquence pratique : les évaluations 9 µm que nous avons lues (Domenico Russo, khj1222, Erwin Nieuwlaar)
  n'utilisent que les 3 masques, soit 0,66 cm² collés à l'entraînement, alors que 3,52 cm² bien isolés existent.
  La fiche `domenicor046/ink9um-dense-labels` parle de « the three held-out validation regions ».

### Chiffres (repère des étiquettes 9,6 µm)

« Proche » : part des pixels de la zone à moins de 128 px puis de 256 px d'un pixel de supervision d'entraînement
(même mesure que l'audit de khj1222, `docs/17_holdout_audit.md`, dont on retrouve les chiffres sur les 3 masques
publiés). Test de mémorisation : checkpoint `seed43/step-075000`, fenêtre centrée, sens direct, seuil 0,5.

| Cas (`ink_9um`) | Segment public | Masque dans le dépôt 9 µm | Zone réservée | Proche (128 / 256 px) | Zone : préc. équilibrée / F1 / AUC | Pixels d'entraînement du même segment |
| --- | --- | --- | --- | --- | --- | --- |
| pherc0139-w016 | 20250108000004-w029_2025010827 | oui | 178 146 px (0,16 cm²) | 59 % / 99 % | 0,810 / 0,720 / 0,937 | 0,975 / 0,955 / 0,994 |
| pherc0814-46527 | 20260226000000-46527_2um_try2 | oui | 161 051 px (0,15 cm²) | 45 % / 88 % | 0,773 / 0,712 / 0,863 | 0,992 / 0,988 / 0,9998 |
| pherc1667-w029 | 20251212185248-w029_20251212185248662_flatboi | oui | 382 353 px (0,35 cm²) | 23 % / 45 % | 0,838 / 0,758 / 0,930 | 0,989 / 0,983 / 0,9996 |
| pherc0139-w028 | 20260115000000-w044_2026011522 | **non** | 226 520 px (0,21 cm²) | 0 % / 9 % | 0,731 / 0,610 / 0,841 | 0,989 / 0,980 / 0,9995 |
| pherc0139-w029 | 20260126000000-w045_2026012619 | **non** | 71 807 px (0,07 cm²) | 0 % / 0 % | 0,783 / 0,700 / 0,879 | 0,936 / 0,911 / 0,976 |
| pherc1667-w018 | 20240304144031-w018_20240304144031_flatboi | **non** | 1 934 776 px (1,78 cm²) | 0,2 % / 3,5 % | 0,734 / 0,600 / 0,830 | 0,944 / 0,909 / 0,986 |
| pherc1667-w023 | 20240304161941-w023_20240304161941_flatboi | **non** | 589 349 px (0,54 cm²) | 0 % / 0 % | 0,643 / 0,439 / 0,769 | 0,980 / 0,966 / 0,998 |
| pherc1667-w028 | 20251208130119-w028_20251208130119156_flatboi | **non** | 401 932 px (0,37 cm²) | 0 % / 0 % | 0,818 / 0,737 / 0,926 | 0,992 / 0,987 / 0,9996 |
| pherc1667-w031 | 20251223230000-w031_2025122323_flatboi | **non** | 594 493 px (0,55 cm²) | 0 % / 0 % | 0,687 / 0,539 / 0,810 | 0,986 / 0,976 / 0,9992 |

Totaux : 721 550 px (0,66 cm²) publiés, 3 818 877 px (3,52 cm²) non publiés à 9 µm.

### Pourquoi on pense que ces zones n'ont pas servi à l'entraînement

1. Recouvrement nul avec le masque de supervision publié, pour les 6 cas.
2. Pour les 8 cas qui ont des étiquettes sur S3 : surface de supervision du dépôt 9 µm = supervision S3 moins
   validation S3 (par exemple 1667-w018 : 12,81 cm² pour 14,56 − 1,78). Le dépôt 9 µm a donc été construit en
   retirant la zone réservée des 9 cas.
3. Pour les 2 cas « online » présents aux deux endroits, le masque du dépôt et celui de S3 coïncident (IoU 0,995).
4. Test de mémorisation, fait sur les 9 cas : le checkpoint à 75k retrouve ses pixels d'entraînement presque
   parfaitement (F1 0,91 à 0,99), mais reste entre 0,44 et 0,74 de F1 dans les 6 zones non publiées (0,71 à 0,76
   dans les 3 masques connus).
5. AUC moyenne pondérée par pixel : 0,83 dans les 6 zones non publiées, 0,92 dans les 3 zones publiées. Les
   zones isolées de l'entraînement sont plus difficiles. C'est un indice de fuite sur les 3 masques publiés, pas
   une preuve : ce ne sont pas les mêmes zones.
6. Le cas `pherc0139-w028` a un jumeau natif dans l'entraînement (`w044`) : sa supervision native ne touche pas la
   zone réservée (distance médiane 522 px).

### À savoir avant d'écrire

- Les étiquettes d'encre du dépôt 9 µm (`_inklabels.zarr`) couvrent déjà ces zones. Il ne manque que le masque.
- `pherc0139-w016` (segment public `…w029_2025010827`) n'a pas de dossier `ink-labels` sur S3.
- Ces zones ne sont tenues à l'écart que pour la recette `ink_9um`. Trois d'entre elles (0139-w028, 0139-w029,
  1667-w028) sont couvertes par les pseudo-étiquettes denses de `domenicor046/ink9um-dense-labels` : sa fiche
  écrit `supervision_mask = render-valid AND NOT validation_mask`, et seuls les 3 masques publiés y sont retirés
  (canevas couverts à 82 à 89 %). Les modèles qui en descendent (reader-v2, reader-v3, argus) ont donc été
  supervisés dans ces 3 zones, avec les cartes du modèle 2 µm. Pour eux, seules 1667-w018, w023 et w031
  (2,87 cm²) restent propres. Déduit de la fiche, pas mesuré par nous.
- L'audit de nestorvfx signale un décalage de canevas entre les masques de `ink/` et leur version S3 (environ
  20 px pour PHerc1667, et [-460, -83] px pour 0139/w028, IoU 0,9884). Nos mesures utilisent la version S3, qui
  est dans le repère des étiquettes 9,6 µm (vérifié : supervision 9 µm = supervision S3 moins validation S3).
- Elles restent dans des rouleaux vus à l'entraînement : ce n'est pas une mesure entre rouleaux.
- On ne sait pas si l'équipe les a laissées de côté exprès. C'est la question à poser.
- Nos chiffres des 3 masques publiés recoupent ceux déjà publiés : Domenico Russo (précision équilibrée et AUC
  de s43-75k : 0,810 / 0,937 sur w016, 0,772 / 0,863 sur 0814) et khj1222 (58,6 %, 45,0 %, 23,2 % à moins d'un
  patch). Notre masque de w016 compte 178 146 px, le sien 175 222 : écart non expliqué.

### Ce qu'on peut demander

- Les 6 zones sont-elles bien tenues à l'écart des checkpoints `ink_9um` publiés, comme les 3 autres ?
- L'équipe peut-elle ajouter les 6 `_validation_mask.zarr` au dossier `ink_9um/labels`, ou préfère-t-elle qu'on
  publie un petit jeu communautaire au même format (conversion du niveau 2 de la version S3) ?

### Pour vérifier soi-même

- Code : `scripts/audit_reserved_validation.py` du dépôt https://github.com/Jonathan8520/vesuvius-ink-adapt
  (masques seuls : quelques minutes sur CPU ; `--memo s43-75k` : environ 20 minutes sur CPU).
- Exemple de chemin S3 : `PHerc1667/segments/20240304144031-w018_20240304144031_flatboi/ink-labels/2.399um-volume-20251217075048/20260918/validation.zarr/2/`.

## Message 2 : quels rouleaux et quel format d'étiquettes seraient utiles à l'équipe

Révisé le 23/11 après la vérification d'antériorité (`docs/RESEARCH.md`, section 10).

### Ce qu'on propose (faits à donner)

- 3 à 5 heures par semaine de vérification humaine au stylet, jusqu'à fin décembre au moins.
- Méthode : carte du modèle 2 µm de l'équipe (`ink_canonical_2um`, cartes `new_canon_autoresearch_recipe` de S3)
  reportée sur la surface native ~9 µm du même segment, puis corrigée à la main.
- Publication prévue : paire d'images `<segment>_inklabels` et `<segment>_supervision_mask` sur le canevas natif,
  et les Zarr correspondants, lisibles par `vesuvius.ink_detection` ; sous CC BY-NC 4.0 ; avec l'outil
  d'étiquetage (page web, stylet) et une comparaison d'entraînements.
- Jamais sur un rouleau éligible à First Letters.

### Ce qui existe déjà (pour montrer qu'on a regardé)

| Objet | Étiquettes faites à la main à ~9 µm déjà publiées |
| --- | --- |
| PHerc0814, PHerc0841, PHerc0009B | Priyank Aranke (`paranke/vesuvius-814-841-9b-studio-training-data`, environ 260 cm², ses surfaces, son format) |
| PHerc0500P2 `front`, `--1`, `--2` ; PHerc0343P `20250511003658` ; 0009B, 0841 w00, 0814, 0139 | jeff-j-chen (dépôt GitHub HercUeNet, PNG, licence MIT, clairsemées, sur les surfaces natives de l'équipe) |
| PHerc0139 | 5 segments natifs annotés par l'équipe (`ink_9um/labels/native9-scrollprizeorg-21slices`) |
| PHerc0841 (3 segments), PHerc0009B (1), PHerc0500P2 `--1` | annotations de l'équipe, mais seulement dans le repère du scan fin (S3 `ink-labels` 20260918) |
| PHerc1447 | 2 segments (`YoussefMoNader/ink-8um-pherc1447-surfaces`) |
| PHerc0139, 0814, 0500P2, 0009B, 0343P, 0172 | sorties du modèle 2 µm seuillées, non vérifiées (`domenicor046/reader-v2-labels`, 70 segments) |
| PHerc0500P2 couches `0`, `1`, `2`, `3`, `4` | rien de fait à la main (notre cible) |

### Chiffres à nous, utilisables dans le message

- Sur la couche `--1` de PHerc0500P2, la carte du modèle 2 µm seuillée à 128 et les étiquettes de l'équipe ont la
  même part d'encre (21 %) et aucun décalage, mais ne se recouvrent qu'à 73 % (IoU ; F1 0,84). Le catalogue S3
  donne un Dice de 0,837 pour ce jeu : même ordre.
- Sur les 28 jeux étiquetés de S3 : F1 de 0,60 à 0,85 selon le rouleau (catalogue S3 : Dice de 0,65 à 0,89).
- Le report du scan fin vers la surface native tient à moins d'un pixel avec un affine par segment (résidu médian
  0,4 px sur les 8 couches numérotées de PHerc0500P2), en accord avec la formule de `tifxyz-canvas-map`.

### Questions possibles

1. Des étiquettes vérifiées à la main sur les couches `0` à `4` de PHerc0500P2 (surfaces natives 9,362 µm)
   seraient-elles utiles, ou un autre objet le serait-il davantage ?
2. Format : une paire d'images sur le canevas natif plus des Zarr à 28 plans (annotation au plan 14), comme le
   dossier `native9` d'`ink_9um`, convient-il ? Ou faut-il la sortie de `create_label_zarrs` (65 plans) ?
3. Licence : le README du jeu `ink-labels` renvoie à l'ancienne licence `dl.ash2txt.org/LICENSE.txt`, qui vise les
   « ink label images » et la redistribution. Sous quelle licence publier des étiquettes corrigées à la main à
   partir des cartes de S3 (CC BY-NC 4.0) ? Et peut-on republier des reports des étiquettes de l'équipe sur le
   canevas natif (PHerc0841, 0009B, 0500P2 `--1`) ?
4. Faut-il prévoir une zone de validation tenue à l'écart dans chaque segment étiqueté, et de quelle taille ?
5. La question déjà posée dans #general le 22/11 : un modèle entraîné avec des étiquettes manuelles publiques
   d'autres rouleaux est-il admis pour First Letters ? (Acquis : le ticket villa #1739 admet l'entraînement sur
   des données 2 µm si le modèle est appliqué au volume éligible à 9 µm.)

### À savoir avant d'écrire

- Le mainteneur bruniss a fermé la PR villa #2381 (outil qui propose où étiqueter d'après l'incertitude) avec :
  « without a training run comparison we'd prefer this one stay in a separate repo and linked in community
  projects ». Notre travail reste donc dans ton dépôt, et la comparaison d'entraînements fait partie du projet.
- Les critères des Progress Prizes : « We discourage standalone analytic, auditing or evaluation tools, and
  instead encourage work that directly advances unwrapping or ink detection. » Parler d'un jeu d'étiquettes et
  d'un modèle, pas d'un audit.
- L'équipe n'a repris jusqu'ici aucune étiquette communautaire dans ses jeux ; elle a repris des modèles
  (reader-v3, argus-v3).

### À ne pas affirmer

- Que nos étiquettes amélioreront un modèle : ce n'est pas encore mesuré. Les comparaisons publiées donnent
  plutôt l'avantage à la quantité (cartes denses du modèle) sur la vérification.
- Que montrer seulement les zones incertaines est efficace : trois essais publics disent le contraire (kit
  `altrain` de ChaseHendrick, docs/20 de khj1222, ink-disagree).
- Que PHerc0500P2 ressemble aux rouleaux non lus : Priyank Aranke écrit que 0009B, 0841 et 0814 sont les plus
  proches ; nous n'avons pas de mesure pour 0500P2.
