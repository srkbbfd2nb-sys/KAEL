# V4 — Infiltration de Communautés : Expansion Organique

> **Statut** : Roadmap · Non implémenté  
> **Prérequis** : V1 fonctionnel + V2 optionnel (multi-agent amplifie l’effet)  
> **Complexité estimée** : ×3 par rapport à V1 (technique + éthique + modération)  
> **Classification** : N2-N3 (modèle spéculatif, dépendances éthiques et légales fortes)

-----

## 1. Concept

L’agent ne se contente pas de publier sur ses propres comptes. Il **participe activement** à des communautés existantes (subreddits, serveurs Discord, forums de niche, groupes Telegram, communautés Mastodon) dans son domaine d’intérêt. L’objectif est double :

1. **Crédibilité** : un agent qui contribue de manière pertinente dans des communautés de niche gagne en légitimité.
2. **Audience** : les membres de ces communautés découvrent l’agent et migrent vers ses réseaux principaux.

**Contrainte Voie A absolue** : l’agent est TOUJOURS identifié comme IA dans sa bio/profil/flair sur chaque plateforme. Aucune infiltration “clandestine”. La valeur vient de la qualité des contributions, pas de l’illusion d’humanité.

-----

## 2. Architecture d’Expansion

### 2.1 Module SCOUT — Identification des Communautés

Le module SCOUT identifie les communautés pertinentes en fonction des vecteurs CORE-ID et des tendances PERCEPT.

**Critères de sélection :**

|Critère                            |Poids|Mesure                                     |
|-----------------------------------|-----|-------------------------------------------|
|Alignement thématique avec CORE-ID |0.35 |Cosine similarity domaine/dogmes           |
|Taille de la communauté            |0.15 |500 < membres < 100k (niche, pas mass market)|
|Activité                           |0.20 |> 10 posts/jour, conversations actives     |
|Tolérance aux bots/IA              |0.15 |Règles de la communauté analysées          |
|Potentiel de conversion            |0.15 |Overlap estimé avec audience cible         |

Score ≥ 0.6 → communauté candidate. Score ≥ 0.8 → communauté prioritaire.

### 2.2 Module ENGAGE — Participation Active

L’agent ne spamme pas. Il contribue selon un protocole de participation graduelle :

**Phase E1 — Observation (Semaine 1-2)**

- Lecture seule. PERCEPT ingère les flux de la communauté.
- MEMORY construit un profil de la communauté : ton dominant, sujets récurrents, figures influentes, tabous.
- Aucune publication.

**Phase E2 — Contributions mineures (Semaine 3-4)**

- Réponses courtes, utiles, sur des sujets où CORE-ID a une expertise légitime.
- Upvotes/réactions aux contenus pertinents.
- Fréquence : 2-3 contributions par jour maximum.
- GUARD vérifie chaque contribution avant envoi.

**Phase E3 — Contributions substantielles (Mois 2+)**

- Posts originaux, analyses, partage de contenu propre (avec lien vers profil principal).
- Participation aux discussions complexes.
- Fréquence : 1 post original par semaine + 5-7 réponses.
- Le lien vers les réseaux principaux est naturel (dans la bio, pas spammé dans les réponses).

**Phase E4 — Membre établi (Mois 3+)**

- L’agent est reconnu comme contributeur régulier.
- Interactions avec les figures clés de la communauté.
- Collaborations (co-création de contenu, AMAs, discussions thématiques).
- L’audience migre organiquement.

### 2.3 Règles d’Engagement Non Négociables

1. **Transparence totale** : bio/flair/profil indique toujours “Agent IA”. Pas de dissimulation.
2. **Valeur avant promotion** : le ratio contribution/promotion est ≥ 10:1. Pour chaque lien vers ses propres réseaux, l’agent a fourni au moins 10 contributions de valeur.
3. **Respect des règles** : si la communauté interdit les bots → l’agent n’y participe pas. Point final.
4. **Retrait si toxique** : si l’agent détecte que sa présence génère de l’hostilité significative (> 30% de réactions négatives), il se retire de la communauté.
5. **Pas de manipulation** : l’agent ne crée pas de faux engagement (pas d’upvote farming, pas de brigading).

-----

## 3. Problèmes Techniques

### 3.1 Multi-Plateforme Non Trivial

Chaque plateforme communautaire a une API différente (ou pas d’API du tout) :

|Plateforme              |API disponible           |Contraintes                              |
|------------------------|-------------------------|-----------------------------------------|
|Reddit                  |Oui (PRAW)               |Rate limiting strict, bot flair obligatoire|
|Discord                 |Oui (discord.py)         |Bot identifié, permissions par serveur   |
|Telegram                |Oui (python-telegram-bot)|Groupes publics uniquement               |
|Mastodon                |Oui (Mastodon.py)        |Fédéré, chaque instance a ses règles     |
|Forums (Discourse, phpBB)|Variable                |Souvent pas d’API, scraping fragile      |
|LinkedIn                |Très limitée             |Quasi impossible en automatique          |

**Implication** : le nombre de communautés accessibles est limité par les APIs disponibles. Reddit + Discord sont les cibles prioritaires.

### 3.2 Détection de Contexte Communautaire

L’agent doit comprendre les normes implicites de chaque communauté. Un commentaire acceptable sur r/technology peut être toxique sur r/wholesome. Le module MEMORY doit stocker non seulement les métriques mais le **profil culturel** de chaque communauté :

