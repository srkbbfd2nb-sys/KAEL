"""
Contrat HTTP de kael_core — ce que N8N appelle.

Le service est **sans état** : N8N lui envoie l'état (lu dans Airtable) et
écrit lui-même le résultat. Aucune base, aucune session, aucun secret
d'API tierce ici : le service ne parle qu'à N8N. Conséquence voulue : il se
redémarre, se duplique et se teste sans rien perdre.

`traiter(route, charge)` est la fonction pure ; `serveur.py` n'est qu'un
transport autour d'elle.
"""

from __future__ import annotations

import random
from datetime import datetime

from . import __version__, cycle, dogmes, guard, identite, impulse, percept, prompt, rythme, vecteurs


class RequeteInvalide(ValueError):
    pass


def _exiger(charge: dict, *cles: str) -> None:
    manquantes = [c for c in cles if c not in charge]
    if manquantes:
        raise RequeteInvalide(f"champs manquants : {manquantes}")


def _sante(_c):
    return {"etat": "ok", "version": __version__}


def _identite_valider(c):
    _exiger(c, "identite")
    return {"fautes": identite.valider(c["identite"], strict=bool(c.get("strict"))),
            "empreinte": identite.empreinte(c["identite"])}


def _dogme_appliquer(c):
    _exiger(c, "dogme", "donnee", "jugement")
    return dogmes.appliquer(c["dogme"], c["donnee"], c["jugement"],
                            c.get("cadre_narratif", "ia_native"), c.get("quand"))


def _dogme_compresser(c):
    _exiger(c, "dogme", "recit_canonique")
    return dogmes.compresser(c["dogme"], c["recit_canonique"], c.get("decision_humaine"),
                             c.get("quand"))


def _vecteurs_moduler(c):
    _exiger(c, "vecteurs", "deltas", "source", "quand")
    v, j = vecteurs.moduler(c["vecteurs"], c["deltas"], c["source"], c["quand"])
    return {"vecteurs": v, "journal": j}


def _vecteurs_audit(c):
    _exiger(c, "vecteurs", "initiaux")
    return vecteurs.audit_derive(c["vecteurs"], c["initiaux"])


def _percept_filtrer(c):
    _exiger(c, "signaux", "profil")
    return percept.filtrer(c["signaux"], c["profil"], c.get("seuil", percept.SEUIL_DEFAUT))


def _impulse_decider(c):
    _exiger(c, "pertinence", "heures_silence", "engagement_recent",
            "publications_aujourdhui", "maintenant")
    profil = c.get("rythme", rythme.PROFIL_DEFAUT)
    maintenant = datetime.fromisoformat(c["maintenant"])
    if maintenant.tzinfo is None:
        raise RequeteInvalide("maintenant doit porter un fuseau (ex. 2026-10-06T09:00:00+02:00)")
    p = impulse.Parametres(**c.get("parametres", {}))
    rng = random.Random(c["graine"]) if "graine" in c else None
    return impulse.decider(c["pertinence"], c["heures_silence"], c["engagement_recent"],
                           c["publications_aujourdhui"], rythme.en_sommeil(maintenant, profil),
                           p, rng, c.get("jours_compte"))


def _guard_verifier(c):
    _exiger(c, "candidat", "identite", "contexte")
    return guard.verifier(c["candidat"], c["identite"], c["contexte"])


def _prompt_plumitif(c):
    _exiger(c, "identite", "plateforme")
    return {"prompt": prompt.construire(c["identite"], c["plateforme"],
                                        c.get("exploration", "normal"), c.get("exemples")),
            "empreinte_identite": identite.empreinte(c["identite"])}


def _vecteurs_expression(c):
    _exiger(c, "declares", "exprimes")
    return vecteurs.audit_expression(c["declares"], c["exprimes"])


def _percept_sujet(c):
    _exiger(c, "embedding", "historique")
    return percept.sujet_le_plus_proche(c["embedding"], c["historique"])


def _cycle_nouveau(c):
    _exiger(c, "id", "quand")
    return cycle.nouveau(c["id"], c["quand"])


def _cycle_avancer(c):
    _exiger(c, "item", "quand")
    if "verdict" in c:
        return cycle.appliquer_verdict(c["item"], c["verdict"], c["quand"])
    _exiger(c, "vers", "acteur")
    return cycle.avancer(c["item"], c["vers"], c["acteur"], c["quand"], c.get("motif", ""))


ROUTES = {
    "/sante": _sante,
    "/identite/valider": _identite_valider,
    "/dogme/appliquer": _dogme_appliquer,
    "/dogme/compresser": _dogme_compresser,
    "/vecteurs/moduler": _vecteurs_moduler,
    "/vecteurs/audit": _vecteurs_audit,
    "/vecteurs/expression": _vecteurs_expression,
    "/percept/sujet": _percept_sujet,
    "/cycle/nouveau": _cycle_nouveau,
    "/cycle/avancer": _cycle_avancer,
    "/percept/filtrer": _percept_filtrer,
    "/impulse/decider": _impulse_decider,
    "/guard/verifier": _guard_verifier,
    "/prompt/plumitif": _prompt_plumitif,
}


def traiter(route: str, charge: dict) -> tuple[int, dict]:
    """Renvoie (code HTTP, corps). Une erreur se déclare, elle ne se tait pas."""
    f = ROUTES.get(route)
    if f is None:
        return 404, {"erreur": f"route inconnue : {route}", "routes": sorted(ROUTES)}
    if not isinstance(charge, dict):
        return 400, {"erreur": "le corps doit être un objet JSON"}
    try:
        return 200, f(charge)
    except (RequeteInvalide, ValueError, TypeError, KeyError) as e:
        return 400, {"erreur": f"{type(e).__name__}: {e}"}
