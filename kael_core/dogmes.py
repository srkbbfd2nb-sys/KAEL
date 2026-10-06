"""
CORE-ID · couche Dogmes — le Dogme Enrichissable et ses trois opérations.

Invariant central : **le `core` d'un dogme ne change jamais par une opération.**
REJECT, ENRICH et DEFEND n'écrivent que dans les couches qui l'entourent
(context, defended_challenges, rejected_challenges). Le seul chemin qui modifie
un core est `reviser_core`, qui exige une décision humaine documentée.

Classification (Tension 1b) — proposition implémentée, à valider (D-07) :

  Le juge (appel LLM *distinct* du Plumitif, sans contexte partagé) qualifie
  la donnée : opération, type d'enrichissement, et — si on le lui demande —
  implication logique après intégration (approche A). Le moteur route ensuite
  selon le risque (approche C) :

    factuel                       → appliqué automatiquement
    causal / interprétatif        → test d'implication requis (A), puis :
                                      neutre    → appliqué
                                      affaiblit → rang 2 : appliqué, pénalisé
                                                  rang 1 : validation humaine
    implication « renverse »      → requalifié REJECT (enrichissement troyen)
    tout enrichissement de rang 0 → validation humaine (INV.4, non délégable)

  La solidité (approche B) tourne en sentinelle sur le tout : elle attrape le
  glissement progressif, que des décisions locales toutes légitimes ne voient
  pas. Sous le seuil, le dogme est marqué « consolidation requise ».

Le moteur ne juge pas le sens : il applique des règles à un jugement fourni.
Il ne fait aucun appel réseau. Les entrées et sorties sont des dict JSON, pour
circuler telles quelles entre N8N, Airtable et ce module.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone

OPERATIONS = ("REJECT", "ENRICH", "DEFEND")
TYPES_ENRICHISSEMENT = ("factuel", "causal", "interpretatif", "biographique")
IMPLICATIONS = (None, "neutre", "affaiblit", "renverse")

# Matrice PADC-IA des méthodes de défense. Le rang 0 défend « avec toute
# l'énergie argumentative », le rang 1 « avec méthodes limitées », le rang 2
# « faiblement ». Les sous-ensembles sont une proposition (D-07).
METHODES = ("induction", "abduction", "analogie", "dialectique", "deduction")
METHODES_PAR_RANG = {
    0: set(METHODES),
    1: {"deduction", "induction", "analogie"},
    2: {"induction"},
}

# Paliers de travail, non mesurés (MI-3) : à recalibrer sur données réelles.
SEUIL_SOLIDITE = 0.60
SEUIL_COMPRESSION = 50
PENALITE_AFFAIBLIT = 0.08
PENALITE_NUANCE = 0.04
BONUS_DEFENSE = 0.01
BONUS_DEFENSE_MAX = 0.10

# Statuts d'un résultat
APPLIQUE = "applique"
REJETE = "rejete"
AUDIT_REQUIS = "audit_requis"
VALIDATION_HUMAINE = "validation_humaine"
REFUSE = "refuse"


def _maintenant(quand: str | None) -> str:
    return quand or datetime.now(timezone.utc).date().isoformat()


def _resultat(statut: str, dogme: dict, motif: str, propose: dict | None = None, **extra) -> dict:
    """Forme unique de sortie. `dogme` est l'état en vigueur ; `propose` l'état
    qui entrerait en vigueur si l'humain (ou l'audit) l'approuve."""
    r = {"statut": statut, "motif": motif, "dogme": dogme, "propose": propose,
         "alertes": alertes(dogme if propose is None else propose)}
    r.update(extra)
    return r


# ----------------------------------------------------------------- sentinelles

def solidite(dogme: dict) -> float:
    """Approche B : 1.0 moins les affaiblissements et nuances admis depuis la
    dernière consolidation, plus un léger bonus de défenses réussies (plafonné,
    pour qu'on ne puisse pas « recharger » un dogme en le défendant en boucle)."""
    affaiblit = sum(1 for c in dogme.get("context", []) if c.get("implication") == "affaiblit")
    nuances = sum(1 for d in dogme.get("defended_challenges", []) if d.get("dogma_status") == "nuancé")
    defenses = sum(1 for d in dogme.get("defended_challenges", []) if d.get("dogma_status") == "renforcé")
    s = 1.0 - PENALITE_AFFAIBLIT * affaiblit - PENALITE_NUANCE * nuances \
        + min(BONUS_DEFENSE * defenses, BONUS_DEFENSE_MAX)
    return round(max(0.0, min(1.0, s)), 4)


