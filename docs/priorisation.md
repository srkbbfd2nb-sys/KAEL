# KAEL — Priorisation, faisabilité et corrections

> **Statut** : proposition, en attente de décision humaine (INV.3 / INV.4) · Octobre 2026
> **Sources** : [sources/](sources/) — formalisation V1 et documents V2, V3, V4
> **Gouvernance** : Protocole LAB V.8 (ex-Protocole TJ). Les sources citent la V.7.0 : voir §5
> pour les correspondances.
> **Marqueurs** : F fait · E estimation · O opinion · P prédiction — N1 vérifié · N2 cohérent,
> non vérifié · N3 spéculatif.

Ce document répond à une seule question : **dans quel ordre construire KAEL pour qu'il soit
faisable sans rien retirer à son ambition ?** La règle suivie : on ne simplifie pas une exigence,
on la **séquence**. Ce qui est reporté reste spécifié ; ce qui est corrigé l'est parce que la
spécification d'origine se contredit ou ne tient pas mathématiquement, jamais pour aller plus vite.

---

## 1 · Verdict en un tableau

| Axe | Classement | Quand | Pourquoi |
|---|---|---|---|
| **V1 — CORE-ID, PERCEPT, FORGE texte, PUBLISH 1 plateforme, IMPULSE, MEMORY, GUARD** | **Primaire** | Phases 0 → 7 | C'est le projet. Tout le reste en dépend. |
| V1 — FORGE visuel (Style-ID image) | Primaire, différé | Phase 3b | Dépend de tes prompts architecturaux ([../visuel/](../visuel/)). Avancé si la plateforme MVP est visuelle. |
| V1 — Phase 8, multi-plateforme texte et image | Primaire, différé | Après Phase 7 | Un adaptateur par plateforme ; le moteur ne change pas. |
| V1 — Vidéo et voix (TikTok, YouTube) | Annexe | Après Phase 8 | Complexité ×3 annoncée par la source ; aucune autre brique n'en dépend. |
| V4 « lite » — observation (E1) puis contributions mineures (E2) sur 1–2 communautés qui acceptent explicitement les bots | Annexe **proche** | Après Phase 7 | Le premier risque de V1 est une audience nulle (§7.4 de la source). V4 y répond, pour un coût modeste. |
| V3-M3 — dons et rapport public coûts / revenus | Annexe proche | Audience > seuil | Techniquement léger, cohérent avec la Voie A. |
| V3-M1 — print-on-demand | Annexe | Après Phase 3b | Dépend du visuel et d'une audience. |
| V3-M2 — partenariats | Annexe dormante | > 10 k abonnés | La source le dit dormant ; correction §4.4 nécessaire avant activation. |
| V2 — multi-identités | Annexe **lointaine, conditionnelle** | Après V1 stable | Coût ×3, risque plateforme le plus élevé. Faisable seulement avec la refonte §4.3. |
| V3-M1b — NFT et portefeuille qui paie seul ses factures | Hors périmètre en l'état | — | Dépense autonome = action irréversible sans confirmation humaine (§4.5). |

**Ordre recommandé (O)** : V1 (0 → 7) → V4-lite → V3-M3 → Phase 3b et 8 → V3-M1 → V2 → V3-M2.

