# Plan : petits Progress Prizes, en solo (cap du 24 novembre 2026)

Ce plan remplace les deux précédents (historique git) :
- sprint de novembre, arrêté le 22/11 : déjà publié par d'autres ;
- étiquettes vérifiées à la main par Jonathan, arrêtée le 23/11 : aucun gain mesurable (journal A8 et A10).

## But

Obtenir de petits Progress Prizes avec ce qui est déjà fait et avec des correctifs utiles, sans projet lourd.

## Règles propres à ce cap

- Jonathan écrit lui-même ses messages Discord et remplit le formulaire. La session prépare les faits et les
  réponses (`docs/DISCORD-FAITS.md`, `docs/SOUMISSION-2026-11.md`).
- Aucune PR ouverte sans que Jonathan l'ait vue et ait dit oui.
- Règles des mainteneurs à respecter (villa, `CONTRIBUTING.md`, lu le 24/11) : un correctif doit venir d'un
  usage réel des outils sur de vraies données ; preuve avant/après sur données réelles, avec capture de l'erreur
  puis de l'outil qui tourne ; section « motivation » ; pour une PR écrite avec un LLM, un commentaire écrit par
  un humain. Ils annoncent fermer les PR qui ressemblent à une « fishing expedition » de LLM sans usage humain
  réel derrière. Ce qu'ils ont refusé ou accepté : `docs/RESEARCH.md`, section 5.
- Les règles absolues de `CLAUDE.md` restent valables (rouleaux éligibles, zones réservées, licences, secrets).

## Étape 1 : soumission de novembre (échéance : 30/11, 23 h 59 heure du Pacifique)

Sujet : la comparaison « étiquettes humaines contre carte du modèle 2 µm, sur les mêmes pixels » (journal A8).
En fermant la PR villa #2381 (un outil qui propose où étiqueter), le mainteneur a demandé à son auteur une
comparaison d'entraînements pour cet outil. Il n'a pas demandé la nôtre ; la nôtre est une comparaison
d'entraînements sur une question voisine, la source des étiquettes.

- [ ] a. Vérifier que personne n'a publié la même comparaison (même pixels, affinage apparié). Noter dans
      `docs/RESEARCH.md`. Si quelqu'un l'a publiée : on le dit à Jonathan et on n'envoie pas.
- [x] b. Résultats principaux : branches `C`, `T`, `H` à 5 graines depuis s43-75k ; `D` à 2 graines.
- [ ] c. Consolidation (kernel `vesuvius-ink9um-bench-robust`, lancé le 24/11) : `D` complétée à 5 graines, et
      `base`, `C`, `T`, `H` refaites depuis un second checkpoint (s42-75k, 3 graines).
- [ ] d. Rapport reproductible en anglais : question, méthode, données exactes, commandes, résultats avec
      intervalles, limites. La chaîne de reproduction est relancée depuis un clone neuf.
- [ ] e. Réponses aux champs du formulaire (5 questions, en anglais), et faits pour le message Discord de
      Jonathan. Les 6 masques de validation en une ligne d'annexe.
- [ ] f. Jonathan relit, pousse ou non sur `main`, poste s'il le souhaite, remplit le formulaire.

Attente réaliste : 0 à quelques centaines de dollars. L'équipe écrit qu'elle décourage les outils d'audit et
d'évaluation seuls ; notre réponse est que le banc est réutilisable pour tester toute source d'étiquettes, et que
le résultat dit où l'effort humain d'étiquetage est inutile.

## Étape 2 : correctifs dans les outils de l'équipe (à partir de décembre)

Cibles : chaîne d'encre (`vesuvius.ink_detection` : inférence, conversion d'étiquettes, entraînement), outils de
téléchargement des données, paquet `vesuvius`.

**Difficulté à régler d'abord.** Nous n'utilisons pas encore ces outils : notre chaîne réimplémente le modèle.
Or les mainteneurs ne veulent que des correctifs nés d'un usage réel, et la session ne peut pas exécuter le code
de villa (refus de l'environnement, 22/11). Proposition, à valider avec Jonathan début décembre :
1. faire tourner les outils de l'équipe pour de vrai, sur Kaggle, sur une tâche que nous faisons déjà
   (inférence officielle sur PHerc0841, conversion de nos étiquettes avec `create_label_zarrs`, téléchargement des
   données d'entraînement 9 µm) et noter ce qui casse ;
2. ne garder que ce qui casse sur de vraies données, vérifier les tickets et PR existants, puis corriger une chose
   à la fois avec preuve avant/après ;
3. Jonathan reproduit le problème lui-même quand c'est possible et écrit le commentaire humain de la PR.

## Jalons

| Date | Jalon |
| --- | --- |
| 26/11 | Antériorité vérifiée, rapport et chaîne de reproduction prêts |
| 27/11 | Résultats de consolidation intégrés (si le kernel est passé) |
| 28/11 | Réponses du formulaire et faits Discord prêts ; relecture par Jonathan |
| 30/11 | Soumission par Jonathan (avant 23 h 59 heure du Pacifique, soit le 1er décembre 8 h 59 à Paris) |
| début décembre | Premier passage des outils de l'équipe sur Kaggle, liste des pannes réelles |
| fin janvier | Bilan |

## Critère d'arrêt

Rien d'accepté (PR fusionnée) ni de primé fin janvier 2027 : on arrête.

## Risques

- La comparaison est une évaluation : le jury peut la classer parmi les audits qu'il décourage.
- Portée du résultat : deux segments, une recette d'affinage abrégée.
- Étape 2 : sans usage réel des outils, les PR seraient fermées. Le temps de Jonathan devient nécessaire ici.
