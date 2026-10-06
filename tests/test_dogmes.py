import copy
import itertools

import pytest

from kael_core import dogmes as dg

D = {"texte": "donnée", "source": "interaction_1"}
Q = "2026-10-06"


def dogme(rang):
    return {"id": f"D-{rang}", "core": "Je préfère le matin", "rank": rang, "confidence": 1.0,
            "context": [], "defended_challenges": [], "rejected_challenges": []}


def enrich(type_, impl=None):
    return {"operation": "ENRICH", "type": type_, "implication": impl}


# --- l'invariant central -------------------------------------------------------

JUGEMENTS = (
    [{"operation": "REJECT"}]
    + [enrich(t, i) for t, i in itertools.product(dg.TYPES_ENRICHISSEMENT, dg.IMPLICATIONS)]
    + [{"operation": "DEFEND", "methode": m, "defense": "x", "nuance": n}
       for m, n in itertools.product(dg.METHODES, (False, True))]
)


@pytest.mark.parametrize("rang", (0, 1, 2))
@pytest.mark.parametrize("cadre", ("ia_native", "personnage_declare"))
def test_aucune_operation_ne_touche_au_core_ni_a_l_entree(rang, cadre):
    for j in JUGEMENTS:
        d = dogme(rang)
        gel = copy.deepcopy(d)
        r = dg.appliquer(d, D, j, cadre, Q)
        assert d == gel, "l'entrée a été modifiée en place"
        assert r["dogme"]["core"] == gel["core"]
        if r["propose"]:
            assert r["propose"]["core"] == gel["core"]


# --- REJECT / ENRICH ---------------------------------------------------------------

def test_reject_journalise_en_silence():
    r = dg.appliquer(dogme(1), D, {"operation": "REJECT"}, quand=Q)
    assert r["statut"] == dg.REJETE and r["reponse_publique"] is False
    assert r["dogme"]["rejected_challenges"][0]["motif"] == "renversement_du_core"


def test_factuel_applique_automatiquement():
    r = dg.appliquer(dogme(2), D, enrich("factuel"), quand=Q)
    assert r["statut"] == dg.APPLIQUE and len(r["dogme"]["context"]) == 1


def test_causal_sans_test_d_implication_demande_un_audit():
    r = dg.appliquer(dogme(1), D, enrich("causal"), quand=Q)
    assert r["statut"] == dg.AUDIT_REQUIS
    assert r["dogme"]["context"] == [] and len(r["propose"]["context"]) == 1


def test_causal_neutre_applique():
    assert dg.appliquer(dogme(1), D, enrich("causal", "neutre"), quand=Q)["statut"] == dg.APPLIQUE


def test_affaiblissement_admis_au_rang_2_mais_pas_au_rang_1():
    assert dg.appliquer(dogme(2), D, enrich("interpretatif", "affaiblit"))["statut"] == dg.APPLIQUE
    assert dg.appliquer(dogme(1), D, enrich("interpretatif", "affaiblit"))["statut"] == dg.VALIDATION_HUMAINE


def test_enrichissement_troyen_requalifie_en_rejet():
    r = dg.appliquer(dogme(2), D, enrich("factuel", "renverse"), quand=Q)
    assert r["statut"] == dg.REJETE
    assert r["dogme"]["rejected_challenges"][0]["motif"] == "enrichissement_troyen"


def test_tout_enrichissement_de_rang_0_passe_par_l_humain():
    for t in ("factuel", "causal", "interpretatif"):
        r = dg.appliquer(dogme(0), D, enrich(t, "neutre"), quand=Q)
        assert r["statut"] == dg.VALIDATION_HUMAINE and r["dogme"]["context"] == []


def test_biographie_rejetee_pour_une_ia_native_admise_pour_un_personnage_declare():
    r = dg.appliquer(dogme(2), D, enrich("biographique", "neutre"), "ia_native", Q)
    assert r["statut"] == dg.REJETE
    r = dg.appliquer(dogme(2), D, enrich("biographique", "neutre"), "personnage_declare", Q)
    assert r["statut"] == dg.APPLIQUE


# --- DEFEND -------------------------------------------------------------------------

def test_methodes_de_defense_restreintes_par_rang():
    j = {"operation": "DEFEND", "methode": "deduction", "defense": "…"}
    assert dg.appliquer(dogme(2), D, j)["statut"] == dg.REFUSE
    assert dg.appliquer(dogme(1), D, j)["statut"] == dg.APPLIQUE
    j["methode"] = "abduction"
    assert dg.appliquer(dogme(1), D, j)["statut"] == dg.REFUSE
    r = dg.appliquer(dogme(0), D, j)
    assert r["statut"] == dg.APPLIQUE
    assert r["dogme"]["defended_challenges"][0]["dogma_status"] == "renforcé"


