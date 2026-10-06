import copy

from kael_core import vecteurs as vc
from kael_core.identite import AXES

Q = "2026-10-06"


def test_modulation_bornee_par_pas_et_par_axe(identite):
    v = identite["vecteurs"]
    gel = copy.deepcopy(v)
    nv, j = vc.moduler(v, {"rigueur": 0.5, "curiosite": 0.02}, "humain", Q)
    assert v == gel
    assert nv["rigueur"]["valeur"] == 0.82                     # pas_max = 0.02
    assert nv["curiosite"]["valeur"] == 0.87
    assert {e["axe"]: e["statut"] for e in j} == {"rigueur": "ecrete", "curiosite": "applique"}
    for _ in range(50):
        nv, _ = vc.moduler(nv, {"rigueur": 0.02}, "humain", Q)
    assert nv["rigueur"]["valeur"] == v["rigueur"]["max"]      # borne d'axe


def test_l_engagement_ne_module_pas_un_axe_protege(identite):
    nv, j = vc.moduler(identite["vecteurs"], {"cynisme": 0.02}, "engagement", Q)
    assert nv["cynisme"]["valeur"] == identite["vecteurs"]["cynisme"]["valeur"]
    assert j[0]["statut"] == "non_modulable_par_engagement"


def test_axe_inconnu_journalise():
    _, j = vc.moduler({}, {"charisme": 0.01}, "humain", Q)
    assert j[0]["statut"] == "axe_inconnu"


def _plat(val):
    return {a: {"valeur": val, "min": 0.0, "max": 1.0} for a in AXES}


def test_le_cosinus_est_aveugle_a_une_derive_uniforme_l_audit_ne_l_est_pas():
    # Tous les axes montent de 0,15 : aucun axe n'atteint 0,20 et le cosinus ne
    # voit presque rien. La norme L2 (0,335) déclenche l'alerte multi-axes.
    initiaux = {a: {"valeur": x, "min": 0, "max": 1} for a, x in zip(AXES, (0.5, 0.6, 0.3, 0.5, 0.7))}
    actuels = {a: {"valeur": initiaux[a]["valeur"] + 0.15, "min": 0, "max": 1} for a in AXES}
    r = vc.audit_derive(actuels, initiaux)
    assert r["cosinus_info"] < 0.02
    assert r["max_axe"] < vc.SEUIL_AXE
    assert r["alertes"] == ["global"] and r["action"] == "snapshot_et_notification"


def test_alerte_par_axe():
    actuels = _plat(0.5)
    actuels["empathie"]["valeur"] = 0.25
    r = vc.audit_derive(actuels, _plat(0.5))
    assert "axe:empathie" in r["alertes"]


def test_aucune_derive():
    assert vc.audit_derive(_plat(0.4), _plat(0.4))["action"] == "aucune"
