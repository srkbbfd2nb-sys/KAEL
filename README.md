# KAEL — agent social IA autonome à identité persistante

> **Statut** : Phase 0 (décisions d'identité) · moteur de décision V1 écrit et testé ·
> aucune publication réelle.
> **Gouvernance** : conçu sous Protocole LAB V.8 ; KAEL n'est pas gouverné par le protocole en
> temps réel, il en hérite les patterns.

KAEL est un agent qui a une identité — des dogmes hiérarchisés, une personnalité sur cinq axes,
un style — et qui publie quand il en a **envie** : quand un signal du monde résonne avec ce qu'il
est, et qu'assez de temps a passé. Il est déclaré comme IA, partout, sans exception. Il défend ses
convictions, laisse ses préférences évoluer dans des bornes, et ne laisse jamais une somme de
petites concessions renverser ce qu'il est.

## Par où commencer

| Tu veux… | Lis |
|---|---|
| savoir ce qui est primaire, ce qui est annexe, et pourquoi | [docs/priorisation.md](docs/priorisation.md) |
| savoir ce qui t'attend comme décisions | [docs/decisions.md](docs/decisions.md) |
| comprendre comment N8N, Airtable et le moteur s'articulent | [docs/architecture_v1.md](docs/architecture_v1.md) |
| définir l'identité | [identite/](identite/) |
| déposer les prompts visuels | [visuel/](visuel/) |
| relire la conception d'origine | [docs/sources/](docs/sources/) |

## Structure

```
docs/          priorisation, décisions, architecture — et les sources d'origine, en archive
identite/      gabarit du fichier d'identité (la seule source de vérité de « qui est KAEL »)
visuel/        structure d'accueil des prompts architecturaux image et vidéo
kael_core/     le moteur de décision — bibliothèque standard Python, sans état, sans réseau
tests/         ce que le moteur garantit, démontré
```

## Le moteur

| Module | Rôle | Ce qu'il garantit |
|---|---|---|
| `identite` | charger, valider, versionner l'identité | aucune mise en production avec un « À DÉFINIR » ; la Voie A n'est pas un réglage |
| `dogmes` | REJECT / ENRICH / DEFEND, compression, révision | le `core` d'un dogme ne change jamais par une opération ; le rang 0 ne bouge que par l'humain |
| `vecteurs` | modulation bornée, audit de dérive | dérive mesurée par axe **et** globalement ; axes protégés de l'engagement |
| `percept` | filtre de pertinence, calibrage du seuil | jamais de comparaison entre espaces incompatibles |
| `impulse` | potentiel d'action P_a | pas de sujet ⇒ pas de publication ; entropie ≤ 0,15 |
| `rythme` | créneaux, sommeil, délais | jamais de publication pendant le sommeil du persona |
| `guard` | verdict publier / escalader / bloquer | échec fermé ; « es-tu une IA ? » ⇒ réponse qui commence par « oui » |
| `prompt` | prompt système du Plumitif dérivé de l'identité | le contenu externe est encapsulé comme donnée |
| `api`, `serveur` | contrat HTTP pour N8N | refuse de démarrer sans jeton |

```bash
cd kael
python -m pytest tests -q                                  # 72 tests
python -m kael_core valider identite/identite.template.json --strict   # sort en 1 : décisions en attente
KAEL_API_TOKEN=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  python -m kael_core.serveur --port 8080                  # service pour N8N
```

## Ce que le moteur ne fait pas

Il n'appelle aucun LLM, aucune plateforme, aucune base : N8N le fait et lui transmet l'état. Il
ne juge pas le sens d'un message — un classifieur LLM le fait — il applique des règles testées à
ce jugement. Les seuils et les poids sont des **paliers de travail**, déclarés comme tels dans le
code : ils deviennent des valeurs quand les données des Phases 3 à 5 les remplacent.
