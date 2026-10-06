# Identité de KAEL — le fichier qui fait foi

1. Copier [identite.template.json](identite.template.json) en `identite.json`.
2. Remplacer chaque « À DÉFINIR » (les codes D-xx renvoient à [../docs/decisions.md](../docs/decisions.md)).
3. Vérifier, depuis la racine du dépôt :

```bash
python -m kael_core valider identite/identite.json            # forme
python -m kael_core valider identite/identite.json --strict   # prêt pour la production
```

`--strict` refuse tant qu'il reste un « À DÉFINIR », qu'aucun dogme de rang 0 n'existe ou qu'une
plateforme active n'a pas sa mention de transparence. La commande affiche l'**empreinte** : c'est
l'identifiant de version que chaque publication portera.

## Règles

- **On ne modifie pas un core à la main dans Airtable.** Une modification d'identité est une
  nouvelle version de ce fichier (nouvelle empreinte), avec auteur, date et motif.
- `transparence.repondre_oui_si_question_ia` vaut `true` et n'est pas un réglage : la validation
  échoue sinon.
- `reponse_question_ia` est la phrase par laquelle **commence** toute réponse à « es-tu une IA ? ».
  GUARD bloque une réponse qui ne commence pas par elle.
- Les clés des dogmes (`core`, `rank`, `context`, `defended_challenges`, `rejected_challenges`)
  reprennent celles de la spécification d'origine, pour rester compatibles avec elle.

> Si le dépôt est public et que l'identité doit rester confidentielle avant le lancement, garde
> `identite.json` hors du dépôt (ou dans un dépôt privé) et ne versionne ici que le gabarit.
