"""Session E regression lock: the composable-shock refactor must
reproduce the v1.0.0 engine's run_scenario output exactly.

The fixture (tests/fixtures/engine_regression_v1.json) was generated
from the committed v1.0.0 engine (commit + sha256 recorded inside).
Comparison is recursive:
  - identical key sets at every level (API shape lock)
  - strings / bools / None by equality (locks channel labels and note
    wording)
  - numbers by approx(rel=1e-6, abs=1e-8) -- the abs floor handles
    near-zero values; the rel tolerance leaves ~10 orders of magnitude
    of headroom over float-association noise and absorbs BLAS
    differences across machines.
"""
import json
from pathlib import Path

import pytest

# History: the v1.0.0 lock proved the Session-E composable-shock refactor
# was numerically inert. The v1.2 financing model (Workstream C) and the
# Senegal elasticity correction (Workstream D) intentionally changed
# outputs, so after the Workstream C verification stop the fixture was
# REGENERATED from the committed v1.2 engine (default tax_financed
# financing, all levers compiled through to_engine_kwargs). It now locks
# the v1.2 behaviour against future drift. Regenerate with
# make_regression_fixture.py (which refuses to run on a dirty engine.py).

FIXTURE = Path(__file__).parent / "fixtures" / "engine_regression_v1.json"

REL = 1e-6
ABS = 1e-8


def _load_cases():
    assert FIXTURE.exists(), (
        "regression fixture missing -- run make_regression_fixture.py "
        "against the committed v1.0.0 engine")
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data["cases"]


def _compare(expected, actual, path=""):
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: type changed"
        assert set(expected) == set(actual), (
            f"{path}: keys changed: -{set(expected) - set(actual)} "
            f"+{set(actual) - set(expected)}")
        for k in expected:
            _compare(expected[k], actual[k], f"{path}.{k}")
    elif isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: type changed"
        assert len(expected) == len(actual), f"{path}: length changed"
        for i, (e, a) in enumerate(zip(expected, actual)):
            _compare(e, a, f"{path}[{i}]")
    elif isinstance(expected, bool) or expected is None or isinstance(
            expected, str):
        assert actual == expected, (
            f"{path}: {actual!r} != {expected!r}")
    else:  # number
        assert actual == pytest.approx(expected, rel=REL, abs=ABS), (
            f"{path}: {actual!r} != {expected!r}")


@pytest.mark.parametrize("case", _load_cases(),
                         ids=lambda c: c["case_id"])
def test_regression_lock(engine, case):
    kwargs = dict(case["kwargs"])
    iso3 = kwargs.pop("iso3")
    # JSON round-trip of kwargs: sector keys/floats survive exactly
    result = engine.run_scenario(iso3, **kwargs)
    _compare(case["result"], result, case["case_id"])
