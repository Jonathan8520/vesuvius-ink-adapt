# Point du 23 novembre 2026 : antériorité vérifiée, plan révisé, banc de mesure prêt

**Mise à jour du 22/11 à 22 h 50 UTC : séances au stylet suspendues.** Tu as essayé l'appli et tu ne savais pas
quoi juger. Tu as raison : ce que les annotateurs de l'équipe ajoutent à la carte du modèle, c'est le redessin des
lettres, et il faut en connaître les formes. Vérifié sur le lot d'étalonnage : même un tri parfait, tache par
tache, ne ferait passer l'accord avec l'équipe que de 0,72 à 0,74 (journal A10). Tu n'as donc rien à dessiner pour
l'instant. Le pré-test de cette nuit dit si des étiquettes humaines servent à l'entraînement ; on décide ensuite.
Ce qui suit date d'avant ton essai.

## En trois phrases

- D'autres ont déjà des étiquettes faites à la main à ~9 µm. Ce qui reste libre est plus étroit qu'annoncé hier,
  mais réel : le format de l'équipe sur ses surfaces natives, la preuve par entraînement, un outil au stylet.
- Rien ne dit encore qu'une correction humaine fait mieux que la carte du modèle seule. Je le mesure cette
  semaine, sans toi, avec les étiquettes humaines qui existent déjà.
- Ta première séance (29/11) reste un étalonnage en aveugle sur la couche `--1` de PHerc0500P2.

## Deux corrections à ce que j'ai écrit hier

1. **Les 6 masques de validation ne sont pas « cachés ».** Ils sont dans le dossier `ink/` du bucket Hugging Face
   depuis juillet et sur S3 depuis septembre, et deux personnes les ont déjà recensés (nestorvfx, ibarapascal).
   Ils manquent seulement dans le dossier 9 µm. `docs/DISCORD-FAITS.md` est corrigé, avec le ton à tenir :
   un signalement voisin a été fermé sèchement par l'équipe en août.
2. **PHerc0500P2 n'avait pas 7 couches libres mais 5.** jeff-j-chen a déjà ses propres étiquettes sur `front` et `--2` (et
   reprend celles de l'équipe sur `--1`). Restent les couches `0`, `1`, `2`, `3`, `4` : c'est la nouvelle cible.

## Ce que j'ai mesuré (détail : `docs/EXPERIMENTS.md`, A5 à A7)

- La carte du modèle 2 µm et les étiquettes humaines de l'équipe ne se recouvrent qu'à 60 à 85 %. Il y a donc
  de la matière à corriger. Image : `docs/img/pherc0500p2_m1_carte_vs_humain.png`.
- La « bande incertaine » ne contient que 14 à 24 % des désaccords. Et trois essais publics trouvent que les
  zones incertaines ne valent pas mieux que des zones au hasard. **L'appli te montrera donc moitié tuiles
  incertaines, moitié tuiles au hasard**, et on mesurera lesquelles servent. C'est un écart à ta consigne
  (« seulement les zones incertaines ») : dis-moi si tu préfères autrement.
- Le report du scan fin vers la surface 9 µm tombe juste à moins d'un pixel (vérifié contre l'équipe).

## Prêt

- Plan révisé : `docs/PLAN.md`. État de l'art : `docs/RESEARCH.md`, section 10.
- Banc de mesure : données (jeu Kaggle privé `vesuvius-ink9um-bench`, 3,7 Go), affineur, script Kaggle. Sur CPU,
  il redonne exactement les scores connus du modèle publié (0,810 et 0,937 sur w016).
- Pré-test en trois branches : sans ajout, avec la carte du modèle, avec les étiquettes humaines de l'équipe
  (mêmes pixels de PHerc0009B et de PHerc0500P2 `--1`). Mesure sur les 9 zones réservées et sur PHerc0841.

- **Appli au stylet, version 0.1** : page privée https://claude.ai/artifact/KkqKvAT9n2jTRyAqYhKrh9 (à ouvrir
  dans Chrome sur la tablette, connecté à claude.ai). Lot d'étalonnage : 6 tuiles de la couche `--1`, en aveugle.
  Essayée dans un navigateur de test, pas encore sur la tablette.
- Cartes de pré-étiquettes des 8 couches de PHerc0500P2 sur la surface 9 µm.

## Prochaines étapes

- Résultat du pré-test Kaggle (cette nuit), puis analyse.
- Ton essai de l'appli : cinq minutes suffisent pour dire si le stylet peint bien et si deux doigts déplacent.
- Tuiles des couches `0` à `4` (moitié incertitude, moitié hasard) pour les séances suivantes.

## Ce que j'attends de toi

- Essayer l'appli sur la tablette et me dire ce qui gêne (taille des boutons, stylet, zoom, lisibilité).
  La vraie séance de 20 minutes peut attendre le 29/11.
- Écrire et poster les deux messages Discord (`docs/DISCORD-FAITS.md`, revu).
- Me dire si la règle « jamais d'étiquettes » s'étend aux rouleaux du seul Grand Prize (PHerc1447, PHerc0211).
  En attendant, je n'y touche pas.
- Me dire si je peux pousser sur `main`. Tout est sur la branche `claude/jolly-shannon-2xycqz`.
- Pour information : le dépôt public de jeff-j-chen contient des étiquettes sur un rouleau éligible à First
  Letters. Je n'en ai rien copié et rien n'en figure dans le dépôt.

## Kaggle

- Essai court réussi (2 × T4) : 0,9 s par pas, scores du modèle publié retrouvés à l'identique.
- Pré-test lancé le 22/11 à 22 h 16 UTC (`vesuvius-ink9um-bench-pretest`, 3 branches, 5 graines, 1 000 pas,
  environ 2 h 30). Résultat à lire dans `docs/EXPERIMENTS.md`, entrée A8, dès qu'il tombe.
- Quota GPU : environ 26 h restantes après ce run, jusqu'au 28/11.