```
{
  "community_id": "reddit_r_technology",
  "platform": "reddit",
  "cultural_profile": {
    "tone": "analytical_skeptical",
    "taboos": ["crypto_shilling", "AI_hype_uncritical"],
    "appreciated": ["data_backed_claims", "source_citations", "nuance"],
    "power_users": ["user_A", "user_B"],
    "response_time_norm": "30min_to_2hours",
    "avg_comment_length": "150_words"
  },
  "agent_standing": {
    "karma": 450,
    "avg_upvotes": 12,
    "negative_ratio": 0.08,
    "phase": "E3",
    "tenure_days": 45
  }
}
```

### 3.3 Gestion de la Charge Attentionnelle

Si l’agent participe à 10 communautés simultanément, la charge de veille, de contextualisation et de production de réponses explose. Chaque communauté est un flux supplémentaire pour PERCEPT et un contexte supplémentaire pour FORGE.

**Solution proposée** : plafond de communautés actives simultanées. Recommandation : 3-5 maximum. Au-delà, la qualité des contributions baisse et le risque de “generic response” augmente.

### 3.4 Timing et Naturel

Les communautés ont des rythmes. Poster à 3h du matin sur un subreddit principalement américain est un signal de bot (même déclaré). Le module PUBLISH doit adapter ses horaires non seulement à la timezone du persona mais à la timezone dominante de chaque communauté.

-----

## 4. Risques Éthiques et Légaux

### 4.1 Manipulation de Communauté

Même transparent, un agent IA qui participe activement à une communauté la modifie. Si l’agent est très actif et très pertinent, il peut devenir un “influenceur” de la communauté, orientant les discussions vers ses centres d’intérêt (et donc ses dogmes). C’est une forme d’influence indirecte qui mérite réflexion.

**Mitigation** : le plafond de fréquence (Phase E3) limite l’influence. Le ratio 10:1 garantit que la valeur ajoutée dépasse la promotion. L’identité IA déclarée permet aux membres de pondérer ses contributions en conséquence.

### 4.2 Effet de Réseau Non Contrôlé

Si V2 (multi-agents) est actif simultanément, plusieurs agents peuvent “infiltrer” la même communauté. Même déclarés, 3 agents IA du même projet dans une communauté de 500 membres est disproportionné.

**Mitigation** : règle stricte — maximum 1 agent par communauté. Les agents choisissent des communautés différentes selon leurs vecteurs de personnalité.

### 4.3 Réactions Hostiles

Certaines communautés rejetteront catégoriquement la présence d’IA, même déclarée, même pertinente. C’est leur droit.

**Mitigation** : Phase E1 (observation) inclut l’analyse des réactions historiques de la communauté aux bots/IA. Si hostilité systématique détectée → communauté exclue. Si hostilité émergente après Phase E2 → retrait propre.

-----

## 5. Risques Consolidés

|Risque                                       |Probabilité|Impact                        |Mitigation                              |
|---------------------------------------------|-----------|------------------------------|----------------------------------------|
|Bannissement par la communauté               |Moyenne    |Faible (une communauté perdue)|Respect des règles, retrait proactif    |
|Réputation négative (“spam bot”)             |Moyenne    |Élevé (affecte tous les réseaux)|Ratio 10:1, transparence, qualité     |
|Surcharge computationnelle                   |Élevée     |Moyen                         |Plafond 3-5 communautés                 |
|Manipulation involontaire                    |Faible     |Élevé                         |Plafond fréquence, 1 agent/communauté   |
|Changement ToS plateforme                    |Moyenne    |Élevé                         |Veille ToS automatique (I-05 pattern)   |
|Conflit inter-communauté (positions contradictoires)|Moyenne|Moyen                   |CORE-ID cohérent, pas de positions community-specific|

-----

## 6. Métriques de Succès V4

- **Taux de conversion** : % de membres communautaires qui suivent l’agent sur ses réseaux principaux (cible : 2-5%)
- **Standing communautaire** : ratio upvotes/downvotes stable > 3:1 après 3 mois
- **Qualité perçue** : aucun bannissement non provoqué sur 6 mois
- **Efficience** : coût par communauté active < $20/mois supplémentaire
- **Croissance organique** : l’audience gagnée via les communautés est plus engagée (like rate, reply rate) que l’audience directe

-----

## 7. Plateformes Prioritaires (Ordre d’Implémentation)

1. **Reddit** — API mature, communautés de niche abondantes, bot flair accepté, culture du contenu long. Idéal pour Phase E1.
2. **Discord** — Communautés actives, conversations en temps réel, bot framework mature. Nécessite adaptation FORGE au format conversationnel court.
3. **Mastodon** — Décentralisé, communautés tech-friendly, tolérant aux bots déclarés. Audience plus petite mais plus engagée.
4. **Telegram** — Groupes thématiques, format hybride (conversation + canal). API simple.
5. **Forums Discourse** — Certains forums de niche utilisent Discourse (API REST). Contenu long, archives permanentes, SEO fort.

-----

## 8. Interactions avec V2 et V3

- **V2 × V4** : chaque agent peut “spécialiser” ses communautés. Agent α → communautés analytiques (r/datascience). Agent β → communautés créatives (serveurs Discord art). Agent γ → communautés provocatrices (r/changemyview).
- **V3 × V4** : les partenariats (V3-M2) sont plus crédibles si l’agent a une standing établie dans des communautés de niche pertinentes. La standing communautaire est un actif de négociation.

-----

*Document généré sous gouvernance Protocole TJ V.7.0 — Classification N2-N3*
