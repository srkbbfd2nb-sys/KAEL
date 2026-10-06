# KAEL — Registre des décisions humaines

> Un agent prépare la décision ; l'humain la prend (INV.3, INV.4). Chaque entrée porte une
> recommandation **argumentée et révocable**, jamais une décision prise à ta place.
> Quand tu tranches : passe le statut à `décidée`, note la date, le choix et la raison en une
> ligne. Une décision qui change l'identité crée une nouvelle version du fichier d'identité
> (nouvelle empreinte).

| Statut | Sens |
|---|---|
| `ouverte` | à trancher |
| `proposée` | une option est implémentée par défaut, réversible, en attente de confirmation |
| `décidée` | tranchée par l'humain — date et raison notées |

## Bloquent la Phase 1 (identité)

### D-01 — Nom public et cadre narratif · `ouverte`
- **Question** : quel nom porte l'identité publique ? Est-elle une **IA native** (goûts et
  positions justifiés par des raisons, jamais par un vécu) ou un **personnage déclaré** (fiction
  assumée, animée par une IA, annoncée comme telle) ?
- **Enjeu** : c'est ce choix qui résout la contradiction C4 (dogmes biographiques ↔ Voie A).
- **Recommandation (O)** : IA native. Plus simple à tenir sur la durée, plus cohérente avec la
  promesse de transparence, et plus singulière : une IA qui a des goûts et les défend par
  l'argument est un objet nouveau ; un humain fictif de plus ne l'est pas.

### D-02 — Dogmes · `ouverte`
- **Question** : 3 à 7 dogmes de rang 0 (qui est l'agent), puis rangs 1 et 2.
- **Forme** : une phrase, à la première personne, falsifiable par un challenge (sinon DEFEND n'a
  rien à défendre). « Je valorise la nuance » se défend ; « Je suis bon » non.
- **Contrôle** : deux dogmes de rang 0 qui se contredisent sont un défaut de conception
  (`resoudre_conflit` escalade). Les relire deux à deux avant de valider.

### D-03 — Niches thématiques · `ouverte`
- **Question** : un domaine principal, deux à quatre secondaires.
- **Enjeu** : leurs embeddings **sont** le filtre PERCEPT (C1). Une niche floue laisse tout passer.
- **Recommandation (O)** : une niche principale assez étroite pour qu'un signal pertinent soit
  rare (le filtre doit rejeter l'immense majorité des signaux, comme la source le prévoit).

### D-04 — Vecteurs initiaux et bornes · `ouverte`
- **Question** : valeur de départ, min et max sur les 5 axes ; quels axes sont modulables par
  l'engagement.
- **Recommandation (O)** : amplitude min–max ≤ 0,40 par axe ; Cynisme non modulable par
  l'engagement (C6).

### D-05 — Style textuel · `ouverte`
- Registre, longueur moyenne, tics de langage, ponctuation, interdits. 10 à 20 publications
  exemplaires écrites ou validées à la main serviront de référence au juge d'identité (C2).

## Bloquent les phases suivantes

### D-06 — Plateforme du MVP · `ouverte` — bloque la Phase 4
| Option | Pour | Contre |
|---|---|---|
| Bluesky | API ouverte et gratuite, texte court, public ouvert aux comptes automatisés déclarés | Audience plus petite que X |
| Mastodon | Case « compte automatisé » native, gratuit, public tech | Fédéré : règles par instance, audience plus petite |
| X | Audience, culture du texte et des threads | Accès en écriture à l'API payant, tarif instable (à vérifier) |
| Instagram | Audience visuelle | Exige la Phase 3b (visuel) avant le MVP, compte professionnel |

**Recommandation (O)** : Bluesky ou Mastodon pour le MVP — coût d'API nul, tolérance native aux
comptes déclarés, permet de valider tout le moteur ; X en Phase 8 quand la voix est stable.

### D-07 — Tension 1b · `proposée`
Hybride C + A + B, implémenté dans `kael_core/dogmes.py` (priorisation, C8). À confirmer, ou à
ajuster : sous-ensembles de méthodes de défense par rang, pénalités de solidité, seuil 0,60.

### D-08 — Définition de la dérive · `proposée`
Points absolus sur [0, 1], alerte par axe à 0,20, alerte globale (L2) à 0,25 (C3). Seuil V2
« < 10 % sur 30 jours » à relire dans les mêmes unités.

### D-09 — Politique d'autonomie · `proposée` — bloque le passage en autonome (Phase 5)
Par défaut, tout escalade. Proposition : une classe de contenu passe en `auto` après 50
publications validées dont ≥ 90 % sans retouche ; elle repasse en validation sur tout incident
GUARD. Coupe-circuit toujours disponible (C5).

### D-10 — Imperfection calculée · `ouverte`
Recommandation (O) : désactivée (C9). Non implémentée.

### D-11 — Formulation de la transparence par plateforme · `ouverte` — bloque la Phase 4
Recommandation (O) : mention claire, plus la case d'automatisation de la plateforme quand elle
existe. Avis juridique conseillé sur l'article 50 de l'AI Act (C9).

### D-12 — Hébergement de `kael_core` · `ouverte` — bloque la Phase 2
Le service est sans état et sans dépendance : tout hébergeur de conteneur Python convient.
Contraintes : HTTPS, jeton (`KAEL_API_TOKEN`), joignable depuis l'instance N8N.

### D-13 — Données relationnelles · `ouverte` — bloque la Phase 6
Pseudonymisation, durée de conservation, pas d'étiquette péjorative stockée (C10).

### D-14 — Identité visuelle · `ouverte` — bloque la Phase 3b
Attend tes prompts architecturaux (voir [../visuel/](../visuel/)).

### D-16 — Stockage à partir de la Phase 6 · `ouverte`
Postgres + pgvector (état, journaux, recherche sémantique dans une seule base) plutôt qu'Airtable +
base vectorielle séparée. Airtable reste le bon choix pour la V1. Voir [etat_de_lart.md](etat_de_lart.md) §5.

### D-17 — Banc d'essai simulé avant la Phase 4 · `ouverte`
Faire tourner KAEL dans un réseau social simulé (OASIS, Y Social) pour calibrer P_a et GUARD et
mesurer la dérive exprimée, sans publier. Faisabilité à évaluer (N3).

### D-18 — Agrégateur MCP pour PUBLISH (Phase 8) · `ouverte`
Adaptateurs écrits à la main ou agrégateur d'API officielles. Recommandation (O) : adaptateur
direct pour le MVP, réévaluer en Phase 8.

### D-15 — Ordre des annexes · `proposée`
V4-lite → V3-M3 → Phase 3b / 8 → V3-M1 → V2 (refondue) → V3-M2 (priorisation, §1).
