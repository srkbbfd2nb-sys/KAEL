import json
import sys
from pathlib import Path

import pytest

KAEL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KAEL))


@pytest.fixture
def identite():
    return json.loads((KAEL / "tests" / "fixtures" / "identite_test.json").read_text(encoding="utf-8"))


@pytest.fixture
def template():
    return json.loads((KAEL / "identite" / "identite.template.json").read_text(encoding="utf-8"))
