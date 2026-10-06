import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from kael_core import rythme as ry

PARIS = ZoneInfo("Europe/Paris")


def test_sommeil():
    assert ry.en_sommeil(datetime(2026, 10, 6, 2, 0, tzinfo=PARIS))
    assert ry.en_sommeil(datetime(2026, 10, 6, 23, 30, tzinfo=PARIS))
    assert not ry.en_sommeil(datetime(2026, 10, 6, 10, 0, tzinfo=PARIS))


def test_prochain_creneau_jamais_dans_le_sommeil_ni_dans_le_passe():
    rng = random.Random(3)
    depart = datetime(2026, 10, 6, 20, 30, tzinfo=timezone.utc)
    for _ in range(500):
        t = ry.prochain_creneau(depart, rng=rng)
        assert t > depart and not ry.en_sommeil(t)


def test_delais_de_reponse():
    rng = random.Random(1)
    assert all(1 <= ry.delai_reponse_minutes("commentaire", rng) <= 15 for _ in range(200))
    assert all(60 <= ry.delai_reponse_minutes("dm", rng) <= 360 for _ in range(200))
    with pytest.raises(ValueError):
        ry.delai_reponse_minutes("story")
