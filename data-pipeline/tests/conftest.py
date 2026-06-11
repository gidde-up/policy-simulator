import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402

BUILT_COUNTRIES = ["ZAF", "TUN"]


@pytest.fixture(scope="session", params=BUILT_COUNTRIES)
def country(request):
    return request.param


@pytest.fixture(scope="session")
def country_data():
    """All built country JSONs. FAILS (not skips) if missing -- the
    JSONs are the session deliverable."""
    data = {}
    for c in BUILT_COUNTRIES:
        path = config.OUTPUT_DIR / f"{c}.json"
        assert path.exists(), (
            f"{path} missing -- run `python run_pipeline.py {c}` first")
        data[c] = json.loads(path.read_text(encoding="utf-8"))
    return data


@pytest.fixture(scope="session")
def registry():
    assert config.ASSUMPTIONS_JSON.exists(), "assumptions.json missing"
    return json.loads(config.ASSUMPTIONS_JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def old_multipliers():
    import make_comparison
    return make_comparison.load_old_multipliers()
