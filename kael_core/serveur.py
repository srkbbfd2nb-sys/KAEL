"""
Transport HTTP minimal autour de api.traiter — bibliothèque standard seule.

    KAEL_API_TOKEN=… python -m kael_core.serveur --port 8080

Toutes les routes sont en POST (JSON), sauf /sante (GET, sans jeton).
Le jeton est obligatoire : sans KAEL_API_TOKEN, le serveur refuse de démarrer
plutôt que d'exposer un moteur de décision sans authentification.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .api import traiter

TAILLE_MAX = 1_000_000


class Gestionnaire(BaseHTTPRequestHandler):
    jeton: str = ""

    def _repondre(self, code: int, corps: dict) -> None:
        donnees = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        self.wfile.write(donnees)

    def do_GET(self):  # noqa: N802
        if self.path == "/sante":
            self._repondre(*traiter("/sante", {}))
        else:
            self._repondre(405, {"erreur": "POST attendu"})

    def do_POST(self):  # noqa: N802
        recu = self.headers.get("Authorization", "")
        if not hmac.compare_digest(recu, f"Bearer {self.jeton}"):
            self._repondre(401, {"erreur": "jeton invalide"})
            return
        try:
            taille = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            taille = -1
        if not 0 <= taille <= TAILLE_MAX:
            self._repondre(413, {"erreur": "corps trop volumineux"})
            return
        try:
            charge = json.loads(self.rfile.read(taille) or b"{}")
        except json.JSONDecodeError as e:
            self._repondre(400, {"erreur": f"JSON invalide : {e}"})
            return
        self._repondre(*traiter(self.path, charge))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="kael_core — service de décision pour N8N")
    p.add_argument("--hote", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    a = p.parse_args(argv)
    jeton = os.environ.get("KAEL_API_TOKEN", "")
    if len(jeton) < 32:
        print("KAEL_API_TOKEN absent ou trop court (32 caractères minimum) — arrêt.", file=sys.stderr)
        return 2
    Gestionnaire.jeton = jeton
    print(f"kael_core à l'écoute sur {a.hote}:{a.port}")
    ThreadingHTTPServer((a.hote, a.port), Gestionnaire).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
