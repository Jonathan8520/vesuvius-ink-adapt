# Contexte : le Vesuvius Challenge et les prix visés

Le Vesuvius Challenge (https://scrollprize.org) récompense les contributions qui aident à lire les rouleaux
d'Herculanum, carbonisés en 79 et illisibles sans les ouvrir. La chaîne : scan CT (synchrotron), reconstruction
de la surface du papyrus (« déroulage virtuel »), puis détection de l'encre par apprentissage automatique.

- Pages utiles : https://scrollprize.org/prizes, https://scrollprize.org/2026_open_problems,
  https://scrollprize.org/data, Discord : https://discord.gg/V4fJhvtaQn
- Il faut être inscrit sur le Discord du challenge au moment de la soumission.

## Progress Prizes (notre cible)

- Évalués chaque mois. **Prochaine date limite : 30 novembre 2026 à 23 h 59, heure du Pacifique.**
- **Meilleure soumission du mois : 20 000 $ garantis**, choisie par l'équipe. Autres prix selon l'importance :
  20 000, 10 000, 5 000, 2 500, 1 000, 500 ou 250 $.
- Le jury favorise les contributions :
  - **publiées tôt** (avec poids et données d'entraînement le cas échéant) ;
  - **réellement utilisées** par la communauté (questions, retours, demandes) ;
  - qui **améliorent les résultats sur des données réelles**, évaluées sur leurs jeux de données publics pour la
    détection d'encre ;
  - qui **corrigent des bugs** d'outils utilisés ;
  - **bien documentées** (tutoriels, images, exemples).
- Il décourage les outils d'analyse ou d'évaluation isolés : il veut ce qui fait **directement** avancer le
  déroulage ou la détection d'encre.
- Exigences : un problème précis traité sur les données du challenge, une démonstration, un avantage net sur les
  solutions existantes, une documentation avec exemples, des formats standards (OME-Zarr, tifxyz).
- Plusieurs petites contributions d'un même mois : les regrouper en une seule soumission.
- Pour toucher un prix, le code doit être publié sous licence permissive.
- Formulaire : lien « Submission Form » dans la section Progress Prizes de https://scrollprize.org/prizes

Repère : en octobre 2026, 29 lauréats. Le prix de 20 000 $ est allé à un ensemble de travaux sur le déroulage
virtuel (HercUNet, HercuViT) ; des outils plus modestes ont reçu de 250 à 2 500 $.

## First Letters (à garder en tête)

- 50 000 $ par rouleau pour 10 lettres lisibles dans une zone de 4 cm² d'un rouleau éligible (7 prix restants
  au 22/11/2026). Date limite : 25 juin 2027.
- Liste des rouleaux et volumes éligibles : `prizeEligibility.json` (dépôt ScrollPrize/villa).
- **Ne jamais rendre public une découverte avant l'annonce officielle.**