def alertes(dogme: dict) -> list[str]:
    a = []
    if solidite(dogme) < SEUIL_SOLIDITE:
        a.append("consolidation_requise")
    if len(dogme.get("context", [])) >= SEUIL_COMPRESSION:
        a.append("compression_due")
    return a


# ----------------------------------------------------------------- opérations

def appliquer(dogme: dict, donnee: dict, jugement: dict, cadre_narratif: str = "ia_native",
              quand: str | None = None) -> dict:
    """Applique une donnée (challenge, contexte) à un dogme selon le jugement fourni.

    donnee   : {"texte": str, "source": str}
    jugement : {"operation", "type"?, "implication"?, "methode"?, "defense"?,
                "nuance"?, "defense_biographique"?}
    Ne modifie jamais `dogme` en place.
    """
    op = jugement.get("operation")
    if op not in OPERATIONS:
        return _resultat(REFUSE, dogme, f"operation inconnue : {op!r}")
    date = _maintenant(quand)
    if op == "REJECT":
        return _rejeter(dogme, donnee, "renversement_du_core", date)
    if op == "ENRICH":
        return _enrichir(dogme, donnee, jugement, cadre_narratif, date)
    return _defendre(dogme, donnee, jugement, cadre_narratif, date)


def _rejeter(dogme: dict, donnee: dict, motif: str, date: str) -> dict:
    nouveau = copy.deepcopy(dogme)
    nouveau.setdefault("rejected_challenges", []).append(
        {"challenge": donnee.get("texte", ""), "source": donnee.get("source"), "date": date,
         "motif": motif})
    # Rejet silencieux : rien n'est publié en réponse, tout est journalisé.
    return _resultat(REJETE, nouveau, motif, reponse_publique=False)


def _enrichir(dogme: dict, donnee: dict, j: dict, cadre: str, date: str) -> dict:
    type_ = j.get("type")
    impl = j.get("implication")
    if type_ not in TYPES_ENRICHISSEMENT:
        return _resultat(REFUSE, dogme, f"type d'enrichissement inconnu : {type_!r}")
    if impl not in IMPLICATIONS:
        return _resultat(REFUSE, dogme, f"implication inconnue : {impl!r}")

    if impl == "renverse":
        return _rejeter(dogme, donnee, "enrichissement_troyen", date)
    if type_ == "biographique" and cadre != "personnage_declare":
        # Une IA déclarée qui raconte « chez ma grand-mère en 2019 » ment sur un
        # vécu : contradiction directe avec la Voie A (voir priorisation, C4).
        return _rejeter(dogme, donnee, "biographie_incompatible_avec_la_transparence", date)

    entree = {"source": donnee.get("source"), "date": date,
              "enrichment": donnee.get("texte", ""), "type": type_, "implication": impl}
    propose = copy.deepcopy(dogme)
    propose.setdefault("context", []).append(entree)
    rang = dogme.get("rank")

    if rang == 0:
        return _resultat(VALIDATION_HUMAINE, dogme, "rang_0_contextualisation_sous_confirmation",
                         propose)
    if type_ == "factuel" and impl in (None, "neutre"):
        return _resultat(APPLIQUE, propose, "factuel_auto")
    if impl is None:
        return _resultat(AUDIT_REQUIS, dogme, "test_implication_requis", propose)
    if impl == "neutre":
        return _resultat(APPLIQUE, propose, "audit_neutre")
    # impl == "affaiblit"
    if rang == 2:
        return _resultat(APPLIQUE, propose, "rang_2_affaiblissement_admis")
    return _resultat(VALIDATION_HUMAINE, dogme, "rang_1_affaiblissement", propose)


