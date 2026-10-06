import pytest

from kael_core import percept as pc

PROFIL = [{"id": "niche:a", "embedding": [1.0, 0.0, 0.0]},
          {"id": "niche:b", "embedding": [0.0, 1.0, 0.0], "poids": 0.9}]


def test_dimensions_incompatibles_refusees():
    # Le piège de la spécification : comparer un embedding à un vecteur à 5 axes.
    with pytest.raises(ValueError, match="même modèle"):
        pc.cosinus([0.1] * 1024, [0.5] * 5)


def test_filtrer_trie_et_journalise_les_rejets():
    signaux = [{"id": "s1", "embedding": [0.9, 0.1, 0.0]},
               {"id": "s2", "embedding": [0.0, 0.0, 1.0]},
               {"id": "s3", "embedding": [0.1, 1.0, 0.0]}]
    r = pc.filtrer(signaux, PROFIL)
    assert [e["id"] for e in r["retenus"]] == ["s1", "s3"]
    assert r["retenus"][1]["ancre"] == "niche:b"
    assert r["rejetes"][0]["id"] == "s2" and r["rejetes"][0]["score"] == 0.0


def test_calibrer_seuil_separe_les_classes():
    r = pc.calibrer_seuil([0.41, 0.45, 0.52, 0.60], [0.10, 0.22, 0.30, 0.38])
    assert r["exactitude_equilibree"] == 1.0 and 0.38 < r["seuil"] <= 0.41
    with pytest.raises(ValueError):
        pc.calibrer_seuil([], [0.1])
