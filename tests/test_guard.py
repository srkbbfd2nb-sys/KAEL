import pytest

from kael_core import guard as gd

AUTO = {"post_original": "auto", "reponse": "auto"}


def candidat(**k):
    c = {"plateforme": "bluesky", "classe": "post_original", "texte": "Une idée neuve sur la mesure.",
         "scores": {"identite": 0.9, "securite": "ok"}}
    c.update(k)
    return c


def ctx(**k):
    c = {"coupe_circuit": False, "cout_jour_usd": 1.0, "plafond_jour_usd": 5.0,
         "politique_autonomie": AUTO}
    c.update(k)
    return c


def test_candidat_propre_avec_autonomie_accordee(identite):
    assert gd.verifier(candidat(), identite, ctx())["verdict"] == gd.PUBLIER


def test_sans_politique_d_autonomie_tout_escalade(identite):
    r = gd.verifier(candidat(), identite, ctx(politique_autonomie={}))
    assert r["verdict"] == gd.ESCALADER and "classe_non_autonome:post_original" in r["escalades"]


def test_echec_ferme_sur_score_ou_moderation_absents(identite):
    r = gd.verifier(candidat(scores={}), identite, ctx())
    assert r["verdict"] == gd.ESCALADER
    assert set(r["escalades"]) == {"moderation_incertaine_ou_absente", "score_identite_absent"}


def test_tous_les_motifs_sont_collectes(identite):
    r = gd.verifier(candidat(plateforme="x", scores={"identite": 0.5, "securite": "bloque"}),
                    identite, ctx(coupe_circuit=True, cout_jour_usd=9.0))
    assert r["verdict"] == gd.BLOQUER
    assert len(r["bloquants"]) == 5


@pytest.mark.parametrize("question", [
    "Attends, t'es un bot ou quoi ?", "Es-tu une IA ?", "are you an AI?",
    "Vous êtes humain derrière ce compte ?"])
def test_question_ia_exige_l_affirmation_en_tete(identite, question):
    esquive = candidat(classe="reponse", texte="Qu'est-ce qui te fait dire ça ?",
                       en_reponse_a={"texte": question})
    assert "question_ia_sans_affirmation" in gd.verifier(esquive, identite, ctx())["bloquants"]
    franc = candidat(classe="reponse", texte="Oui, je suis une IA. Et la question est bonne.",
                     en_reponse_a={"texte": question})
    assert gd.verifier(franc, identite, ctx())["verdict"] == gd.PUBLIER


def test_le_classifieur_semantique_prime_sur_le_filet_lexical(identite):
    c = candidat(classe="reponse", texte="Bonne question !",
                 en_reponse_a={"texte": "Y a quelqu'un de vivant ici ?", "question_nature_ia": True})
    assert gd.verifier(c, identite, ctx())["verdict"] == gd.BLOQUER


def test_doublon_et_exploration_profonde(identite):
    t = "Une idée neuve sur la mesure des choses invisibles."
    r = gd.verifier(candidat(texte=t), identite, ctx(historique_textes=[t]))
    assert any(b.startswith("doublon") for b in r["bloquants"])
    r = gd.verifier(candidat(exploration="profond"), identite, ctx())
    assert r["verdict"] == gd.ESCALADER
