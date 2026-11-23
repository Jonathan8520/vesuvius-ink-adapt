# En attente de la décision de Jonathan (23 novembre 2026, soir)

La piste « étiquettes vérifiées à la main » ne montre aucun gain mesurable (ci-dessous). Je recommande de
l'arrêter ; Jonathan n'a pas encore tranché. Plus aucun calcul ni rappel programmé.
Correction : une version précédente de ce fichier annonçait « projet arrêté, décision de Jonathan ». C'était une
erreur de lecture de ma part : Jonathan parlait de l'arrêt du sprint de novembre.

# Point du 23 novembre 2026 (matin) : le pré-test a parlé, la correction à la main ne sert pas

## Le résultat

- **Sur les mêmes pixels, les étiquettes humaines de l'équipe et la carte du modèle 2 µm donnent le même modèle.**
  Écart d'AUC : +0,0002 sur PHerc0841 (intervalle à 95 % : −0,005 à +0,005), +0,0008 sur les 9 zones réservées.
  5 graines, même lecture à 250, 500 et 1 000 pas. La règle de lecture était écrite avant le résultat.
- **Ajouter deux segments nouveaux aide nettement sur le rouleau jamais vu** : +0,04 d'AUC et +0,05 de précision
  équilibrée sur PHerc0841, que les étiquettes soient humaines ou tirées de la carte.
- Détail : `docs/EXPERIMENTS.md`, entrée A8.

## Ce que ça veut dire

- Corriger la carte à la main n'apporte rien de mesurable à cette échelle. Avec ton essai d'hier soir (tâche
  infaisable sans connaître les lettres, journal A10), cela fait deux raisons indépendantes. **Le critère d'arrêt
  du plan est atteint pour la piste « étiquettes vérifiées à la main ».**
- Ce qui aide, ce sont des segments nouveaux sur le scan 9 µm, étiquetés par la carte du modèle. C'est ce que font
  déjà reader-v2 et reader-v3 de Domenico Russo, sur 70 segments. Ce n'est pas un créneau libre.

## Dernière vérification (branche `D`, 23/11 à 16 h 50 UTC)

- La carte du modèle sur toute la surface, sans aucun choix humain, garde l'essentiel du gain (+0,032 d'AUC sur
  PHerc0841 au lieu de +0,039). Le choix des zones par l'équipe vaut au mieux +0,01 sur le rouleau jamais vu, et
  −0,007 sur les rouleaux vus. 2 graines seulement (un plantage, corrigé). Conclusion inchangée.

## Ce qui reste de valable

- La comparaison appariée elle-même : personne ne l'avait publiée, et le mainteneur de villa demande ce genre de
  preuve par entraînement.
- Le banc de mesure (données, affineur, analyse), relu par un relecteur indépendant côté données : aucune fuite.
- Le constat sur les 6 masques de validation absents du dossier 9 µm.
- L'appli au stylet fonctionne sur ta tablette, mais elle n'a plus d'objet si la correction ne sert pas.
- Honnêtement : pas de quoi faire une soumission solide aux Progress Prizes. L'équipe écrit qu'elle décourage les
  outils d'audit et de mesure seuls, et notre modèle affiné (AUC 0,79 sur PHerc0841) reste sous ceux déjà
  publiés (0,82 à 0,86 annoncés pour reader-v2, reader-v3 et hecate).

## Décisions qui t'appartiennent

1. **Arrêter la piste « étiquettes à la main » ?** Je recommande oui.
2. **Publier le résultat ?** Les faits pour un court message Discord sont dans `docs/DISCORD-FAITS.md`
   (message 3). Le message 1 (masques de validation) reste valable. Le message 2 n'a plus lieu d'être tel quel.
3. **La suite** : s'arrêter là, ou chercher autre chose. Je n'ai pas de piste sérieuse à te vendre aujourd'hui.
4. Pousser sur `main` ? Tout est sur la branche `claude/jolly-shannon-2xycqz`.

## À savoir

- La limite hebdomadaire d'usage de ton compte Claude a été atteinte cette nuit (remise à zéro à 2 h UTC). Mes
  agents de recherche et de relecture y ont largement contribué. Deux relecteurs sur trois ont été coupés par
  cette limite. Je n'en relance pas sans te le dire.
- Kaggle : 2 h 30 de GPU utilisées pour le pré-test, environ 1 h pour la branche `D`. Il reste environ 25 h
  jusqu'au 28/11.
