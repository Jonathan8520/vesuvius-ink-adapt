# Plan : étiquettes d'encre vérifiées à la main (cap du 22 novembre 2026)

Ce plan remplace celui du sprint de novembre, arrêté le 22/11 (ancien texte dans l'historique git, raisons dans
`docs/HANDOFF.md`).

## But

1. **D'ici le 31 décembre 2026** : publier des étiquettes d'encre à ~9 µm vérifiées à la main par Jonathan, dans le
   format de l'équipe, avec la preuve chiffrée qu'elles améliorent un modèle. Soumission aux Progress Prizes de
   décembre (date exacte de l'échéance à confirmer sur https://scrollprize.org/prizes).
2. **Ensuite, jusqu'au 25 juin 2027** : utiliser le modèle obtenu pour First Letters (50 000 $ par rouleau).

Répartition : Jonathan corrige au stylet 3 à 5 heures par semaine sur sa tablette (Galaxy Tab S6 Lite), par
séances de 20 minutes. La session fait le reste.

## Ce que la vérification préalable a montré (22/11)

Lecture du billet sur PHerc. 211, des dépôts de Priyank Aranke et des jeux publiés. Détail : `docs/RESEARCH.md`.
Chiffres par rouleau : `docs/INVENTAIRE.md`.

- **La méthode visée a déjà été appliquée et publiée.** Priyank Aranke a reporté les cartes du modèle 2 µm de
  l'équipe sur des surfaces à ~9 µm de PHerc0814, PHerc0841 et PHerc0009B, puis les a corrigées à la main :
  environ 250 cm² supervisés (294 millions de pixels, médiane de 21 révisions par segment), publiés sous
  CC BY-NC 4.0 avec le code et le modèle. D'après lui, c'est ce qui a le plus compté pour trouver les lettres de
  PHerc. 211. Ces trois objets sont, d'après son analyse, ceux qui ressemblent le plus aux rouleaux non lus.
- **Ce que ses jeux ne couvrent pas** :
  - ses étiquettes sont sur ses propres surfaces et dans son propre format (tuiles `npy`), pas sur les segments
    publics ni dans le format que lit l'entraîneur de l'équipe ;
  - son outil d'étiquetage (« Donor Studio ») n'est pas publié ;
  - pour PHerc0139, PHerc0343P et PHerc0500P2, il n'existe à ~9 µm que des étiquettes issues de modèles
    (reader-v2-labels de Domenico Russo, qui laisse de côté la bande incertaine), plus 5 segments annotés par
    l'équipe pour 0139 ;
  - PHerc1667 et PHercParis4 n'ont aucune surface publiée à ~9 µm.
- **Conséquence** : refaire 0814, 0841 ou 0009B n'apporterait rien. Notre apport possible tient en trois points :
  des étiquettes vérifiées là où il n'y a que des sorties de modèle, un outil d'étiquetage ouvert et utilisable
  sur tablette, et la mesure du gain par heure de correction humaine.

## Règles

- Jamais d'étiquettes sur un rouleau éligible à First Letters (liste en tête de `docs/INVENTAIRE.md`).
- Jamais d'étiquette ni d'entraînement dans les 9 zones de validation réservées d'`ink_9um`, quelle que soit la
  représentation. PHerc0841 reste un jeu de mesure : pas d'étiquettes dessus.
- Si des lettres apparaissent sur un rouleau éligible : rien dans le dépôt, prévenir Jonathan.
- Discord : la session prépare les faits (`docs/DISCORD-FAITS.md`), Jonathan écrit et poste.
- Licences : étiquettes sous CC BY-NC 4.0 (licence des scans), code sous MIT. Citer les jeux réutilisés.
- Publier tôt : une première version du jeu et de l'appli dès qu'elles servent, sans attendre la fin décembre.

## Cible des étiquettes

Choix provisoire, à confirmer par la réponse de l'équipe (message Discord n° 2) et par la première séance.

**Condition préalable, vérifiée à l'œil le 22/11 : on ne peut corriger à la main que là où la carte du modèle 2 µm
est lisible** (lignes et formes de lettres). Là où elle ne montre que des taches, un humain ne peut pas juger.

| Candidat | Carte 2 µm lisible ? | Étiquettes à ~9 µm existantes | Verdict |
| --- | --- | --- | --- |
| **PHerc0500P2, 8 couches numérotées** (`500P2_front`, `--1`, `0`, `--2`, `1`, `2`, `3`, `4` ; 9,362 µm à 113 keV et 2,215 µm) | oui : lignes de lettres nettes sur `front`, `--1`, `--2`, partielles sur les autres | `front` : sorties de modèle seulement ; `--1` : étiquettes de l'équipe à 2,2 µm ; les 6 autres : rien | **cible de départ** |
| PHerc0343P, segment `20250511003658-tifxyz` (8,64 µm à 116 keV) | oui, trois lignes | sorties de modèle seulement | deuxième cible, petite |
| PHerc0343P, 7 autres segments ; PHerc0500P2, 25 segments `z_dbg_gen` | non, taches seulement | sorties de modèle | écartés : invérifiables à la main |
| PHerc0139 natif (9,362 µm) | oui, lignes de texte sur tous les segments regardés | 5 segments de l'équipe, 20 en sorties de modèle (819 cm²) | réserve : gros volume, mais rouleau jugé peu ressemblant aux rouleaux non lus |
| PHerc0814, PHerc0009B, PHerc0841 | oui | corrigés à la main par Priyank Aranke | écartés : déjà faits |
| PHerc1667, PHercParis4 | oui | aucune surface publiée à ~9 µm | écartés pour l'instant |

Pourquoi PHerc0500P2 : cartes lisibles, aucune étiquette humaine à ~9 µm sur 7 couches, même réglage de scan
(9,362 µm à 113 keV) que 10 rouleaux éligibles, taille compatible avec nos heures (ordre de grandeur : 1 heure par couche, à mesurer).
La couche `--1`, déjà annotée par l'équipe, sert d'étalon : Jonathan la corrige en aveugle, on compare, puis elle
reste hors entraînement pour la mesure.

## Étapes

- [x] **0. Vérification préalable** (22/11) : méthode de Priyank Aranke, jeux déjà publiés.
- [x] **1. Inventaire** (22/11) : `scripts/inventory.py` → `docs/INVENTAIRE.md`. 10 objets hors First Letters ont un
      scan fin et un scan à ~9 µm. À relancer quand le catalogue du bucket change.
- [ ] **2. Pré-étiquettes et incertitude.**
      a. Tri de lisibilité : une planche réduite par segment candidat, classée lisible ou non (fait le 22/11 pour
         PHerc0343P, PHerc0500P2 et six segments de PHerc0139).
      b. Pour chaque segment retenu : carte du modèle 2 µm de l'équipe ramenée au repère de la surface ~9 µm
         (recalage vérifié sur la texture CT, tolérance 2 px ; l'essai sur PHerc0343P montre 8 px d'écart à
         corriger), et carte de reader-v3 calculée par nous quand l'équipe ne l'a pas publiée (cas de PHerc0500P2).
      c. Pré-étiquette : encre si la carte 2 µm dépasse 128, fond sous 64 (règle de reader-v2-labels).
      d. Zones à montrer : désaccords entre la carte 2 µm et reader-v3, taches isolées hors des lignes de texte,
         traits interrompus. La seule bande 64 à 128 ne suffit pas : c'est surtout le contour des taches.
- [ ] **3. Appli web au stylet.** Page statique (sans serveur ni compte), ouverte dans Chrome sur la tablette :
      une tuile à la fois, couches CT, carte du modèle, pré-étiquette ; peindre encre, fond ou « je ne sais pas » ;
      valider ; minuteur de 20 minutes ; reprise là où on s'est arrêté ; export d'un fichier de corrections.
      Avant d'écrire : vérifier qu'aucun outil existant ne fait déjà l'affaire.
      Première séance : étalonnage en aveugle sur une zone déjà annotée par l'équipe, pour chiffrer l'accord.
- [ ] **4. Export au format de l'équipe.** `<segment>_inklabels.zarr` et `<segment>_supervision_mask.zarr`
      (Zarr v2, uint8, 255 sur le plan médian, même forme que la surface native), lisibles par l'entraîneur de
      villa sans changement, plus un manifeste (segment, surface, origine de chaque pixel : modèle ou humain,
      date, durée). Dépôt sur Hugging Face.
- [ ] **5. Mesure du gain.**
      a. Finir le test de mémorisation sur les 9 zones réservées (en cours le 22/11).
      b. Banc d'entraînement sur Kaggle : recette `ink_9um` raccourcie, données réduites aux zones utiles.
         Contrôle : retrouver un chiffre publié avant toute comparaison.
      c. Comparaison : étiquettes de modèle seules contre étiquettes de modèle plus corrections humaines, mêmes
         graines, au moins 2 graines. Mesure sur les 9 zones réservées (3 publiées et 6 sur S3), sur la couche
         `--1` de PHerc0500P2 (étiquettes de l'équipe, jamais entraînée) et sur PHerc0841 (rouleau jamais vu, même
         réglage de scan).
      d. Courbe du gain en fonction des heures de correction.

## Jalons

| Date | Jalon | Critère |
| --- | --- | --- |
| 24/11 | Messages Discord postés par Jonathan (zones de validation absentes ; question sur les rouleaux et le format) | faits prêts dans `docs/DISCORD-FAITS.md` |
| 29/11 | Première séance de 20 minutes sur la tablette : couche `--1` de PHerc0500P2, en aveugle | l'appli charge, le stylet peint, l'export se relit, accord avec l'équipe chiffré |
| 29/11 | Banc d'entraînement Kaggle | un chiffre publié retrouvé à ±0,01 |
| 06/12 | Version 0.1 publiée : appli, premières étiquettes | chargement sans erreur dans `vesuvius.ink_detection` |
| 13/12 | Première mesure avec et sans corrections | écart et bruit entre graines chiffrés |
| 20/12 | Les 7 couches de PHerc0500P2 terminées, segment lisible de PHerc0343P entamé ; courbe gain par heure | |
| 27/12 | Jeu figé, documentation, notebook Kaggle public | |
| 31/12 | Soumission Progress Prizes par Jonathan | |
| fin janvier | Bilan : gain mesurable ou arrêt | voir critères d'arrêt |

## Critères d'arrêt

- **L'équipe répond que ces étiquettes ne lui servent pas** : on arrête, ou on change de cible si elle en indique
  une autre.
- **Aucun gain mesurable fin janvier** : écart inférieur au bruit entre graines sur les trois mesures.
- **La cible est déjà couverte** : quelqu'un publie des étiquettes vérifiées à la main sur le même objet avant nous
  (à revérifier avant chaque publication avec `scripts/inventory.py` et une recherche sur Hugging Face).
- **Débit trop faible** : après trois séances, moins de 1 cm² vérifié par heure. On revoit alors l'appli ou le
  choix des tuiles avant de continuer.

## Risques connus

- Volume : 15 à 25 heures de correction d'ici fin décembre, face aux 250 cm² déjà publiés par Priyank Aranke.
  Notre intérêt est ailleurs (objets sans étiquette humaine, outil ouvert, mesure par heure), pas dans la surface.
- Mesure : les 9 zones réservées sont sur PHerc0139, 0814 et 1667, en représentation « 2,4 µm réduit ». Des
  étiquettes sur un fragment natif peuvent ne rien y changer. D'où les deux autres mesures.
- Calcul : la recette complète demande environ 5 heures sur une H100. Sur un T4, il faudra une recette raccourcie
  ou un affinage à partir d'un checkpoint publié, et une reprise entre sessions.
- Règles : la question « peut-on entraîner un modèle First Letters avec des étiquettes manuelles publiques » est
  posée sur Discord et sans réponse au 22/11. À trancher avant la deuxième phase.
- Un humain non papyrologue peut valider de fausses lettres. Consigne : n'étiqueter que ce qui est appuyé par la
  carte 2 µm, et utiliser « je ne sais pas » sans retenue.

## Après décembre : First Letters

À planifier quand la mesure sera faite. Points déjà acquis : 37 soumissions de 15 concurrents sur le seul
PHerc. 211, donc la concurrence est forte ; les lauréats entraînent sur 0814, 0841 et 0009B ; PHerc. 1203 est déjà
travaillé avec son scan à 2,4 µm. Rien dans le dépôt si des lettres apparaissent sur un rouleau éligible.