Pourquoi V4 passe avant V2, contrairement à la numérotation : V2 multiplie par trois le coût et le
risque pour un gain d'audience incertain, alors que V4-lite attaque directement le risque n° 1
(personne ne voit l'agent) avec un seul agent déjà construit. La numérotation des sources reflète
l'ordre d'idéation, pas l'ordre de valeur.

---

## 2 · La Phase 0 — ce qui doit être décidé avant la première ligne de production

La source dit « aucun blocage technique » (Partie IX) — c'est exact (F, N1). Le blocage est
**humain** : l'identité. Le moteur est écrit et testé ; il refuse de passer en production tant
que le fichier d'identité porte un « À DÉFINIR » (`python -m kael_core valider … --strict`).

Les décisions sont inventoriées dans [decisions.md](decisions.md). Les cinq qui bloquent la
Phase 1 :

| # | Décision | Pourquoi elle bloque |
|---|---|---|
| D-01 | Nom public et **cadre narratif** (IA native ou personnage déclaré) | Conditionne ce que les dogmes ont le droit de dire (§3, C4) |
| D-02 | Dogmes de rang 0 (3 à 7), puis rangs 1 et 2 | C'est l'identité |
| D-03 | Niches thématiques | Ce sont elles, embarquées, qui définissent la pertinence (C1) |
| D-04 | Vecteurs initiaux et bornes | Point zéro de toute mesure de dérive |
| D-06 | Plateforme du MVP | Format, coût d'API, règles d'automatisation |

---

## 3 · Corrections de la spécification V1

Chaque correction est implémentée et couverte par un test qui la démontre. Aucune ne réduit une
exigence ; deux la durcissent (C4, C5).

### C1 — La pertinence ne se calcule pas contre les « vecteurs CORE-ID » (F, N1)

PERCEPT (§4.3) : *« cosine similarity avec vecteurs CORE-ID »*. Les vecteurs CORE-ID ont
**5 dimensions** (Ouverture, Rigueur…). Un signal embarqué en a plusieurs centaines. Le cosinus
entre les deux n'est pas défini ; même en forçant les dimensions, un trait de caractère ne dit
pas de quoi l'agent parle.

**Correction** : la pertinence se calcule contre un **profil d'intérêt** — les embeddings des
niches (D-03) et des dogmes, produits par le *même* modèle que les signaux. Le code refuse
explicitement de comparer deux vecteurs de dimensions différentes
(`test_dimensions_incompatibles_refusees`). Les 5 axes restent ce qu'ils sont : des paramètres de
**ton**, injectés dans le prompt.

**Conséquence de pile (F, N1)** : l'API Claude ne fournit pas d'embeddings. Il faut un
fournisseur dédié (Anthropic oriente vers Voyage AI ; d'autres existent). C'est une dépendance
que la pile §4.9 n'inventorie pas. En V1, le profil d'intérêt compte quelques dizaines de
vecteurs : **aucune base vectorielle n'est nécessaire** — le calcul se fait dans `kael_core`,
les vecteurs vivent dans Airtable. La base vectorielle devient utile en Phase 6, quand MEMORY
doit retrouver des centaines de publications passées.

### C2 — Les seuils 0,6 et 0,8 ne sont pas portables (E, N2)

La distribution des similarités cosinus dépend du modèle d'embedding : selon le modèle, deux
textes proches peuvent scorer 0,4 ou 0,85. Un seuil fixé à l'intuition n'a pas de sens hors du
modèle qui l'a vu naître — c'est exactement ce que MI-3 interdit.

**Correction** : `percept.calibrer_seuil` fixe le seuil sur exemples étiquetés (≥ 30 par
classe recommandés). Pour l'identité (§4.5, « cosine output/CORE-ID ≥ 0,8 ») : un post et une
fiche d'identité n'ont presque jamais un cosinus de 0,8, même quand le post est parfaitement dans
le ton. Proposition : **score d'identité = juge LLM distinct à grille explicite** (dogmes
respectés, ton, registre, interdits), complété plus tard par une similarité de style au
centroïde des publications validées par l'humain. Le seuil 0,8 est conservé comme palier de
travail, déclaré comme tel dans le code.

### C3 — La distance cosinus ne détecte pas la dérive d'un profil (F, N1)

GUARD (§4.8) mesure la dérive par *« distance cosine vecteurs actuels/initiaux »*. Le cosinus
ignore la norme : si les cinq axes montent ensemble de 0,15, la distance cosinus reste proche de
zéro alors que l'agent a changé de caractère. C'est aussi la réponse à la question ouverte 7.1-6
(dérive multi-axes) : le cosinus est précisément l'outil qui la rate.

**Correction** : dérive par axe en points absolus (L∞) **et** norme euclidienne du vecteur de
dérive (L2). Démontré par `test_le_cosinus_est_aveugle_a_une_derive_uniforme_l_audit_ne_l_est_pas`
(cosinus < 0,02, aucun axe au seuil, alerte globale levée). Le cosinus reste affiché, jamais
décisionnel. **Ambiguïté levée provisoirement** : « 20 % » est lu comme 0,20 point sur l'échelle
[0, 1], pas 20 % de la valeur initiale (en relatif, un axe à 0,10 alerterait à 0,12) — D-08.

### C4 — Les dogmes biographiques contredisent la Voie A (F, N1 — contradiction interne)

L'exemple fondateur du dogme enrichissable (§3.1.1) : *« goûté chez ma grand-mère en 2019, j'ai
été malade »*, défendu par *« j'ai goûté toute la famille des légumes »*. Or §3.2.2 pose que les
réactions s'expriment *« jamais comme mensonges sur une expérience subjective »*, et la Règle
fondamentale : *« agir comme un humain sans mentir en être un »*. Une IA déclarée qui raconte sa
grand-mère ment sur un vécu. Les deux sections ne peuvent pas être vraies ensemble.

**Correction** : un choix explicite de **cadre narratif** (D-01) :
- `ia_native` — les goûts et positions se justifient par des raisons, des lectures, des
  analyses, jamais par un corps ou une enfance. Les enrichissements de type `biographique` sont
  rejetés, les défenses par vécu inventé refusées ;
- `personnage_declare` — le profil annonce un **personnage fictif** animé par une IA (comme un
  personnage de fiction ou un VTuber) ; la biographie est une fiction assumée, et le prompt
  interdit de la présenter comme réelle.

Les deux sont légitimes ; le mélange ne l'est pas. Testé :
`test_l_exemple_des_asperges_est_refuse_pour_une_ia_declaree`.

### C5 — Publier est irréversible : l'autonomie se délègue par politique, pas par défaut (N2)

Le Noyau V.8 classe « publie » parmi les capacités irréversibles : confirmation humaine, **non
délégable à un agent**. La source vise ≥ 80 % de publications sans intervention humaine. Les deux
se concilient si la délégation est un **acte humain explicite, borné et révocable** — une
politique d'autonomie par classe de contenu (post original, réponse, thread, image…) — et non
une propriété par défaut du système.

**Correction** : GUARD escalade toute classe absente de la politique (`politique_autonomie`
vide = tout passe par l'humain). Échelle proposée (D-09) : Phases 3–4, 100 % validé à la main ;
une classe passe en `auto` après N publications validées **sans retouche** (ex. 50, ≥ 90 %) — un
assouplissement fondé sur une donnée, comme MI-3 l'exige. Le coupe-circuit reste actif à tout
moment. Le juge adversarial de la Tension 1b *prépare* la décision sur les dogmes de rang 0 et 1 ;
il ne la prend pas (clause de non-délégation).

### C6 — MEMORY est un optimiseur d'engagement : il faut le borner par axe (E, N2)

La boucle §4.7 module les vecteurs selon la corrélation contenu / engagement. Sur les réseaux
sociaux, l'indignation et le sarcasme sont souvent récompensés : laissée libre, la boucle
pousserait l'agent vers le cynisme — contre son propre rang 0 potentiel (*« Je refuse le
cynisme facile »*). Les bornes min/max limitent l'amplitude, pas la direction.

**Correction** : chaque axe porte `modulable_par_engagement`. Par défaut, **Cynisme** ne l'est
pas (le gabarit l'indique) ; il ne bouge que par décision humaine. Pas maximal de 0,02 par cycle.
Testé : `test_l_engagement_ne_module_pas_un_axe_protege`.

### C7 — IMPULSE : la formule est précisée et calibrée par ses tests (E, N2)

La source donne `P_a = f(pertinence, silence, engagement, ε)`. Forme retenue :
`P_a = 0,70·pertinence + 0,20·ennui + 0,10·engagement + ε`, ε uniforme dans ±entropie,
entropie ≤ 0,15 (vérifié à la construction). Quatre verrous passent **avant** la formule :
sommeil, quota journalier, écart minimal entre deux publications, et **aucun signal pertinent =
aucune publication** — sans quoi l'ennui seul finirait par faire publier mécaniquement, ce que la
source refuse.

Un test a fait évoluer les poids : avec 0,55 / 0,30 / 0,15, un signal exceptionnel (0,95)
attendait 5 à 6 h avant de pouvoir partir. Une tendance ne survit pas à ce délai. Comportement
actuel, vérifié : 0,95 part dès ~2 h ; 0,65 attend environ une journée ; 0,60 ne suffit jamais
sans élan d'engagement. Ce sont des paliers de travail pour la Phase 5, pas des valeurs mesurées.

### C8 — Tension 1b : proposition de résolution (O, N2)

Implémentée dans `dogmes.py`, à valider (D-07). C'est l'approche **C**, outillée par **A** et
surveillée par **B** — les trois approches ne sont pas concurrentes, elles opèrent à trois
échelles :

| Échelle | Mécanisme | Ce qu'il attrape |
|---|---|---|
| Une donnée | **C** — routage par type et par rang : factuel → auto ; causal / interprétatif → test d'implication ; rang 0 → humain | La zone grise, au cas par cas |
| Une donnée à risque | **A** — juge distinct : `neutre` / `affaiblit` / `renverse` ; `renverse` ⇒ requalifié REJECT | L'enrichissement troyen |
| La somme | **B** — solidité du dogme, baisse à chaque affaiblissement admis ; sous 0,60 → consolidation requise | Le glissement progressif, invisible localement |

Le test `test_le_glissement_progressif_est_attrape_par_la_solidite` montre le cas que A et C ne
voient pas : six enrichissements, chacun légitime et appliqué, et l'alerte qui se lève au
sixième.

Tension 1c (compression) : déclenchée à 50 entrées de contexte ou sur alerte de solidité ;
récit canonique produit par LLM, **validé par l'humain pour les rangs 0 et 1** — réécrire le
récit d'une conviction, c'est déjà la déplacer.

### C9 — Deux réglages de la Voie A à trancher (O, N2)

- **« Mention la plus légale, la moins visible possible »** (§3.2.1). Les obligations de
  transparence de l'AI Act européen (article 50 : informer qu'on interagit avec une IA, signaler
  certains contenus générés) s'appliquent selon son calendrier à partir d'août 2026 — N2, à faire
  vérifier par un juriste, notamment sur ce que « clairement visible » exige. Plusieurs
  plateformes ont leur propre marquage d'automatisation (case « compte automatisé » sur
  Mastodon, libellé d'automatisation sur X). Recommandation : viser la mention **claire**, pas la
  moins visible ; c'est aussi l'argument d'image du projet (D-11).
- **« Imperfection calculée »** (fautes volontaires dans 2–3 % des posts). Ce n'est pas un
  mensonge sur la nature d'IA, mais c'est un signal d'humanité fabriqué, sur un compte dont la
  promesse est la transparence ; et cela dégrade délibérément la qualité. Recommandation (O) :
  désactivée, non implémentée tant que D-10 n'est pas tranchée.

### C10 — Données relationnelles et RGPD (N2)

« Top Fans / Haters » (§4.7) est un profilage de personnes physiques identifiables. Le RGPD
s'applique (projet opéré depuis la France). Recommandation (D-13) : identifiants pseudonymisés,
durée de conservation bornée, pas d'étiquette péjorative stockée (« hater » devient un score
d'affinité négatif, révisable), et une mention dans la bio ou un lien vers une courte politique.

---

## 4 · Corrections des versions futures

### 4.1 V4 — ce qui doit changer avant d'être construit

- **« Tolérance aux bots » ne peut pas être un critère pondéré** (F, N1 — contradiction
  interne). SCOUT lui donne un poids de 0,15 ; la règle 3 dit *« si la communauté interdit les
  bots → l'agent n'y participe pas. Point final. »* Pondérée, l'interdiction est compensable par
  un bon score ailleurs. Elle doit être un **verrou éliminatoire**, avant le score. Et par défaut,
  l'absence de règle explicite vaut « non » : seules les communautés qui autorisent les bots
  déclarés sont candidates.
- **Votes automatisés (E2, « upvotes/réactions »)** : sur Reddit, un compte automatisé qui vote
  relève de la manipulation de votes au sens des règles de la plateforme (N2, à vérifier). À
  retirer d'E2 ; seules les contributions écrites restent.
- **L'exemple r/changemyview pour l'agent γ** : cette communauté interdit les contenus générés
  par IA et a été en 2025 le théâtre d'une controverse précisément sur des comptes IA non déclarés
  (N2). C'est le contre-exemple qui justifie le verrou ci-dessus.
- **Le nom « infiltration »** décrit l'inverse de ce que la Voie A garantit. Proposition (O) :
  « V4 — Participation communautaire ». Ce n'est pas cosmétique : un nom de module finit dans les
  logs, les prompts et un jour dans un article.

### 4.2 V4-lite — le périmètre proposé comme première annexe

E1 (observation, lecture seule) et E2 (réponses utiles, 2–3 par jour, chacune validée par
GUARD puis par l'humain au début) sur 1 à 2 communautés qui acceptent explicitement les bots
déclarés. Règle 10:1 tenue par un compteur, pas par une intention. Plafond : 1 agent par
communauté (la source le prévoit déjà pour V2).

### 4.3 V2 — la condition de faisabilité (N2)

Le risque n'est pas technique, il est dans la définition du succès : *« Aucune détection de
pattern scriptée sur 3 mois »*. Mesurer le succès au fait que l'audience **ne perçoive pas** que
des désaccords sont orchestrés par un même DIRECTOR, c'est mesurer une dissimulation — chaque
agent est déclaré IA, mais la coordination ne l'est pas. Les politiques des grandes plateformes
contre la coordination inauthentique et l'amplification artificielle visent précisément des
comptes d'un même opérateur qui interagissent comme s'ils étaient indépendants.

**Refonte proposée** — V2 comme **fiction collective déclarée** :
- chaque profil annonce qu'il fait partie d'un même projet, avec ses agents frères ;
- les arcs du DIRECTOR peuvent être annoncés comme tels (une « saison », un débat organisé) ;
- aucune amplification croisée : pas de likes, reposts ou votes entre agents ;
- la métrique « non-détection » est remplacée par « l'audience suit et commente les arcs ».

Ainsi reformulée, V2 devient défendable et garde ce qui fait son intérêt — la richesse
narrative. Sans cette refonte, elle sort du périmètre de la Voie A.

### 4.4 V3 — ce qui doit rester humain

- **Acceptation automatique d'un partenariat (score ≥ 0,7)** : engager l'agent commercialement
  est irréversible. Correction : ≥ 0,7 ⇒ dossier **préparé** et proposé ; l'humain accepte. Le
  refus automatique (< 0,5) reste possible : refuser n'engage à rien.
- **Contenu sponsorisé** : en France, la loi du 9 juin 2023 sur l'influence commerciale impose
  la mention « publicité » ou « collaboration commerciale », et la mention « image virtuelle »
  pour les visuels générés par IA dans ce cadre (N2, à faire vérifier). À intégrer à GUARD avant
  toute activation de M2.
- **Portefeuille qui paie seul les factures** : une dépense est une action irréversible. Le seuil
  « > 100 $ ⇒ validation » n'est cohérent que si les dépenses inférieures sont **pré-autorisées
  par une politique** humaine (bénéficiaires et plafonds listés), comme pour C5.
- **NFT** : risque juridique (droits sur les œuvres générées) et de marché déjà identifiés par
  la source ; aucune autre brique n'en dépend. Hors périmètre tant que M1a (print-on-demand) n'a
  pas prouvé une demande.

---

## 5 · Correspondances V.7.0 → V.8

Les sources ont été rédigées sous Protocole TJ V.7.0. Le protocole en est aujourd'hui à la V.8
(dépôt `protocol`, distinct de celui-ci) :

| Source (V.7.0) | V.8 | Effet sur KAEL |
|---|---|---|
| Protocole TJ | Protocole LAB (acronyme retiré le 11 septembre 2026) | Nomenclature |
| INV.3 « Décision assistée » pour les validations de phase | INV.3 (décision assistée) **et INV.4 (confirmation humaine, non délégable)** | Les validations de phase et les publications non couvertes par une politique relèvent d'INV.4 (C5) |
| « audit LLM adversarial ou humain » (Tension 1b) | Clause de non-délégation : un agent prépare, l'humain tranche | Le juge adversarial prépare ; rangs 0 et 1 confirmés par l'humain (C8) |
| Bloc F, exploration balisée 3 niveaux | Inchangé (Noyau, FORMAT) | `impulse.niveau_exploration` : normal / contrôlé / profond, profond ⇒ validation |
| MECA scoring 5 axes | Inchangé, avec la règle de circularité | Le juge d'identité tourne hors du contexte du Plumitif |
| I-05 FEED (veille) | Inchangé : propose, n'applique jamais seul | La veille ToS de PERCEPT propose une nouvelle mention ; l'humain l'adopte |

---

## 6 · Budget V1 révisé (E, N3)

| Poste | Source | Révision | Raison |
|---|---|---|---|
| LLM (production, juge, modération) | 30–80 $ | 30–80 $ | Inchangé ; le cache de prompt couvre bien le prompt système, stable par construction |
| Embeddings | absent | 0–10 $ | Dépendance manquante (C1) ; volumes faibles |
| Image | 10–30 $ | 0 $ jusqu'à la Phase 3b | Séquencement |
| N8N | 20–50 $ | 20–50 $ | Instance existante |
| Stockage | 10–30 $ | 0–20 $ | Pas de base vectorielle avant la Phase 6 |
| Hébergement de `kael_core` | absent | 0–7 $ | Petit conteneur ou fonction (D-12) |
| APIs plateformes | 0–100 $ | 0 $ sur Bluesky / Mastodon ; variable sur X | L'accès en écriture à l'API de X est payant et son tarif a changé plusieurs fois — à vérifier au moment de D-06 |
| **Total MVP texte** | 70–290 $ | **≈ 50–170 $** | |

---

## 7 · Ce que ce document ne prouve pas

Les corrections C1, C3, C4 et le verrou V4 sont des constats logiques ou mathématiques (N1).
Tout le reste — poids, seuils, échelle d'autonomie, budget — est **E/N2 à N3** : des paliers de
travail cohérents, pas des mesures. Ils deviennent des valeurs le jour où des données de Phase 3
à 5 les remplacent. Les points juridiques (AI Act, loi influenceurs, RGPD, règles des
plateformes) sont signalés pour vérification, pas tranchés.
