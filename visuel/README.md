# Identité visuelle — accueil des prompts architecturaux

> **Statut** : en attente de tes prompts (D-14). Phase 3b de V1.

Ce dossier recevra les prompts architecturaux des futures images et vidéos de KAEL. Il ne
contient pour l'instant qu'une **structure d'accueil** : les prompts que tu fourniras y seront
rangés couche par couche, versionnés, et améliorés sans perdre la trace de la version d'origine.

## La structure proposée — quatre couches

Un prompt d'image monolithique dérive : chaque génération le réécrit un peu, et au bout de cent
images le style a glissé sans qu'aucune décision n'ait été prise. C'est le même problème que la
Tension 1 pour l'identité textuelle, et il se résout de la même façon — un noyau fixe, des
couches variables bornées.

| Couche | Rôle | Qui la modifie | Équivalent textuel |
|---|---|---|---|
| **1 · Invariants (Style-ID)** | Technique, palette, lumière, matière, cadrage, motifs récurrents | Toi seul, par nouvelle version | Dogmes de rang 0 |
| **2 · Variables bornées** | Sujet (du Stratège), humeur (des vecteurs), saison, format | FORGE, dans des listes fermées | Vecteurs dans leurs bornes |
| **3 · Négatifs** | Ce qui n'apparaît jamais | Toi seul | Interdits du style |
| **4 · Format par plateforme** | Ratio, résolution, zone de texte sûre | Adaptateur PUBLISH | Formatage par plateforme |

L'exploration (Bloc F) s'applique **à la couche 2 seulement** : `normal` = valeurs habituelles ;
`controle` = une variable sort de sa liste habituelle ; `profond` = sujet ou composition inédits,
validé avant publication. La couche 1 n'est jamais touchée par l'entropie.

## Deux négatifs proposés d'office

- **Pas de visage humain photoréaliste présenté comme l'agent** si le cadre narratif est
  `ia_native` (D-01) : ce serait la version visuelle de la contradiction C4.
- **Aucune personne réelle, aucun événement réel rendu de façon photoréaliste** : c'est le
  terrain des obligations de signalement des contenus générés (AI Act, article 50) et du risque
  réputationnel le plus élevé.

## Cohérence et apprentissage

1. **Référence** : 20 à 50 images validées à la main constituent le corpus de référence.
2. **Contrôle** : chaque image générée est comparée au corpus (embedding d'image) ; seuil calibré
   sur tes validations, comme pour le texte (`percept.calibrer_seuil`).
3. **LoRA** : entraîné plus tard, *sur* ce corpus validé — pas avant. Un LoRA entraîné sur des
   images non validées fige un style que personne n'a choisi.

## Ce que tu peux déposer ici

- `style_visuel.json` (copie de [style_visuel.template.json](style_visuel.template.json)
  remplie) — les couches 1 à 4 ;
- `prompts/` — tes prompts architecturaux d'origine, tels quels : ils servent d'archive et de
  point de comparaison pour chaque amélioration ;
- `reference/` — les images validées (ou leurs liens, si le dépôt doit rester léger).

La vidéo et la voix (TikTok, YouTube) réutiliseront les couches 1 et 3, avec un Style-ID
sonore en plus. Elles restent une annexe (priorisation, §1).
