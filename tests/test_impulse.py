import random

import pytest

from kael_core import impulse as im

CALME = im.Parametres(entropie=0.0)


def test_parametres_gardes():
    with pytest.raises(ValueError):
        im.Parametres(entropie=0.2)
    with pytest.raises(ValueError):
        im.Parametres(poids_pertinence=0.9)


@pytest.mark.parametrize("args, motif", [
    ((0.95, 48, 1.0, 0, True), "heures_de_sommeil"),
    ((0.95, 48, 1.0, 4, False), "quota_journalier"),
    ((0.55, 48, 1.0, 0, False), "aucun_signal_pertinent"),
    ((0.95, 0.5, 1.0, 0, False), "ecart_minimal"),
])
def test_verrous_avant_la_formule(args, motif):
    r = im.decider(*args, p=CALME)
    assert r["publier"] is False and r["motif"] == motif


def test_l_envie_monte_avec_le_silence():
    tot = im.decider(0.65, 2, 0.5, 0, False, CALME)
    tard = im.decider(0.65, 24, 0.5, 0, False, CALME)
    assert not tot["publier"] and tard["publier"]
    assert tard["p_a"] == pytest.approx(0.455 + 0.20 + 0.05)


def test_un_signal_tout_juste_pertinent_ne_suffit_pas_seul():
    assert not im.decider(0.60, 48, 0.0, 0, False, CALME)["publier"]


def test_signal_fort_publie_vite_mais_jamais_en_rafale():
    assert im.decider(0.95, 2, 0.5, 0, False, CALME)["publier"]
    assert im.decider(0.95, 1, 1.0, 0, False, CALME)["motif"] == "ecart_minimal"


def test_p_a_toujours_borne_et_exploration_coherente():
    rng = random.Random(7)
    vus = set()
    for _ in range(2000):
        r = im.decider(rng.random() * 0.4 + 0.6, rng.random() * 100, rng.random(), 0, False,
                       im.Parametres(entropie=0.15), rng)
        assert 0.0 <= r["p_a"] <= 1.0
        assert r["validation_requise"] == (r["exploration"] == "profond")
        vus.add(r["exploration"])
    assert vus == {"normal", "controle", "profond"}


def test_sans_entropie_jamais_d_exploration():
    assert {im.niveau_exploration(x / 100, 0.0) for x in range(100)} == {"normal"}
