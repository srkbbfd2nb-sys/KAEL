"""
CORE-ID · couche Vecteurs — modulation bornée et audit de dérive.

Deux corrections par rapport à la spécification d'origine (priorisation, C3) :

1. **La distance cosinus ne mesure pas la dérive d'un profil de personnalité.**
   Elle ignore la norme : un agent dont *tous* les axes montent de 0,2 garde une
   distance cosinus quasi nulle avec son état initial alors qu'il a changé de
   caractère. L'audit utilise donc la distance absolue par axe (L∞) et la norme
   euclidienne du vecteur de dérive (L2), qui couvre la dérive multi-axes
   (question ouverte 7.1-6 : chaque axe sous le seuil, la somme significative).

2. **« 20 % de dérive » est ambigu.** En relatif, un axe initial à 0,10 alerterait
   à 0,12. L'audit l'interprète en **points absolus sur l'échelle [0, 1]** :
   0,20 = un cinquième de l'échelle. Choix à confirmer (D-08).

La modulation est bornée trois fois : par pas (pas_max), par axe (min/max
déclarés), et par droit (`modulable_par_engagement`). Ce dernier existe parce
que la boucle MEMORY est un optimiseur d'engagement : laissée libre, elle pousse
vers ce que l'algorithme récompense — souvent le cynisme (priorisation, C6).
"""

from __future__ import annotations

import copy
import math

from .identite import AXES

PAS_MAX = 0.02              # variation maximale d'un axe par cycle de modulation
SEUIL_AXE = 0.20            # palier de travail, non mesuré (MI-3)
SEUIL_GLOBAL = 0.25         # norme L2 du vecteur de dérive, palier de travail


def _borne(x: float, bas: float, haut: float) -> float:
    return max(bas, min(haut, x))


def moduler(vecteurs: dict, deltas: dict, source: str, quand: str,
            pas_max: float = PAS_MAX) -> tuple[dict, list[dict]]:
    """Applique des deltas proposés (par MEMORY) et renvoie (nouveaux vecteurs,
    entrées de journal). Ne modifie pas l'entrée. Toute écrêtage est journalisé :
    une modulation refusée silencieusement serait une dérive invisible."""
    nouveau = copy.deepcopy(vecteurs)
    journal = []
    for axe, delta in deltas.items():
        if axe not in AXES:
            journal.append({"axe": axe, "statut": "axe_inconnu", "source": source, "date": quand})
            continue
        a = nouveau[axe]
        if source == "engagement" and not a.get("modulable_par_engagement", True):
            journal.append({"axe": axe, "demande": delta, "applique": 0.0,
                            "statut": "non_modulable_par_engagement", "source": source, "date": quand})
            continue
        d = _borne(float(delta), -pas_max, pas_max)
        avant = float(a["valeur"])
        apres = round(_borne(avant + d, float(a["min"]), float(a["max"])), 6)
        a["valeur"] = apres
        statut = "applique" if abs((apres - avant) - float(delta)) < 1e-9 else "ecrete"
        journal.append({"axe": axe, "demande": delta, "applique": round(apres - avant, 6),
                        "avant": avant, "apres": apres, "statut": statut,
                        "source": source, "date": quand})
    return nouveau, journal


def valeurs(vecteurs: dict, cle: str = "valeur") -> list[float]:
    return [float(vecteurs[a][cle]) for a in AXES]


def distance_cosinus(u: list[float], v: list[float]) -> float:
    nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
    if nu == 0 or nv == 0:
        return 1.0
    return 1.0 - sum(a * b for a, b in zip(u, v)) / (nu * nv)


def audit_expression(declares: dict, exprimes: dict, seuil_axe: float = SEUIL_AXE,
                     seuil_global: float = SEUIL_GLOBAL) -> dict:
    """Écart entre la personnalité **déclarée** (le fichier d'identité) et la
    personnalité **exprimée**, notée sur les dernières publications par un juge
    distinct (ou mesurée par un entretien psychométrique). `audit_derive` ne voit
    que ce que MEMORY a écrit dans le fichier ; la dérive propre au modèle — le
    persona qui s'efface au fil des générations — ne se voit qu'ici."""
    r = audit_derive(exprimes, declares, seuil_axe, seuil_global)
    r["action"] = "recalibrer_prompt" if r["alertes"] else "aucune"
    return r


def audit_derive(vecteurs: dict, initiaux: dict, seuil_axe: float = SEUIL_AXE,
                 seuil_global: float = SEUIL_GLOBAL) -> dict:
    """Audit hebdomadaire GUARD. `initiaux` = vecteurs de la version d'identité
    validée par l'humain (pas ceux de la semaine précédente : une dérive lente
    se mesure contre l'origine, sinon elle est invisible par construction)."""
    actuel, origine = valeurs(vecteurs), valeurs(initiaux)
    par_axe = {a: round(x - y, 6) for a, x, y in zip(AXES, actuel, origine)}
    l2 = math.sqrt(sum(d * d for d in par_axe.values()))
    alertes = [f"axe:{a}" for a, d in par_axe.items() if abs(d) > seuil_axe]
    if l2 > seuil_global:
        alertes.append("global")
    return {
        "par_axe": par_axe,
        "max_axe": round(max(abs(d) for d in par_axe.values()), 6),
        "l2": round(l2, 6),
        "cosinus_info": round(distance_cosinus(actuel, origine), 6),  # affiché, jamais décisionnel
        "alertes": alertes,
        "action": "snapshot_et_notification" if alertes else "aucune",
    }
