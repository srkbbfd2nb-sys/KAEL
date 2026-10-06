"""Mécanismes repris de l'étude des dépôts de référence (docs/etat_de_lart.md)."""
import pytest

from kael_core import guard as gd, identite as idt, impulse as im, percept as pc, prompt as pr
from kael_core import vecteurs as vc
from kael_core.identite import AXES

AUTO = {"reponse": "auto", "post_original": "auto"}
CTX = {"coupe_circuit": False, "politique_autonomie": AUTO}


def _cand(**k):
    c = {"plateforme": "bluesky", "classe": "reponse", "texte": "Point intéressant.",
         "scores": {"identite": 0.9, "securite": "ok"}}
    c.update(k)
    return c


def test_on_ne_repond_jamais_deux_fois_au_meme_message(identite):
    cle = gd.cle_operation("bluesky", "reponse", "at://msg/42")
    r = gd.verifier(_cand(cible="at://msg/42"), identite, {**CTX, "operations_faites": [cle]})
    assert r["verdict"] == gd.BLOQUER and r["bloquants"] == [f"operation_deja_faite:{cle}"]
    assert gd.verifier(_cand(cible="at://msg/43"), identite,
                       {**CTX, "operations_faites": [cle]})["verdict"] == gd.PUBLIER


def test_meme_angle_avec_d_autres_mots_est_bloque(identite):
    c = _cand(scores={"identite": 0.9, "securite": "ok", "similarite_sujet": 0.91})
    assert any(b.startswith("sujet_deja_traite") for b in gd.verifier(c, identite, CTX)["bloquants"])


def test_sujet_le_plus_proche():
    r = pc.sujet_le_plus_proche([1.0, 0.0], [{"id": "a", "embedding": [0.0, 1.0]},
                                            {"id": "b", "embedding": [0.9, 0.1]}])
    assert r["id"] == "b" and r["similarite_sujet"] > 0.99


def test_regle_apprise_sans_validation_humaine_refusee(identite):
    identite["regles_apprises"] = [{"regle": "Jamais d'emoji en ouverture", "source": "retouche 12"}]
    assert any("décision humaine" in f for f in idt.valider(identite))
    identite["regles_apprises"][0]["decision"] = {"auteur": "Lazerr", "date": "2026-10-06"}
    assert idt.valider(identite, strict=True) == []
    assert "Jamais d'emoji en ouverture" in pr.construire(identite, "bluesky")


def test_empreinte_de_voix_bornee(identite):
    p = pr.construire(identite, "bluesky", exemples=[f"post {i}" for i in range(9)])
    assert p.count("<exemple>") == pr.MAX_EXEMPLES


@pytest.mark.parametrize("jour, attendu", [(0, 1), (6, 2), (13, 4), (40, 4)])
def test_rodage_d_un_compte_neuf(jour, attendu):
    assert im.quota_rodage(4, jour, 14) == attendu


def test_le_rodage_bloque_avant_le_quota_plein():
    p = im.Parametres(entropie=0.0)
    assert im.decider(0.95, 5, 0.5, 1, False, p, jours_compte=0)["motif"] == "quota_journalier"
    assert im.decider(0.95, 5, 0.5, 1, False, p, jours_compte=30)["publier"]


def test_personnalite_exprimee_qui_s_eloigne_de_la_declaree(identite):
    declares = identite["vecteurs"]
    exprimes = {a: dict(declares[a]) for a in AXES}
    exprimes["cynisme"]["valeur"] = 0.55   # le juge lit bien plus de cynisme que déclaré
    r = vc.audit_expression(declares, exprimes)
    assert "axe:cynisme" in r["alertes"] and r["action"] == "recalibrer_prompt"
    assert vc.audit_expression(declares, declares)["action"] == "aucune"
