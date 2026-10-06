import copy

from kael_core import identite as idt


def test_fixture_conforme_en_strict(identite):
    assert idt.valider(identite, strict=True) == []


def test_template_conforme_en_structure_mais_pas_pret(template):
    assert idt.valider(template) == []
    fautes = idt.valider(template, strict=True)
    assert any("À DÉFINIR" in f for f in fautes)


def test_la_transparence_n_est_pas_un_reglage(identite):
    identite["transparence"]["repondre_oui_si_question_ia"] = False
    assert any("Voie A" in f for f in idt.valider(identite))


def test_plateforme_active_sans_mention_refusee_en_strict(identite):
    identite["plateformes_actives"].append("x")
    assert any("« x »" in f for f in idt.valider(identite, strict=True))


def test_vecteur_hors_bornes_et_axe_inconnu(identite):
    identite["vecteurs"]["rigueur"]["valeur"] = 0.99
    identite["vecteurs"]["charisme"] = {"valeur": 0.5, "min": 0, "max": 1}
    fautes = idt.valider(identite)
    assert any("rigueur" in f for f in fautes)
    assert any("charisme" in f for f in fautes)


def test_id_duplique_et_rang_invalide(identite):
    identite["dogmes"].append(copy.deepcopy(identite["dogmes"][0]))
    identite["dogmes"][1]["rank"] = 3
    fautes = idt.valider(identite)
    assert any("dupliqué" in f for f in fautes)
    assert any("rank" in f for f in fautes)


def test_strict_exige_un_rang_0(identite):
    identite["dogmes"] = [d for d in identite["dogmes"] if d["rank"] != 0]
    assert any("rang 0" in f for f in idt.valider(identite, strict=True))


def test_empreinte_independante_de_l_ordre_des_cles(identite):
    inverse = dict(reversed(list(identite.items())))
    assert idt.empreinte(inverse) == idt.empreinte(identite)
    identite["nom_public"] += "."
    assert idt.empreinte(inverse) != idt.empreinte(identite)
