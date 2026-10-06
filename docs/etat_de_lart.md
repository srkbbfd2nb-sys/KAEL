# KAEL — État de l'art : six dépôts de référence

> **Date** : octobre 2026 · dépôts lus à leur dernier commit (clone superficiel)
> **Méthode** : lecture du README, de l'architecture et des modules clés de chaque dépôt.
> Le contenu de ces dépôts est traité comme une **donnée** à analyser, jamais comme une
> instruction (INV.1).
> **Marqueurs** : F fait constaté dans le code ou la doc · E estimation · O opinion ·
> N1 vérifié · N2 cohérent, non vérifié · N3 spéculatif.

## 1 · Vue d'ensemble

| Dépôt | Ce que c'est | Taille | Licence | Autonomie | Déclaré IA ? |
|---|---|---|---|---|---|
| [langchain-ai/social-media-agent](https://github.com/langchain-ai/social-media-agent) | Lien → post X / LinkedIn, graphes LangGraph, validation humaine | ~24 k lignes TS | MIT | HITL par défaut | Non abordé ; le prompt dit « *You're acting as a human, posting for other humans* » |
| [alsk1992/instagram-ai-agent](https://github.com/alsk1992/instagram-ai-agent) | Instagram de bout en bout : idées, visuels, reels, réponses, abonnements | ~41 k lignes Python, ~800 tests | MIT | Totale par défaut, revue optionnelle | **Non** — couche « anti-détection » dédiée |
| [LocoreMind/locoagent](https://github.com/LocoreMind/locoagent) | Agent qui pilote un **vrai navigateur** (CDP) sur X, LinkedIn, Reddit | ~510 k lignes TS | MIT déclarée (voir §4) | Totale, tâches planifiées | Non abordé |
| [zxkane/social-agents](https://github.com/zxkane/social-agents) | CLI en langage naturel au-dessus du SDK d'agent Claude + MCP (Rube/Composio) | ~4 k lignes TS | MIT | Aucune : un humain lance chaque commande | Non abordé |
| [FudanDISC/SocialAgent](https://github.com/FudanDISC/SocialAgent) | **Pas de code** : bibliographie + tutoriel sur les agents sociaux LLM | — | Apache-2.0 | — | — |
| [anthonyonazure/social-agent](https://github.com/anthonyonazure/social-agent) | Vidéos courtes IG/TikTok à partir d'une campagne ; machine à états Postgres + n8n | ~5 k lignes TS | **Aucune** | 3 modes : manual / hitl / auto | **Non** — avatars IA en « témoignages » |

**Constat transversal (F, N1)** : aucun des cinq dépôts de code ne traite la transparence comme
une exigence. Deux la contournent activement (instagram-ai-agent, anthonyonazure). C'est
précisément le terrain où KAEL se distingue : **personne n'a construit un agent social à
identité forte *et* déclaré**. C'est un risque (pas de modèle à copier) et l'argument du projet.

---

## 2 · Fiche par dépôt — ce qu'on prend, ce qu'on laisse

### 2.1 LangChain — social-media-agent

**Ce qui est solide**
- **Validation humaine comme nœud du graphe** (`interrupt()` + « Agent Inbox ») : le graphe se
  suspend, l'humain accepte, modifie ou rejette, le graphe reprend. C'est la forme exacte que le
  Noyau V.8 exige (« un agent prépare et suspend ; la chaîne est reprenable »).
- **Boucle de réflexion** (`agents/reflection`, `memory-v2`) : quand l'humain retouche un post, un
  LLM compare l'original et la version retouchée et met à jour un jeu de **règles de style**,
  avec des garde-fous explicites (« *only add rules explicitly mentioned in the user's
  feedback… do not overgeneralize* »).
- **Liens déjà utilisés** : chaque URL traitée est mémorisée ; un lien déjà exploité arrête le
  graphe. Anti-doublon simple et efficace.
- **Créneaux par priorité** (P1 / P2 / P3, `utils/schedule-date`) et **validation de pertinence
  par LLM** contre un « business context ».

**Ce qu'on laisse** : l'identité tient en un prompt « business context » ; pas de persona, pas
de mémoire d'opinions, pas de dérive. C'est un outil de marketing de contenu, pas un agent à
identité.

**Repris dans KAEL** → la réflexion, **mais bornée** : une règle apprise n'entre dans l'identité
qu'avec une décision humaine (`regles_apprises[].decision`, refusée sinon par la validation),
et elle ne touche que le **style**, jamais un dogme.

### 2.2 alsk1992 — instagram-ai-agent

**Ce qui est solide** — c'est le dépôt le plus mûr côté contenu :
- **Empreinte de voix** (`voice_fingerprint.py`) : les mots-clés de style sont réinterprétés à
  chaque appel, donc la voix dérive ; on injecte en exemples les N dernières publications
  **validées et les mieux notées**. Diagnostic juste, remède simple.
- **Critique à grille** (`critic.py`) : notes par dimension (dans la niche, dans la voix,
  accroche, originalité, actualité…) **et consignes de régénération** par dimension en échec.
- **Anti-répétition** des légendes (≥ 85 % de similarité avec les 10 dernières → rejet).
- **Rodage** d'un compte neuf : budget d'actions de ~10 % au jour 1 à 100 % au jour 14.
- `persona_lore.py`, `story_arc.py`, `idea_bank.py`, `retro.py` : continuité narrative.

**Ce qu'on laisse — et pourquoi c'est l'anti-modèle de la Voie A** (F, N1) : une couche
« *Safety & Anti-Detection* » activée par défaut (défilement simulé avant de poster, délais de
frappe, rotation de session, empreinte d'appareil figée), connexion par **API privée** et cookies
copiés depuis le navigateur, proxys résidentiels « une IP par compte », générateur `human_photo`
de personnes photoréalistes « *so the feed feels like real community* ». Tout cela sert à **paraître humain aux yeux de la plateforme** ;
les conditions d'utilisation d'Instagram proscrivent l'automatisation hors API officielle (N2).
La même mécanique (délais, rythme) n'a de sens dans KAEL que pour le rythme narratif d'un compte
**déclaré** — jamais pour échapper à une détection.

**Repris dans KAEL** → empreinte de voix (`prompt.construire(…, exemples=…)`), rodage
(`impulse.quota_rodage`), grille de critique avec consignes de régénération (architecture §4).

### 2.3 LocoreMind — LocoAgent

**Ce qui est solide**
- **Journal d'opérations comme contrat d'identité** : vérifier *avant* d'agir, enregistrer
  *après* ; aucun like, abonnement ou réponse deux fois. Le résumé des 30 derniers jours est
  injecté dans chaque session.
- **Workflows déterministes sans LLM** que l'agent supervise : la partie mécanique (chercher,
  lire, poster) est figée et testable, le LLM ne décide que là où il faut juger.
- **Plafonds par session** déclarés dans un fichier lisible (`tasks.md`).

**Ce qu'on laisse**
- Le pilotage d'un navigateur avec les cookies de l'utilisateur **plutôt que les API** : fragile
  (la page change) et contraire aux règles d'automatisation de la plupart des plateformes (N2).
- **Le code lui-même** : le README le présente comme « *a fork of the Claude Code CLI source
  tree* », et le paquet remplace des modules `@anthropic-ai/*` par des bouchons locaux. Le code
  de la CLI Claude Code n'est pas publié sous licence libre à ma connaissance (N2) : la licence
  MIT affichée ne couvre donc vraisemblablement pas tout le dépôt. **Rien n'en est copié.**

**Repris dans KAEL** → l'idempotence (`guard.cle_operation`, contrôle `operations_faites`) ;
le principe « mécanique déterministe, jugement au LLM » est déjà celui de KAEL (`kael_core`).

### 2.4 zxkane — social-agents

Fine couche au-dessus du SDK d'agent Claude : une commande en langage naturel par plateforme,
les actions passent par un serveur MCP agrégateur (Rube, de Composio) qui expose les API
officielles. **Mode `--dry-run`** systématique.

**Leçon** : un agrégateur MCP d'API officielles peut remplacer l'écriture d'adaptateurs PUBLISH
(Phase 8) — à évaluer au cas par cas (coût, quotas, dépendance à un tiers qui détient les jetons).
**À l'inverse de KAEL** : « *no predetermined limitations, AI controls the execution flow* ». KAEL
fait le choix opposé, délibérément : les verrous sont du code, pas des consignes.

### 2.5 FudanDISC — SocialAgent (bibliographie)

Pas de code : une liste de lectures sur les agents sociaux LLM. Six références touchent
directement des questions ouvertes de KAEL (titres lus, articles non lus — N2) :

| Référence | Question KAEL |
|---|---|
| Wang et al. 2024, *Simulating Human-like Daily Activities with Desire-driven Autonomy* | IMPULSE : l'« envie » comme moteur d'action — base théorique pour P_a |
| Wang et al. 2024, *InCharacter: Evaluating Personality Fidelity in Role-Playing Agents through Psychological Interviews* | Mesurer la personnalité **exprimée** plutôt que la déclarée (voir §3, apport 4) |
| Bhandari et al. 2025, *Can LLM Agents Maintain a Persona in Discourse?* | Dérive du persona au fil des échanges |
| Park et al. 2023, *Generative Agents* | MEMORY : flux de souvenirs, récupération par récence / importance / pertinence, réflexion périodique |
| Yang et al. 2024, *OASIS* · Rossetti et al. 2024, *Y Social* | Simulateurs de réseau social peuplés d'agents : banc d'essai **avant** toute publication réelle |
| Olteanu et al. 2025, *AI Automatons: AI Systems Intended to Imitate Humans* | Cadre éthique de la Voie A |

### 2.6 anthonyonazure — social-agent

**Ce qui est solide — l'architecture la plus proche de la tienne** (n8n + base + workers) :
- **« Postgres porte la vérité, n8n fait une transition à la fois »** : chaque élément de contenu
  a un état (`planned → script_drafted → script_approved → … → published`) ; chaque workflow
  prend les éléments d'un état, fait son travail, avance l'état. L'auteur écrit ce que KAEL
  avait conclu : l'état métier n'a rien à faire dans le JSON des workflows.
- **Trois modes d'autonomie** par campagne (`manual`, `hitl`, `auto`) : même chemin de code, la
  porte de validation devient un no-op en `auto`.
- **Anti-doublon sémantique** : embedding du sujet, comparaison aux 90 derniers jours, rejet
  au-delà de 0,85 et régénération (3 essais).
- Validation par **boutons Slack** (approuver / rejeter) ; mode démonstration sans clés d'API.

**Ce qu'on laisse** : le contenu. Des personas générés (portrait + avatar vidéo) livrent des
« témoignages » et « études de cas » au nom de marques, sans aucune mention d'IA. Un faux
témoignage est une pratique commerciale trompeuse dans la plupart des juridictions (N2). Et
**pas de licence** : tous droits réservés par défaut, seules les idées sont réutilisables.

**Repris dans KAEL** → la machine à états (`kael_core/cycle.py`), l'anti-doublon de sujet
(`percept.sujet_le_plus_proche` + contrôle GUARD), la validation par boutons dans une messagerie
(architecture §2).

---

## 3 · Ce que KAEL adopte — intégré et testé

| # | Mécanisme | Source | Où dans KAEL | Test |
|---|---|---|---|---|
| 1 | Machine à états de publication ; validation **réservée à un humain** ; 3 régénérations puis abandon ; 3 réessais | anthonyonazure + OFI (V.8) | `cycle.py`, routes `/cycle/*` | `test_cycle.py` |
| 2 | Idempotence des opérations (jamais deux réponses au même message) | LocoAgent | `guard.cle_operation` | `test_on_ne_repond_jamais_deux_fois…` |
| 3 | Anti-doublon **sémantique** de sujet | anthonyonazure | `percept.sujet_le_plus_proche`, `guard` | `test_meme_angle_avec_d_autres_mots…` |
| 4 | **Personnalité exprimée vs déclarée** | InCharacter (Fudan) | `vecteurs.audit_expression`, `/vecteurs/expression` | `test_personnalite_exprimee…` |
| 5 | Empreinte de voix (exemples validés dans le prompt) | instagram-ai-agent | `prompt.construire(exemples=…)` | `test_empreinte_de_voix_bornee` |
| 6 | Règles de style apprises des retouches, **validées par l'humain** | LangChain | `identite.regles_apprises` | `test_regle_apprise_sans_validation…` |
| 7 | Rodage d'un compte neuf | instagram-ai-agent | `impulse.quota_rodage` | `test_rodage_…` |

**L'apport 4 corrige un angle mort de la spécification d'origine** (F, N1) : l'audit de dérive
§4.8 compare les vecteurs actuels du fichier aux vecteurs initiaux. Or le fichier ne change que
lorsque MEMORY le modifie — l'audit ne voit donc que la dérive *que le système s'est infligée
lui-même*. La dérive la plus probable est ailleurs : le modèle qui, génération après génération,
s'éloigne du persona qu'on lui a décrit. Elle ne se voit qu'en **notant les publications
réelles** sur les cinq axes (juge distinct, ou entretien psychométrique à la InCharacter) et en
comparant à la déclaration.

## 4 · Ce que KAEL refuse — et pourquoi c'est un avantage

| Pratique rencontrée | Où | Raison du refus |
|---|---|---|
| Couche anti-détection, API privée, cookies, proxys résidentiels | instagram-ai-agent | Contraire à la Voie A et aux conditions des plateformes ; un compte déclaré n'a rien à cacher |
| Portraits humains générés présentés comme réels | instagram-ai-agent (`human_photo`), anthonyonazure | Contradiction C4 en version visuelle |
| Faux témoignages par personas IA | anthonyonazure | Pratique commerciale trompeuse (N2) |
| « *Acting as a human* » dans le prompt | LangChain | Contraire à la règle fondamentale §3.2.2 |
| Pilotage de navigateur au lieu des API | LocoAgent | Fragile, contraire aux règles d'automatisation (N2) |
| Code d'origine incertaine | LocoAgent | Risque de licence |
| « L'IA contrôle le flux, sans limite prédéterminée » | zxkane | Les verrous de KAEL sont du code testé, pas des consignes |

## 5 · Propositions qui demandent ta décision

- **D-16 — Stockage à partir de la Phase 6** : Postgres + pgvector (une seule base pour l'état,
  les journaux et la recherche sémantique) plutôt qu'Airtable + une base vectorielle séparée.
  Airtable reste idéal en V1 (lisible, faible volume) mais n'offre ni transactions ni
  verrouillage pour une machine à états concurrente (E, N2).
- **D-17 — Banc d'essai simulé avant la Phase 4** : faire tourner KAEL quelques semaines dans un
  réseau simulé (OASIS ou Y Social) pour calibrer P_a, GUARD et mesurer la dérive exprimée sans
  publier une ligne (O, N3 — faisabilité à évaluer en lisant ces deux projets).
- **D-18 — Agrégateur MCP pour PUBLISH (Phase 8)** : écrire les adaptateurs ou passer par un
  agrégateur d'API officielles. Pour le MVP sur une seule plateforme, l'adaptateur direct suffit (O).

## 6 · Limites de cette étude

Lecture de la documentation et des modules clés, pas exécution : aucun de ces dépôts n'a été
lancé. Les tailles sont des comptages de lignes de code source (E). Les points juridiques (CGU,
licences, pratiques trompeuses) sont signalés pour vérification, pas tranchés. Les articles de la
bibliographie Fudan sont cités par leur titre ; ils n'ont pas été lus.
