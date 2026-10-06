"""
    python -m kael_core valider identite/identite.json [--strict]

Sortie 0 = conforme · 1 = fautes (listées) · 2 = fichier illisible.
`--strict` = prêt pour la production : plus aucun « À DÉFINIR », un dogme de
rang 0 au moins, une mention de transparence par plateforme active.
"""

import argparse
import json
import sys
from pathlib import Path

from .identite import empreinte, valider


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="kael_core")
    sp = p.add_subparsers(dest="commande", required=True)
    v = sp.add_parser("valider", help="valide un fichier d'identité")
    v.add_argument("fichier")
    v.add_argument("--strict", action="store_true")
    a = p.parse_args(argv)

    try:
        donnees = json.loads(Path(a.fichier).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"illisible : {e}", file=sys.stderr)
        return 2
    fautes = valider(donnees, strict=a.strict)
    if fautes:
        print(f"{len(fautes)} faute(s) :")
        print("\n".join(f"  - {x}" for x in fautes))
        return 1
    print(f"conforme{' (strict)' if a.strict else ''} — empreinte {empreinte(donnees)[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