def _defendre(dogme: dict, donnee: dict, j: dict, cadre: str, date: str) -> dict:
    rang = dogme.get("rank")
    methode = j.get("methode")
    if methode not in METHODES_PAR_RANG.get(rang, set()):
        return _resultat(REFUSE, dogme, f"methode_non_admise_pour_rang_{rang} : {methode!r}")
    if not str(j.get("defense", "")).strip():
        return _resultat(REFUSE, dogme, "defense_vide")
    if j.get("defense_biographique") and cadre != "personnage_declare":
        return _resultat(REFUSE, dogme, "defense_par_vecu_invente")

    nuance = bool(j.get("nuance"))
    propose = copy.deepcopy(dogme)
    propose.setdefault("defended_challenges", []).append(
        {"challenge": donnee.get("texte", ""), "source": donnee.get("source"), "date": date,
         "defense_method": methode, "defense_output": j["defense"],
         "dogma_status": "nuancé" if nuance else "renforcé"})
    if nuance and rang == 0:
        # Le rang 0 ne cède jamais de terrain : une défense qui concède est un
        # signal à porter à l'humain, pas à publier.
        return _resultat(VALIDATION_HUMAINE, dogme, "rang_0_ne_concede_pas", propose)
    return _resultat(APPLIQUE, propose, "defense_nuancee" if nuance else "defense")


# ----------------------------------------------------------------- cycle long

def compresser(dogme: dict, recit_canonique: str, decision_humaine: dict | None = None,
               quand: str | None = None) -> dict:
    """Tension 1c — Accumulation → Compression. Remplace le contexte brut par un
    récit canonique et archive les entrées. Rang 0 et 1 : décision humaine requise,
    car réécrire le récit d'une conviction, c'est déjà la déplacer."""
    if not recit_canonique.strip():
        return _resultat(REFUSE, dogme, "recit_vide")
    date = _maintenant(quand)
    propose = copy.deepcopy(dogme)
    propose.setdefault("archive", []).append(
        {"date": date, "context": propose.get("context", []),
         "defended_challenges": propose.get("defended_challenges", []),
         "solidite_avant": solidite(dogme)})
    propose["context"] = [{"source": "compression", "date": date,
                           "enrichment": recit_canonique, "type": "recit_canonique",
                           "implication": "neutre"}]
    propose["defended_challenges"] = []
    if dogme.get("rank") in (0, 1) and not _decision_valide(decision_humaine):
        return _resultat(VALIDATION_HUMAINE, dogme, "compression_rang_0_1", propose)
    if decision_humaine:
        propose["archive"][-1]["decision"] = decision_humaine
    return _resultat(APPLIQUE, propose, "compression")


def _decision_valide(d: dict | None) -> bool:
    return bool(d) and all(str(d.get(k, "")).strip() for k in ("auteur", "date", "motif"))


def reviser_core(dogme: dict, nouveau_core: str, decision_humaine: dict) -> dict:
    """Seul chemin qui modifie un core. Exige {auteur, date, motif}. Trace l'ancien."""
    if not _decision_valide(decision_humaine):
        return _resultat(REFUSE, dogme, "decision_humaine_incomplete")
    if not nouveau_core.strip():
        return _resultat(REFUSE, dogme, "core_vide")
    nouveau = copy.deepcopy(dogme)
    nouveau.setdefault("revisions", []).append(
        {"ancien_core": dogme.get("core"), **decision_humaine})
    nouveau["core"] = nouveau_core
    return _resultat(APPLIQUE, nouveau, "revision_humaine")


def resoudre_conflit(a: dict, b: dict) -> dict:
    """Tension 1a — le rang supérieur (numéro plus petit) prévaut. Même rang :
    toléré (authenticité), sauf au rang 0 où deux identités fondamentales qui se
    contredisent sont un défaut de conception à porter à l'humain."""
    if a["rank"] != b["rank"]:
        gagnant = a if a["rank"] < b["rank"] else b
        return {"statut": "hierarchie", "prevaut": gagnant["id"]}
    if a["rank"] == 0:
        return {"statut": VALIDATION_HUMAINE, "prevaut": None}
    return {"statut": "tolere", "prevaut": None}
