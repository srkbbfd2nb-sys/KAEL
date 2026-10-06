"""
PERCEPT — filtre de pertinence identitaire.

Correction par rapport à la spécification (priorisation, C1) : la pertinence ne
se calcule pas contre les « vecteurs CORE-ID ». Ceux-ci vivent dans un espace à
5 dimensions (Ouverture, Rigueur…) ; un signal embarqué vit dans l'espace du
modèle d'embedding (des centaines de dimensions). Le cosinus entre les deux n'est
pas défini. La pertinence se calcule contre un **profil d'intérêt** : les
embeddings des niches et des dogmes, produits par le *même* modèle que celui
qui embarque les signaux.

Le seuil 0,6 dépend du modèle d'embedding : selon le modèle, deux textes
proches peuvent scorer 0,4 ou 0,85. D'où `calibrer_seuil`, qui fixe le seuil à
partir d'exemples étiquetés par l'humain plutôt qu'à l'intuition (MI-3).

Les embeddings sont fournis par l'appelant (N8N) : ce module ne fait aucun appel
réseau.
"""

from __future__ import annotations

import math

SEUIL_DEFAUT = 0.60


def cosinus(u: list[float], v: list[float]) -> float:
    if len(u) != len(v):
        raise ValueError(f"dimensions incompatibles : {len(u)} ≠ {len(v)} — "
                         "le signal et le profil doivent venir du même modèle d'embedding")
    nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
    if nu == 0 or nv == 0:
        return 0.0
    return sum(a * b for a, b in zip(u, v)) / (nu * nv)


def pertinence(embedding: list[float], profil: list[dict]) -> dict:
    """profil : [{"id": "niche:principale", "embedding": [...], "poids": 1.0}, ...]
    Renvoie le meilleur ancrage pondéré : un signal est pertinent s'il résonne
    fortement avec *un* intérêt, pas faiblement avec tous."""
    meilleur, ancre = 0.0, None
    for p in profil:
        s = cosinus(embedding, p["embedding"]) * float(p.get("poids", 1.0))
        if s > meilleur:
            meilleur, ancre = s, p["id"]
    return {"score": round(meilleur, 4), "ancre": ancre}


def filtrer(signaux: list[dict], profil: list[dict], seuil: float = SEUIL_DEFAUT) -> dict:
    """signaux : [{"id", "source", "embedding", ...}]. Tout rejet est journalisé avec
    son score : un filtre qui jette sans trace ne se calibre jamais."""
    retenus, rejetes = [], []
    for s in signaux:
        r = pertinence(s["embedding"], profil)
        entree = {"id": s["id"], "source": s.get("source"), **r}
        (retenus if r["score"] >= seuil else rejetes).append(entree)
    retenus.sort(key=lambda e: e["score"], reverse=True)
    return {"retenus": retenus, "rejetes": rejetes, "seuil": seuil}


def calibrer_seuil(scores_pertinents: list[float], scores_non_pertinents: list[float]) -> dict:
    """Choisit le seuil qui maximise l'exactitude équilibrée sur des exemples
    étiquetés à la main. Recommandation : ≥ 30 exemples de chaque classe."""
    if not scores_pertinents or not scores_non_pertinents:
        raise ValueError("il faut des exemples des deux classes")
    candidats = sorted(set(scores_pertinents) | set(scores_non_pertinents))
    meilleur = (0.0, SEUIL_DEFAUT)
    for t in candidats:
        vp = sum(s >= t for s in scores_pertinents) / len(scores_pertinents)
        vn = sum(s < t for s in scores_non_pertinents) / len(scores_non_pertinents)
        score = (vp + vn) / 2
        if score > meilleur[0]:
            meilleur = (score, t)
    return {"seuil": round(meilleur[1], 4), "exactitude_equilibree": round(meilleur[0], 4),
            "n": len(scores_pertinents) + len(scores_non_pertinents)}
