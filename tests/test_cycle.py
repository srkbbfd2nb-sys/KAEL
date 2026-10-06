import pytest

from kael_core import cycle as cy

Q = "2026-10-06"


def test_parcours_nominal_avec_validation_humaine():
    it = cy.nouveau("p1", Q)
    it = cy.appliquer_verdict(it, {"verdict": "escalader", "escalades": ["classe_non_autonome:post"]}, Q)
    assert it["etat"] == "en_validation"
    it = cy.avancer(it, "valide", "humain:Lazerr", Q)
    it = cy.avancer(it, "planifie", "systeme", Q)
    it = cy.avancer(it, "publie", "systeme", Q)
    assert [h["vers"] for h in it["historique"]] == [
        "brouillon", "en_validation", "valide", "planifie", "publie"]


def test_seul_un_humain_valide():
    it = cy.appliquer_verdict(cy.nouveau("p", Q), {"verdict": "escalader"}, Q)
    for acteur in ("systeme", "guard", "agent:juge"):
        with pytest.raises(cy.TransitionRefusee, match="INV.4"):
            cy.avancer(it, "valide", acteur, Q)


def test_pas_de_raccourci_autour_de_guard():
    with pytest.raises(cy.TransitionRefusee):
        cy.avancer(cy.nouveau("p", Q), "planifie", "systeme", Q)


def test_terminal_et_etat_inconnu():
    it = cy.avancer(cy.nouveau("p", Q), "abandonne", "systeme", Q)
    with pytest.raises(cy.TransitionRefusee, match="terminal"):
        cy.avancer(it, "brouillon", "systeme", Q)
    with pytest.raises(cy.TransitionRefusee, match="inconnu"):
        cy.avancer(cy.nouveau("p", Q), "envoye", "systeme", Q)


def test_trois_regenerations_puis_abandon():
    it = cy.nouveau("p", Q)
    bloque = {"verdict": "bloquer", "bloquants": ["identite_sous_seuil"]}
    for i in range(cy.MAX_REGENERATIONS):
        it = cy.appliquer_verdict(it, bloque, Q)
        assert it["etat"] == "a_regenerer"
        it = cy.avancer(it, "brouillon", "systeme", Q)
    it = cy.appliquer_verdict(it, bloque, Q)
    assert it["etat"] == "abandonne"


def test_reessais_de_publication_bornes():
    it = cy.appliquer_verdict(cy.nouveau("p", Q), {"verdict": "publier"}, Q)
    it = cy.avancer(it, "planifie", "systeme", Q)
    for _ in range(cy.MAX_REESSAIS):
        it = cy.avancer(it, "echec", "systeme", Q, "429")
        it = cy.avancer(it, "planifie", "systeme", Q)
    it = cy.avancer(it, "echec", "systeme", Q)
    with pytest.raises(cy.TransitionRefusee, match="réessais"):
        cy.avancer(it, "planifie", "systeme", Q)


def test_l_entree_n_est_pas_modifiee():
    it = cy.nouveau("p", Q)
    cy.avancer(it, "abandonne", "systeme", Q)
    assert it["etat"] == "brouillon" and len(it["historique"]) == 1
