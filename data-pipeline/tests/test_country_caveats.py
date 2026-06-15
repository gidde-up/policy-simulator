"""Workstream F.3: country data caveats assembled from the verified JSON.

The helper is FastAPI-free (backend/app/api/country_caveats.py), loaded by
file path like lever_params. Checks that every built country yields the
required caveat fields and that data-derived warnings are present where the
data warrants them.
"""
import importlib.util
import json

import pytest

import config
from tests.conftest import BUILT_COUNTRIES

REQUIRED = {
    "io_data", "io_data_year", "employment_data", "compensation_data",
    "informality_indicator", "informality_year", "working_poverty_year",
    "employment_validation_gap_pct", "financing_mpc_status",
    "type_ii_propensity_capped", "notes", "warnings",
}


def _load_helper():
    path = config.REPO_ROOT / "backend" / "app" / "api" / "country_caveats.py"
    spec = importlib.util.spec_from_file_location("country_caveats", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.country_caveats


def _country_json(iso3):
    path = (config.REPO_ROOT / "backend" / "app" / "data" / "countries"
            / f"{iso3}.json")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def test_caveats_has_required_fields(iso3):
    cav = _load_helper()(iso3, _country_json(iso3))
    assert REQUIRED <= set(cav), f"{iso3}: missing {REQUIRED - set(cav)}"
    assert isinstance(cav["warnings"], list)
    assert isinstance(cav["notes"], list)
    assert cav["io_data_year"]  # IO data year present


def test_validation_gap_is_computed(iso3):
    cav = _load_helper()(iso3, _country_json(iso3))
    gap = cav["employment_validation_gap_pct"]
    assert gap is not None
    # the national-accounts vs LFS gap is real and non-trivial for these
    # economies; a large gap must raise a warning
    if abs(gap) >= 10.0:
        assert cav["warnings"], f"{iso3}: gap {gap:.0f}% but no warning"


def test_partial_data_does_not_crash():
    """A country object missing optional blocks still yields caveats (the
    panel must render even when some fields are absent)."""
    cav = _load_helper()("XXX", {"metadata": {}, "employment": [1.0, 2.0]})
    assert set(cav) >= REQUIRED
    assert cav["employment_validation_gap_pct"] is None
    assert cav["informality_indicator"] is None


def test_mpc_status_is_labelled():
    cav = _load_helper()("ZAF", _country_json("ZAF"))
    assert "literature_based" in cav["financing_mpc_status"]
