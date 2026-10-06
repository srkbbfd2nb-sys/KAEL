"""
IMPULSE — potentiel d'action P_a (« l'envie de publier »).

    P_a = w_p · pertinence + w_e · ennui(t) + w_g · engagement_recent + ε

  pertinence        meilleur score PERCEPT en file, dans [0, 1]
  ennui(t)          min(1, heures_silence / horizon_ennui) — linéaire, remis à
                    zéro à chaque publication (le compteur de la spécification)
  engagement_recent élan des dernières publications, normalisé [0, 1]
  ε                 bruit uniforme dans [-entropie, +entropie], entropie ≤ 0,15

Quatre verrous passent **avant** la formule, parce qu'aucun score ne doit pouvoir
les acheter : heures de sommeil ; quota journalier ; écart minimal depuis la
dernière publication (pas de rafale) ; pas de signal au-dessus du seuil PERCEPT
→ pas de publication (sans sujet, l'ennui seul produirait de la publication
mécanique — exactement ce que la spécification refuse).

Calibrage par défaut, vérifié par les tests : un signal exceptionnel (0,95)
part dès ~2 h de silence — une tendance ne survit pas à six heures d'attente ;
un signal tout juste pertinent (0,65) attend environ une journée ; un signal à
0,60 seul ne suffit jamais sans élan d'engagement.

L'entropie a deux usages séparés, comme dans la spécification : un bruit sur la
décision, et un **niveau d'exploration** transmis à FORGE pour le sujet et le
ton (jamais les dogmes) — normal / contrôlé / profond, le profond exigeant
validation (Bloc F, exploration balisée en 3 niveaux).

Poids et seuils : paliers de travail, à calibrer en Phase 5 sur données (MI-3).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

ENTROPIE_MAX = 0.15


@dataclass(frozen=True)
class Parametres:
    poids_pertinence: float = 0.70
    poids_ennui: float = 0.20
    poids_engagement: float = 0.10
    horizon_ennui_h: float = 24.0
    seuil_publication: float = 0.70
    seuil_pertinence: float = 0.60
    entropie: float = 0.10
    max_publications_jour: int = 4
    ecart_min_h: float = 1.5
    duree_rodage_j: int = 14

    def __post_init__(self):
        if not 0.0 <= self.entropie <= ENTROPIE_MAX:
            raise ValueError(f"entropie hors [0, {ENTROPIE_MAX}] : {self.entropie}")
        somme = self.poids_pertinence + self.poids_ennui + self.poids_engagement
        if abs(somme - 1.0) > 1e-9:
            raise ValueError(f"les poids doivent sommer à 1 (obtenu {somme})")


def niveau_exploration(tirage: float, entropie: float) -> str:
    """Tirage uniforme [0, 1). Plus l'entropie est haute, plus l'exploration est
    fréquente ; à entropie nulle, toujours « normal »."""
    if entropie <= 0:
        return "normal"
    r = entropie / ENTROPIE_MAX            # 0..1
    if tirage < 0.05 * r:
        return "profond"
    if tirage < 0.25 * r:
        return "controle"
    return "normal"


def quota_rodage(quota: int, jours_compte: int | None, duree_j: int) -> int:
    """Montée en charge d'un compte neuf : ~1/duree du quota au jour 0, plein
    quota à la fin du rodage. Pas pour échapper à une détection — le compte est
    déclaré — mais parce qu'un compte neuf qui publie à plein régime ressemble à
    du spam, et que les premiers jours sont ceux où l'humain observe."""
    if jours_compte is None or duree_j <= 0:
        return quota
    return max(1, math.ceil(quota * min(1.0, (jours_compte + 1) / duree_j)))


def decider(pertinence: float, heures_silence: float, engagement_recent: float,
            publications_aujourdhui: int, en_sommeil: bool,
            p: Parametres = Parametres(), rng: random.Random | None = None,
            jours_compte: int | None = None) -> dict:
    rng = rng or random.Random()
    base = {"publier": False, "p_a": 0.0, "composantes": {}, "exploration": "normal",
            "validation_requise": False}
    if en_sommeil:
        return {**base, "motif": "heures_de_sommeil"}
    if publications_aujourdhui >= quota_rodage(p.max_publications_jour, jours_compte,
                                               p.duree_rodage_j):
        return {**base, "motif": "quota_journalier"}
    if heures_silence < p.ecart_min_h:
        return {**base, "motif": "ecart_minimal"}
    if pertinence < p.seuil_pertinence:
        return {**base, "motif": "aucun_signal_pertinent"}

    ennui = min(1.0, max(0.0, heures_silence) / p.horizon_ennui_h)
    eng = max(0.0, min(1.0, engagement_recent))
    epsilon = rng.uniform(-p.entropie, p.entropie)
    comp = {"pertinence": round(p.poids_pertinence * pertinence, 4),
            "ennui": round(p.poids_ennui * ennui, 4),
            "engagement": round(p.poids_engagement * eng, 4),
            "epsilon": round(epsilon, 4)}
    p_a = max(0.0, min(1.0, sum(comp.values())))
    exploration = niveau_exploration(rng.random(), p.entropie)
    publier = p_a >= p.seuil_publication
    return {"publier": publier, "p_a": round(p_a, 4), "composantes": comp,
            "exploration": exploration, "validation_requise": exploration == "profond",
            "motif": "seuil_atteint" if publier else "sous_le_seuil"}
