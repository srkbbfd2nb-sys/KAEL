"""
GUARD — verdict pré-publication.

Chaque candidat à la publication reçoit un verdict unique : `publier`,
`escalader` (la chaîne est suspendue et reprenable : un humain tranche) ou
`bloquer`. Tous les contrôles s'exécutent, même après un premier échec : le
journal doit dire *tout* ce qui n'allait pas, pas seulement la première faute.

Par défaut, GUARD échoue fermé : un score manquant ou une modération
« incertaine » escaladent, ils ne passent pas.

La question « es-tu une IA ? » n'est pas laissée à la génération libre : si elle
est détectée, la réponse doit **commencer** par l'affirmation inscrite dans
l'identité (`transparence.reponse_question_ia`). La détection combine le
jugement sémantique du classifieur (prioritaire) et un filet lexical, qui n'est
qu'un plancher : il rattrape l'évident, il ne prétend pas tout voir.

Publier est une action irréversible : sans politique d'autonomie décidée par
l'humain (D-09), toute classe de contenu escalade (INV.4).
"""

from __future__ import annotations

import re
import unicodedata

SEUIL_IDENTITE = 0.80        # palier de la spécification — à recalibrer (C2)
SEUIL_DOUBLON = 0.85         # similarité de Jaccard sur trigrammes de mots
SEUIL_SUJET = 0.85           # cosinus d'embedding du sujet, 90 jours — à recalibrer (C2)

PUBLIER, ESCALADER, BLOQUER = "publier", "escalader", "bloquer"

_QUESTION_IA = re.compile(
    r"\b(es[- ]?tu|t'?es|tu es|êtes[- ]vous|vous êtes|est[- ]ce que (tu es|vous êtes)|"
    r"are you|r u|is this)\b[^?!.]{0,40}?\b(une? )?(ia|ai|bot|robot|humain|humaine|human|"
    r"machine|llm|programme|vrai|vraie|real|person|personne)\b",
    re.IGNORECASE)


def _normaliser(t: str) -> str:
    t = unicodedata.normalize("NFKC", t).lower()
    return re.sub(r"\s+", " ", t).strip()


def question_ia_detectee(message: dict | None) -> bool:
    if not message:
        return False
    if message.get("question_nature_ia") is True:
        return True
    return bool(_QUESTION_IA.search(message.get("texte", "")))


def similarite(a: str, b: str, n: int = 3) -> float:
    def trig(t):
        m = _normaliser(t).split()
        return {tuple(m[i:i + n]) for i in range(max(1, len(m) - n + 1))}
    x, y = trig(a), trig(b)
    return len(x & y) / len(x | y) if x | y else 0.0


def cle_operation(plateforme: str, action: str, cible: str) -> str:
    """Clé d'idempotence : on ne répond pas deux fois au même message, on ne
    republie pas deux fois la même chose. Journal des opérations tenu par N8N."""
    return f"{plateforme}:{action}:{cible}"


def verifier(candidat: dict, identite: dict, contexte: dict) -> dict:
    """candidat : {plateforme, classe, texte, en_reponse_a?, exploration?,
                   scores: {identite?, securite?}}
    contexte : {coupe_circuit, cout_jour_usd, plafond_jour_usd,
                politique_autonomie, historique_textes?, seuil_identite?,
                operations_faites?}
    candidat peut porter `action` et `cible` (id du message auquel on répond)
    pour le contrôle d'idempotence, et `scores.similarite_sujet` (max sur 90 j)."""
    bloquants, escalades = [], []
    plateforme = candidat.get("plateforme")
    texte = candidat.get("texte", "")
    scores = candidat.get("scores", {})
    transparence = identite.get("transparence", {})

    if contexte.get("coupe_circuit"):
        bloquants.append("coupe_circuit_actif")

    if not str(transparence.get("mention_par_plateforme", {}).get(plateforme, "")).strip():
        bloquants.append(f"transparence_absente:{plateforme}")

    if question_ia_detectee(candidat.get("en_reponse_a")):
        affirmation = _normaliser(transparence.get("reponse_question_ia", ""))
        if not affirmation or not _normaliser(texte).startswith(affirmation):
            bloquants.append("question_ia_sans_affirmation")

    securite = scores.get("securite")
    if securite == "bloque":
        bloquants.append("moderation_bloque")
    elif securite != "ok":
        escalades.append("moderation_incertaine_ou_absente")

    seuil_id = contexte.get("seuil_identite", SEUIL_IDENTITE)
    s_id = scores.get("identite")
    if s_id is None:
        escalades.append("score_identite_absent")
    elif s_id < seuil_id:
        bloquants.append(f"identite_sous_seuil:{s_id:.2f}<{seuil_id:.2f}")

    plafond = contexte.get("plafond_jour_usd")
    if plafond is not None and contexte.get("cout_jour_usd", 0.0) >= plafond:
        bloquants.append("plafond_budget_atteint")

    doublon = max((similarite(texte, h) for h in contexte.get("historique_textes", [])), default=0.0)
    if doublon >= SEUIL_DOUBLON:
        bloquants.append(f"doublon:{doublon:.2f}")

    if candidat.get("cible"):
        cle = cle_operation(plateforme, candidat.get("action", candidat.get("classe", "")),
                            candidat["cible"])
        if cle in set(contexte.get("operations_faites", [])):
            bloquants.append(f"operation_deja_faite:{cle}")

    s_sujet = scores.get("similarite_sujet")
    if s_sujet is not None and s_sujet >= contexte.get("seuil_sujet", SEUIL_SUJET):
        bloquants.append(f"sujet_deja_traite:{s_sujet:.2f}")

    if candidat.get("exploration") == "profond":
        escalades.append("exploration_profonde")

    classe = candidat.get("classe", "inconnue")
    if contexte.get("politique_autonomie", {}).get(classe) != "auto":
        escalades.append(f"classe_non_autonome:{classe}")

    verdict = BLOQUER if bloquants else ESCALADER if escalades else PUBLIER
    return {"verdict": verdict, "bloquants": bloquants, "escalades": escalades,
            "similarite_max": round(doublon, 4)}
