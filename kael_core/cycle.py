"""
Cycle de vie d'une publication — machine à états explicite.

Inspiré du patron « l'état vit dans la base, les workers font une transition
chacun » (voir docs/etat_de_lart.md). Chaque publication candidate porte un
`etat` ; N8N lit les éléments dans un état donné, fait le travail, et demande
ici la transition suivante. Une transition non prévue est refusée : un post ne
peut pas passer de `brouillon` à `planifie` sans être passé par GUARD, ni de
`en_validation` à `valide` sans un humain.

    brouillon ──GUARD publier──▶ verifie ─────────────┐
        │ ──GUARD escalader─▶ en_validation ─humain─▶ valide ──▶ planifie ──▶ publie
        │                          └─humain─▶ rejete               │
        └──GUARD bloquer──▶ a_regenerer ──▶ brouillon (≤ 3 fois)   ├──▶ echec ──▶ planifie (≤ 3)
                                  └──▶ abandonne                   └──▶ annule

Trois régénérations au plus : c'est la boucle OFI du protocole (3 itérations,
puis escalade). Au-delà, l'élément est abandonné et journalisé — jamais relancé
en silence.
"""

from __future__ import annotations

import copy

TRANSITIONS = {
    "brouillon": {"verifie", "en_validation", "a_regenerer", "abandonne"},
    "a_regenerer": {"brouillon", "abandonne"},
    "en_validation": {"valide", "rejete"},
    "verifie": {"planifie", "annule"},
    "valide": {"planifie", "annule"},
    "planifie": {"publie", "echec", "annule"},
    "echec": {"planifie", "abandonne"},
}
TERMINAUX = {"publie", "rejete", "abandonne", "annule"}
ETATS = set(TRANSITIONS) | TERMINAUX

DECISIONS_HUMAINES = {("en_validation", "valide"), ("en_validation", "rejete")}
DEPUIS_VERDICT = {"publier": "verifie", "escalader": "en_validation", "bloquer": "a_regenerer"}
MAX_REGENERATIONS = 3
MAX_REESSAIS = 3


class TransitionRefusee(ValueError):
    pass


def nouveau(identifiant: str, quand: str) -> dict:
    return {"id": identifiant, "etat": "brouillon", "regenerations": 0, "reessais": 0,
            "historique": [{"de": None, "vers": "brouillon", "acteur": "systeme", "date": quand}]}


def avancer(item: dict, vers: str, acteur: str, quand: str, motif: str = "") -> dict:
    """Renvoie une copie de l'élément dans son nouvel état, ou lève TransitionRefusee.
    `acteur` : "systeme", "guard" ou "humain:<nom>"."""
    de = item.get("etat")
    if vers not in ETATS:
        raise TransitionRefusee(f"état inconnu : {vers!r}")
    if de in TERMINAUX:
        raise TransitionRefusee(f"« {de} » est terminal")
    if vers not in TRANSITIONS.get(de, set()):
        raise TransitionRefusee(f"transition interdite : {de} → {vers}")
    if (de, vers) in DECISIONS_HUMAINES and not acteur.startswith("humain:"):
        raise TransitionRefusee(f"{de} → {vers} exige un humain (INV.4), pas « {acteur} »")

    n = copy.deepcopy(item)
    if vers == "brouillon" and de == "a_regenerer":
        if n["regenerations"] >= MAX_REGENERATIONS:
            raise TransitionRefusee(f"{MAX_REGENERATIONS} régénérations atteintes : abandonner")
        n["regenerations"] += 1
    if vers == "planifie" and de == "echec":
        if n["reessais"] >= MAX_REESSAIS:
            raise TransitionRefusee(f"{MAX_REESSAIS} réessais atteints : abandonner")
        n["reessais"] += 1
    n["etat"] = vers
    n["historique"].append({"de": de, "vers": vers, "acteur": acteur, "date": quand, "motif": motif})
    return n


def appliquer_verdict(item: dict, verdict: dict, quand: str) -> dict:
    """Branche le verdict GUARD sur la machine. Un blocage au-delà du quota de
    régénérations mène directement à `abandonne`."""
    vers = DEPUIS_VERDICT[verdict["verdict"]]
    motif = ", ".join(verdict.get("bloquants", []) + verdict.get("escalades", []))
    n = avancer(item, vers, "guard", quand, motif)
    if vers == "a_regenerer" and n["regenerations"] >= MAX_REGENERATIONS:
        n = avancer(n, "abandonne", "systeme", quand, "quota de régénérations épuisé")
    return n
