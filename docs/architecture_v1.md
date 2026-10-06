# KAEL — Architecture d'implémentation V1

> Complète la Partie IV de la [source](sources/kael_projet_complet.md) ; ne la remplace pas.
> Corrections citées : [priorisation.md](priorisation.md) §3.

## 1 · Principe de répartition

**N8N orchestre · `kael_core` décide · Airtable se souvient · l'humain autorise.**

| Composant | Rôle | Ce qu'il ne fait jamais |
|---|---|---|
| **N8N** (instance existante) | Cron, webhooks, appels LLM / embeddings / plateformes, lecture-écriture Airtable | Prendre une décision : aucun seuil, aucune règle dans un nœud |
| **`kael_core`** (ce dépôt) | Opérations sur les dogmes, dérive, P_a, verdict GUARD, prompt du Plumitif | Appeler un service externe, stocker un état |
| **Airtable** | Livre de Soi lisible, journaux, file de validation | Calculer |
| **Humain** | Identité, politique d'autonomie, validation des escalades | — |

**Pourquoi la logique sort de N8N** : un workflow N8N est un JSON difficile à relire en diff, à
tester et à versionner. Or tout ce qui tranche — rejeter un challenge, laisser partir un post —
doit être testé et tracé. `kael_core` est en bibliothèque standard Python, sans état : N8N lui
envoie l'état lu dans Airtable, reçoit une décision, écrit le résultat. Le service se
redémarre, se duplique et se teste sans rien perdre.

## 2 · Flux

```
           ┌──────────── N8N ─────────────────────────────────────────────────────┐
 RSS/API → │ WF-PERCEPT ──embed──▶ /percept/filtrer ──▶ Airtable.Signaux          │
           │ WF-IMPULSE ─────────▶ /impulse/decider ── publier ? ─┐               │
           │ WF-FORGE ───────────▶ /prompt/plumitif → LLM Plumitif │               │
           │            juge identité (LLM distinct) + modération  │               │
           │            ────────▶ /guard/verifier ─┬─ publier ─────┼─▶ WF-PUBLISH  │
           │                                       ├─ escalader ──▶ File_Validation ─▶ humain
           │                                       └─ bloquer ────▶ Journal_Guard  │
 mentions →│ WF-REPONSES: classifieur (challenge ? question IA ?)                 │
           │            ────────▶ /dogme/appliquer ──▶ Airtable.Dogmes           │
           │ WF-METRIQUES (cron) → Airtable.Metriques → /vecteurs/moduler         │
           │ WF-AUDIT (hebdo) ───▶ /vecteurs/audit ─ alerte ─▶ snapshot + notification
           └──────────────────────────────────────────────────────────────────────┘
```

## 3 · Contrat de `kael_core`

Toutes les routes : `POST`, JSON, en-tête `Authorization: Bearer $KAEL_API_TOKEN`
(`GET /sante` sans jeton). Erreur ⇒ 400 avec message explicite, jamais un succès silencieux.

| Route | Entrée | Sortie |
|---|---|---|
| `/identite/valider` | `identite`, `strict?` | `fautes`, `empreinte` |
| `/dogme/appliquer` | `dogme`, `donnee`, `jugement`, `cadre_narratif?`, `quand?` | `statut`, `motif`, `dogme`, `propose`, `alertes` |
| `/dogme/compresser` | `dogme`, `recit_canonique`, `decision_humaine?` | idem |
| `/vecteurs/moduler` | `vecteurs`, `deltas`, `source`, `quand` | `vecteurs`, `journal` |
| `/vecteurs/audit` | `vecteurs`, `initiaux` | `par_axe`, `max_axe`, `l2`, `alertes`, `action` |
| `/percept/filtrer` | `signaux[{id, embedding}]`, `profil[{id, embedding, poids?}]`, `seuil?` | `retenus`, `rejetes` |
| `/impulse/decider` | `pertinence`, `heures_silence`, `engagement_recent`, `publications_aujourdhui`, `maintenant` (ISO avec fuseau), `rythme?`, `parametres?` | `publier`, `p_a`, `composantes`, `exploration`, `validation_requise`, `motif` |
| `/guard/verifier` | `candidat`, `identite`, `contexte` | `verdict`, `bloquants`, `escalades` |
| `/prompt/plumitif` | `identite`, `plateforme`, `exploration?`, `exemples?` | `prompt`, `empreinte_identite` |
| `/vecteurs/expression` | `declares`, `exprimes` (notés par un juge distinct sur les N derniers posts) | idem audit + `action` |
| `/percept/sujet` | `embedding`, `historique[{id, embedding}]` (90 jours) | `similarite_sujet`, `id` |
| `/cycle/nouveau` | `id`, `quand` | élément à l'état `brouillon` |
| `/cycle/avancer` | `item`, `quand`, et `verdict` (GUARD) **ou** `vers` + `acteur` | élément avancé, ou 400 si la transition est interdite |

