"""
CORE-ID — chargement, validation et empreinte du fichier d'identité.

Le fichier d'identité est la seule source de vérité de « qui est KAEL ». Il est
écrit par un humain (décisions D-01 à D-05) et ne se modifie qu'en créant une
nouvelle version : l'empreinte SHA-256 de sa forme canonique sert d'identifiant
de version, de sorte qu'un retour arrière est toujours possible et qu'une
modification silencieuse est toujours détectable.

Deux niveaux de validation :
  - structurelle (toujours) : forme, bornes, rangs, unicité ;
  - stricte (mise en production) : aucun champ encore « À DÉFINIR », au moins un
    dogme de rang 0, une mention de transparence pour chaque plateforme active.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

SCHEMA = "kael.identite/1"
AXES = ("ouverture", "rigueur", "cynisme", "empathie", "curiosite")
RANGS = (0, 1, 2)
CADRES_NARRATIFS = ("ia_native", "personnage_declare")
MARQUEUR_A_DEFINIR = "À DÉFINIR"


class IdentiteInvalide(ValueError):
    """Le fichier d'identité viole le contrat. Porte la liste complète des fautes."""

    def __init__(self, fautes: list[str]):
        self.fautes = fautes
        super().__init__("identité invalide :\n  - " + "\n  - ".join(fautes))


def charger(chemin: str | Path, strict: bool = False) -> dict:
    """Lit, valide et renvoie l'identité. Lève IdentiteInvalide au premier écart."""
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    fautes = valider(donnees, strict=strict)
    if fautes:
        raise IdentiteInvalide(fautes)
    return donnees


def empreinte(donnees: dict) -> str:
    """SHA-256 de la forme canonique (clés triées, sans espaces) — identifiant de version."""
    canon = json.dumps(donnees, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _contient_a_definir(valeur) -> bool:
    if isinstance(valeur, str):
        return MARQUEUR_A_DEFINIR in valeur
    if isinstance(valeur, dict):
        return any(_contient_a_definir(v) for v in valeur.values())
    if isinstance(valeur, list):
        return any(_contient_a_definir(v) for v in valeur)
    return False


def valider(d: dict, strict: bool = False) -> list[str]:
    """Renvoie toutes les fautes (liste vide = conforme). N'arrête pas à la première."""
    f: list[str] = []
    if not isinstance(d, dict):
        return ["la racine doit être un objet JSON"]
    if d.get("schema") != SCHEMA:
        f.append(f"schema attendu « {SCHEMA} », obtenu « {d.get('schema')} »")
    if d.get("cadre_narratif") not in CADRES_NARRATIFS:
        f.append(f"cadre_narratif doit valoir l'un de {CADRES_NARRATIFS}")

    # --- transparence : non négociable (Voie A) -------------------------------
    t = d.get("transparence")
    if not isinstance(t, dict):
        f.append("transparence manquante")
    else:
        if t.get("repondre_oui_si_question_ia") is not True:
            f.append("transparence.repondre_oui_si_question_ia doit valoir true — "
                     "ce n'est pas un réglage, c'est la Voie A")
        if not str(t.get("reponse_question_ia", "")).strip():
            f.append("transparence.reponse_question_ia vide")
        mentions = t.get("mention_par_plateforme")
        if not isinstance(mentions, dict):
            f.append("transparence.mention_par_plateforme doit être un objet")
        elif strict:
            for p in d.get("plateformes_actives", []):
                if not str(mentions.get(p, "")).strip():
                    f.append(f"plateforme active « {p} » sans mention de transparence")

    # --- dogmes ---------------------------------------------------------------
    dogmes = d.get("dogmes")
    if not isinstance(dogmes, list) or not dogmes:
        f.append("dogmes : liste non vide attendue")
        dogmes = []
    vus = set()
    for i, g in enumerate(dogmes):
        ou = f"dogmes[{i}]"
        if not isinstance(g, dict):
            f.append(f"{ou} doit être un objet")
            continue
        gid = g.get("id")
        if not gid:
            f.append(f"{ou} sans id")
        elif gid in vus:
            f.append(f"{ou} id dupliqué « {gid} »")
        vus.add(gid)
        if not str(g.get("core", "")).strip():
            f.append(f"{ou} core vide")
        if g.get("rank") not in RANGS:
            f.append(f"{ou} rank doit valoir 0, 1 ou 2")
        c = g.get("confidence", 1.0)
        if not isinstance(c, (int, float)) or not 0.0 <= c <= 1.0:
            f.append(f"{ou} confidence hors [0, 1]")
    if strict and not any(isinstance(g, dict) and g.get("rank") == 0 for g in dogmes):
        f.append("aucun dogme de rang 0 — l'identité fondamentale n'est pas définie (D-02)")

    # --- vecteurs -------------------------------------------------------------
    v = d.get("vecteurs")
    if not isinstance(v, dict):
        f.append("vecteurs manquants")
    else:
        for axe in AXES:
            a = v.get(axe)
            if not isinstance(a, dict):
                f.append(f"vecteurs.{axe} manquant")
                continue
            try:
                mn, val, mx = float(a["min"]), float(a["valeur"]), float(a["max"])
            except (KeyError, TypeError, ValueError):
                f.append(f"vecteurs.{axe} : min, valeur, max numériques requis")
                continue
            if not 0.0 <= mn <= val <= mx <= 1.0:
                f.append(f"vecteurs.{axe} : 0 ≤ min ≤ valeur ≤ max ≤ 1 non respecté "
                         f"({mn}, {val}, {mx})")
        inconnus = set(v) - set(AXES)
        if inconnus:
            f.append(f"vecteurs : axes inconnus {sorted(inconnus)}")

    # --- règles de style apprises (boucle de réflexion) ---------------------
    for i, r in enumerate(d.get("regles_apprises", [])):
        dec = r.get("decision", {}) if isinstance(r, dict) else {}
        if not (isinstance(r, dict) and str(r.get("regle", "")).strip()):
            f.append(f"regles_apprises[{i}] : champ « regle » vide")
        elif not all(str(dec.get(k, "")).strip() for k in ("auteur", "date")):
            f.append(f"regles_apprises[{i}] sans décision humaine (auteur, date) — une règle "
                     "proposée par la réflexion n'entre pas dans l'identité sans validation")

    if strict and _contient_a_definir(d):
        f.append(f"des champs portent encore « {MARQUEUR_A_DEFINIR} » — décisions humaines en attente")
    return f
