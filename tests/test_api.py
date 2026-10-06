from kael_core import api, serveur


def test_routes(identite):
    assert api.traiter("/sante", {})[0] == 200
    code, corps = api.traiter("/identite/valider", {"identite": identite, "strict": True})
    assert code == 200 and corps["fautes"] == []
    code, corps = api.traiter("/prompt/plumitif", {"identite": identite, "plateforme": "bluesky"})
    assert code == 200 and "Rang 0" in corps["prompt"]


def test_impulse_par_l_api():
    c = {"pertinence": 0.95, "heures_silence": 10, "engagement_recent": 0.5,
         "publications_aujourdhui": 0, "maintenant": "2026-10-06T10:00:00+02:00",
         "parametres": {"entropie": 0.0}}
    code, r = api.traiter("/impulse/decider", c)
    assert code == 200 and r["publier"]
    c["maintenant"] = "2026-10-06T03:00:00+02:00"
    assert api.traiter("/impulse/decider", c)[1]["motif"] == "heures_de_sommeil"


def test_erreurs_declarees():
    assert api.traiter("/inconnue", {})[0] == 404
    assert api.traiter("/dogme/appliquer", {"dogme": {}})[0] == 400
    assert api.traiter("/sante", [])[0] == 400
    c = {"pertinence": 0.9, "heures_silence": 1, "engagement_recent": 0,
         "publications_aujourdhui": 0, "maintenant": "2026-10-06T10:00:00"}
    code, r = api.traiter("/impulse/decider", c)
    assert code == 400 and "fuseau" in r["erreur"]


def test_le_serveur_refuse_de_demarrer_sans_jeton(monkeypatch):
    monkeypatch.delenv("KAEL_API_TOKEN", raising=False)
    assert serveur.main([]) == 2
    monkeypatch.setenv("KAEL_API_TOKEN", "court")
    assert serveur.main([]) == 2