Statuts d'une opération sur un dogme : `applique` · `rejete` · `audit_requis` (lancer le juge
d'implication, rappeler la route avec `implication` renseignée) · `validation_humaine` (écrire
`propose` dans la file de validation) · `refuse` (jugement invalide).

**Machine à états d'une publication** (`cycle.py`, voir [etat_de_lart.md](etat_de_lart.md)) :
`brouillon → verifie | en_validation | a_regenerer` → `valide | rejete` (humain seulement) →
`planifie → publie | echec | annule`. Chaque workflow N8N prend les éléments d'un état et demande
la transition suivante ; l'état vit dans Airtable (`Publications.etat`), jamais dans le workflow.
La validation humaine passe par une messagerie à boutons (Telegram ou Slack : « valider » /
« rejeter » appellent `/cycle/avancer` avec `acteur = humain:<nom>`).

## 4 · Appels LLM — séparation des rôles

| Rôle | Palier | Contexte | Sortie |
|---|---|---|---|
| Stratège | rapide | signal + résumé d'identité | angle, format, classe de contenu |
| Plumitif | profond pour threads, rapide sinon | `/prompt/plumitif` + signal encapsulé | texte |
| Juge d'identité | rapide | grille + texte, **sans** le prompt du Plumitif | score par dimension (dogmes, ton, registre, interdits) + consigne de régénération par dimension en échec |
| Juge de personnalité exprimée (hebdomadaire) | profond | les N dernières publications, **sans** les vecteurs déclarés | note 0–1 sur les 5 axes → `/vecteurs/expression` |
| Modération | rapide | texte (+ conversation si réponse) | `ok` / `incertain` / `bloque` |
| Classifieur de challenge | rapide | dogme + message encapsulé | `jugement` (opération, type, `question_nature_ia`) |
| Juge d'implication (Tension 1b, A) | profond | dogme + enrichissement proposé, **sans** l'historique | `neutre` / `affaiblit` / `renverse` |

Règle de circularité V.8 : un juge qui partage le contexte du producteur mesure la cohérence du
producteur, pas sa justesse. Chaque juge est un appel neuf. Le prompt système du Plumitif est
stable par construction (dérivé de l'identité) : le cache de prompt s'y applique pleinement.

## 5 · Airtable — tables

| Table | Contenu | Écrite par |
|---|---|---|
| `Identite_Versions` | JSON complet, empreinte, auteur, date, motif | humain |
| `Dogmes` | un enregistrement par dogme (JSON + colonnes lisibles : core, rang, solidité) | WF-REPONSES, humain |
| `Signaux` | id, source, score, ancre, statut (retenu / rejeté / consommé) | WF-PERCEPT |
| `Publications` | texte, plateforme, classe, P_a, verdict GUARD, empreinte d'identité, id plateforme | WF-PUBLISH |
| `Metriques` | publication, horodatage, impressions, réactions | WF-METRIQUES |
| `File_Validation` | objet proposé, motif d'escalade, décision humaine, date | GUARD, humain |
| `Journal_Guard` | tout refus, avec motifs | WF-FORGE |
| `Journal_Derive` | entrées de `moduler` et rapports d'`audit` | WF-METRIQUES, WF-AUDIT |
| `Relations` *(Phase 6)* | identifiant pseudonymisé, affinité, dernière interaction | WF-REPONSES |

`Publications.empreinte_identite` relie chaque post à la version d'identité qui l'a produit :
c'est ce qui rend le retour arrière et l'audit possibles (axe d'amélioration 7.3-2 de la
source).

## 6 · Phases et critères de sortie

| Phase | Livrable | Critère de sortie (mesurable) | État |
|---|---|---|---|
| **0** | Décisions D-01 à D-05 | `python -m kael_core valider identite/identite.json --strict` sort en 0 | ouverte |
| **1** | CORE-ID | Moteur dogmes et vecteurs testé ; banc de 30 challenges écrits à la main, classés par le classifieur, résultat relu | **moteur fait** |
| 2 | PERCEPT | Profil d'intérêt embarqué ; seuil calibré sur ≥ 30 + 30 signaux étiquetés (`calibrer_seuil`) | moteur fait |
| 3 | FORGE texte (manuel) | 50 textes générés, juge d'identité calibré contre le jugement humain | prompt fait |
| 3b | FORGE visuel | Voir [../visuel/](../visuel/) | en attente des prompts |
| 4 | PUBLISH, 1 plateforme | Publication réelle, 100 % validée à la main, journaux complets | — |
| 5 | IMPULSE autonome | Politique d'autonomie (D-09) ; poids P_a recalibrés sur les données de la Phase 4 | moteur fait |
| 6 | MEMORY | Modulation journalisée ; aucun axe protégé modulé | moteur fait |
| 7 | GUARD complet | Coupe-circuit testé en réel ; audit hebdomadaire ; alertes de quotas et de clés d'API | moteur fait |
| 8 | Multi-plateforme | Un adaptateur par plateforme, même moteur | — |
