# Soumission Progress Prizes de novembre 2026 (préparée pour Jonathan)

Échéance : **30 novembre, 23 h 59 heure du Pacifique**, soit le **1er décembre à 8 h 59 à Paris**.
Formulaire : https://docs.google.com/forms/d/e/1FAIpQLSeB6MC_--4UCCEGc3zalX57-uE4puRcE_vJoYJCrEt4uYaaaw/viewform
(titre « November 2026 Progress Prizes », lu le 24/11).

Ce que tu soumets : le rapport `docs/label-source-comparison.md` et le code du dépôt.
Chiffres provisoires : ils seront mis à jour avec les runs de consolidation (branche `D` à 5 graines, branche
`S`, second checkpoint de départ). Je te préviendrai quand le texte est définitif.

## Avant d'envoyer

1. Relire le rapport (anglais). Ce qu'il dit en une phrase : sur les mêmes pixels, les étiquettes humaines de
   l'équipe et la carte du modèle 2 µm donnent le même modèle ; ce qui aide, c'est d'ajouter des segments de
   rouleaux nouveaux.
2. Me dire « pousse » pour mettre `main` à jour : le lien du formulaire pointe vers `main`.
3. Remplir le formulaire toi-même avec les réponses ci-dessous (à recopier ou à reformuler).

## Réponses proposées, champ par champ

**Your full name** : ton nom complet (je ne le connais pas).

**Team description** (proposition, à ajuster) :

> Individual submission (Jonathan8520). The code, experiments and write-up were produced with an AI coding
> assistant (Claude Code) working under my direction; I chose the questions, reviewed the results and wrote this
> form.

Pourquoi le mentionner : le `CONTRIBUTING.md` de villa demande de dire quand un LLM a écrit le travail, et le
serveur Discord a une règle sur l'IA. À toi de voir la formulation, mais je conseille de le dire.

**Discord display name** : ton pseudo (facultatif).

**URL** :

> https://github.com/Jonathan8520/vesuvius-ink-adapt (report: docs/label-source-comparison.md)

**What is your contribution?** (1) données, (2) en quoi ça aide à lire, (3) ce que ça permet de nouveau,
(4) preuves :

> (1) Data: two native 9 µm segments added as training data, PHerc0500P2 (layer --1, 9.362 µm, 113 keV) and
> PHerc0009B (auto_grown_20250919055754487_inp_hr, 8.64 µm, 116 keV), each with the team's human ink labels and
> the team's 2 µm model map (new_canon_autoresearch_recipe) on the same pixels; the ink_9um corpus as replay;
> evaluation on PHerc0841 (a scroll neither the starting checkpoint nor any arm saw) and on the nine reserved
> validation zones of ink_9um. No prize-eligible scroll was used.
>
> (2) It tells labellers and model builders where human effort pays off at 9 µm. Fine-tuning ink_9um with the
> team's human labels or with the team's registered 2 µm map, on exactly the same pixels and the same patches,
> gives the same model: +0.0002 AUC on PHerc0841 (95 % interval −0.005 to +0.005, 5 paired seeds), +0.0008 on
> the reserved zones. What helps is adding native segments from new scrolls: +0.04 AUC and +0.05 balanced
> accuracy on PHerc0841, whatever the label source. So new 9 µm training segments can be labelled with the
> registered 2 µm map instead of hours of hand labelling, and the scarce human time can go elsewhere.
>
> (3) It is the training-run comparison the maintainers asked for when closing villa PR #2381, and the first one
> we could find where only the label source changes. It contrasts with an earlier controlled test
> (moisescorreo/vesuvius-uncertainty-bench) that concluded the opposite, with its two label sources on different
> scans and segments.
> It comes with a paired fine-tuning bench for ink_9um (same patches per seed, any label source can be dropped
> in) and a CT-texture registration of the 2 µm map onto the native canvas (sub-pixel residual, checked against
> the team's labels published on both canvases), runnable on two free Kaggle T4 GPUs.
>
> (4) Evidence: per-segment and per-seed scores with paired block bootstrap intervals; controls (the published
> checkpoint reproduced exactly; a replay-only arm; a dense map arm with no human choice); a decision rule
> committed in git before the results were read; a script that rebuilds everything from public data; limits
> stated in the report (two segments, abbreviated recipe, evaluation labels drawn by the same team).

**Terms and Conditions** : cocher « Yes, I agree » (lis le texte : il faut rendre le code open source sous licence
permissive si tu gagnes ; c'est déjà le cas, MIT).

## Ce que j'attends réalistement

0 à quelques centaines de dollars. L'équipe écrit qu'elle décourage les outils d'audit et d'évaluation seuls. Le
point fort : c'est exactement la comparaison qu'un mainteneur a demandée, et elle change une décision pratique
(où mettre le temps humain).