def test_le_rang_0_ne_concede_jamais():
    j = {"operation": "DEFEND", "methode": "dialectique", "defense": "…", "nuance": True}
    assert dg.appliquer(dogme(0), D, j)["statut"] == dg.VALIDATION_HUMAINE
    j["methode"] = "induction"
    assert dg.appliquer(dogme(1), D, j)["statut"] == dg.APPLIQUE


def test_l_exemple_des_asperges_est_refuse_pour_une_ia_declaree():
    # « J'ai goûté toute la famille des légumes » : défense par vécu inventé.
    j = {"operation": "DEFEND", "methode": "induction", "defense_biographique": True,
         "defense": "J'ai goûté toute la famille des légumes similaires"}
    assert dg.appliquer(dogme(2), D, j, "ia_native")["statut"] == dg.REFUSE
    assert dg.appliquer(dogme(2), D, j, "personnage_declare")["statut"] == dg.APPLIQUE


def test_defense_vide_ou_operation_inconnue_refusees():
    assert dg.appliquer(dogme(0), D, {"operation": "DEFEND", "methode": "induction"})["statut"] == dg.REFUSE
    assert dg.appliquer(dogme(0), D, {"operation": "MERGE"})["statut"] == dg.REFUSE


# --- sentinelles ----------------------------------------------------------------------

def test_le_glissement_progressif_est_attrape_par_la_solidite():
    d = dogme(2)
    for i in range(6):
        r = dg.appliquer(d, {"texte": f"nuance {i}"}, enrich("interpretatif", "affaiblit"), quand=Q)
        assert r["statut"] == dg.APPLIQUE   # chaque pas, pris seul, est légitime
        d = r["dogme"]
        if i < 5:
            assert "consolidation_requise" not in r["alertes"]
    assert dg.solidite(d) < dg.SEUIL_SOLIDITE
    assert "consolidation_requise" in r["alertes"]


def test_les_defenses_ne_rechargent_pas_indefiniment():
    d = dogme(0)
    d["defended_challenges"] = [{"dogma_status": "renforcé"}] * 100
    d["context"] = [{"implication": "affaiblit"}] * 3
    assert dg.solidite(d) == pytest.approx(1 - 3 * dg.PENALITE_AFFAIBLIT + dg.BONUS_DEFENSE_MAX)


def test_compression_due_au_seuil():
    d = dogme(2)
    d["context"] = [{"implication": "neutre"}] * (dg.SEUIL_COMPRESSION - 1)
    assert "compression_due" not in dg.alertes(d)
    d["context"].append({"implication": "neutre"})
    assert "compression_due" in dg.alertes(d)


# --- cycle long ----------------------------------------------------------------------

def test_compression_rang_0_exige_une_decision_humaine():
    d = dogme(0)
    d["context"] = [{"enrichment": "a", "implication": "neutre"}] * 3
    r = dg.compresser(d, "récit", quand=Q)
    assert r["statut"] == dg.VALIDATION_HUMAINE and len(r["dogme"]["context"]) == 3
    decision = {"auteur": "Lazerr", "date": Q, "motif": "consolidation trimestrielle"}
    r = dg.compresser(d, "récit", decision, Q)
    assert r["statut"] == dg.APPLIQUE
    assert r["dogme"]["context"][0]["type"] == "recit_canonique"
    assert len(r["dogme"]["archive"][0]["context"]) == 3
    assert r["dogme"]["core"] == d["core"]


def test_compression_rang_2_automatique():
    assert dg.compresser(dogme(2), "récit", quand=Q)["statut"] == dg.APPLIQUE


def test_reviser_core_exige_une_decision_complete_et_trace_l_ancien():
    assert dg.reviser_core(dogme(0), "Autre", {"auteur": "Lazerr"})["statut"] == dg.REFUSE
    r = dg.reviser_core(dogme(0), "Autre", {"auteur": "Lazerr", "date": Q, "motif": "m"})
    assert r["dogme"]["core"] == "Autre"
    assert r["dogme"]["revisions"][0]["ancien_core"] == "Je préfère le matin"


def test_conflits_entre_dogmes():
    assert dg.resoudre_conflit(dogme(0), dogme(2)) == {"statut": "hierarchie", "prevaut": "D-0"}
    assert dg.resoudre_conflit(dogme(1), dogme(1))["statut"] == "tolere"
    assert dg.resoudre_conflit(dogme(0), dogme(0))["statut"] == dg.VALIDATION_HUMAINE
