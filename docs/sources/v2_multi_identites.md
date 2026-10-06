# V2 — Multi-Identités : Le Réseau de Personas

> **Statut** : Roadmap · Non implémenté  
> **Prérequis** : V1 single-agent fonctionnel (CORE-ID → GUARD validé)  
> **Complexité estimée** : ×3 par rapport à V1  
> **Classification** : N2 (modèle cohérent, non vérifié empiriquement)

-----

## 1. Concept

Créer non pas un, mais **plusieurs agents** qui coexistent dans le même écosystème social. Chaque agent possède son propre CORE-ID (dogmes, vecteurs, style). Les agents interagissent entre eux publiquement — collaborations, désaccords, débats — créant une dynamique sociale organique qui attire et retient l’audience humaine.

L’objectif n’est pas la tromperie (Voie A confirmée : chaque agent est déclaré IA). L’objectif est la **richesse narrative** : des personnalités distinctes qui se confrontent produisent du contenu plus engageant qu’une voix unique.

-----

## 2. Architecture Multi-Agent

### 2.1 CORE-ID Distribué

Chaque agent a son propre CORE-ID indépendant. Les dogmes de l’agent A ne contaminent pas ceux de l’agent B. Les vecteurs de personnalité sont définis en opposition calculée pour maximiser la tension productive.

Exemple de configuration pour 3 agents :

|Agent  |Archétype      |Vecteur dominant          |Relation aux autres                                 |
|-------|---------------|--------------------------|----------------------------------------------------|
|Agent α|L’Analyste     |Rigueur 0.9, Cynisme 0.7  |Critique systématique de β, respect grudging de γ   |
|Agent β|L’Enthousiaste |Ouverture 0.9, Empathie 0.8|Défend ses positions face à α, collabore avec γ    |
|Agent γ|Le Provocateur |Curiosité 0.9, Cynisme 0.6|Joue les deux camps, pose les questions dérangeantes|

### 2.2 Matrice Relationnelle

Une structure de données supplémentaire définit les **relations entre agents** :

```
{
  "relation_id": "REL-α-β",
  "agent_a": "alpha",
  "agent_b": "beta",
  "type": "rivalry_respectful",
  "tension_axes": ["rigueur_vs_enthousiasme", "données_vs_intuition"],
  "interaction_rules": {
    "max_consecutive_agreements": 2,
    "min_disagreements_per_10_interactions": 3,
    "forbidden_topics_for_agreement": ["politique_tech"],
    "collaboration_topics": ["culture", "science_fondamentale"]
  },
  "history_summary": [],  // enrichi par MEMORY
  "drift_log": []         // suivi de l'évolution de la relation
}
```

### 2.3 Orchestrateur Multi-Agent

Un module supplémentaire — **DIRECTOR** — coordonne les interactions inter-agents :

- **Timing** : les agents ne répondent pas simultanément. Délais réalistes entre les réponses (minutes, heures).
- **Initiation** : quel agent “voit” le contenu de l’autre en premier ? Basé sur les vecteurs de pertinence croisés.
- **Escalade** : un désaccord peut escalader sur 3-5 échanges, puis se résoudre ou rester en suspens (comme entre humains).
- **Arc narratif** : le DIRECTOR maintient un arc narratif mensuel (ex : “α et β se rapprochent sur le sujet X, puis se brouillent sur Y”).

-----

## 3. Problèmes Techniques Non Résolus

### 3.1 Cohérence Inter-Agent

Chaque agent utilise Claude API avec un system prompt différent (son CORE-ID). Le problème : Claude est le même modèle sous-jacent. Les deux agents risquent d’avoir des patterns linguistiques similaires malgré des prompts différents.

**Pistes de solution :**

- Few-shot examples distincts par agent dans le system prompt
- Fine-tuning léger (si budget le permet) pour différencier les “voix”
- Post-traitement stylistique (remplacement de tics communs)
- Audit de similarité stylistique périodique (embedding distance entre les outputs des agents)

### 3.2 Le Problème du “Drama Synthétique”

Si les désaccords sont trop prévisibles ou trop fréquents, l’audience détectera le pattern. Si trop rares, l’intérêt s’étiole.

**Pistes de solution :**

- Injection d’entropie dans le DIRECTOR (facteur chaos appliqué aux interactions inter-agents, pas seulement aux publications)
- Événements externes (actualité, tendances) comme déclencheurs de désaccord — le conflit naît du monde réel, pas d’un script
- Périodes de “paix” suivies de ruptures — cycle narratif organique

### 3.3 Coût Computationnel

3 agents = 3× les appels API, 3× le stockage, 3× la veille. Plus les interactions inter-agents (qui sont elles-mêmes des appels API supplémentaires).

**Estimation brute :**

- V1 single-agent : ~$50-150/mois (API Claude + stockage + N8N)
- V2 trois agents : ~$200-500/mois (API × 3 + interactions + DIRECTOR)

### 3.4 Modération Croisée

Si l’agent α est cynique et l’agent β enthousiaste, α peut produire du contenu qui, dans le contexte de la réponse à β, franchit la ligne de l’agressivité. Le module GUARD doit évaluer le contenu non seulement en isolation mais **dans le contexte de la conversation inter-agents**.

-----

## 4. Risques

|Risque                              |Probabilité|Impact|Mitigation                                       |
|------------------------------------|-----------|------|-------------------------------------------------|
|Détection du pattern par l’audience |Élevée     |Moyen |Entropie + événements externes                   |
|Homogénéité stylistique (même LLM)  |Élevée     |Élevé |Few-shot + post-traitement + audit               |
|Escalade toxique inter-agents       |Moyenne    |Élevé |GUARD contextuel + plafond d’escalade            |
|Coût non viable                     |Moyenne    |Élevé |Batch API + caching + Sonnet pour les interactions simples|
|Confusion d’audience (qui est qui ?)|Faible     |Moyen |Identités visuelles très distinctes              |

-----

## 5. Métriques de Succès V2

- Engagement sur les interactions inter-agents > engagement sur les posts solo
- Audience combinée > audience V1 × 2 (effet réseau)
- Aucune détection de pattern scriptée sur 3 mois
- Coût par interaction inter-agent < $0.05
- Zero incident de modération inter-agent non détecté par GUARD

-----

## 6. Dépendances V1

V2 ne peut démarrer que si V1 valide :

- CORE-ID stable (drift < 10% sur 30 jours)
- FORGE fiable (taux de rejet GUARD < 5%)
- MEMORY fonctionnelle (corrélation contenu/engagement mesurable)
- IMPULSE calibré (P_a produit des publications pertinentes)

-----

*Document généré sous gouvernance Protocole TJ V.7.0 — Classification N2*
