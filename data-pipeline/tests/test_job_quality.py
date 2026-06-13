"""Session G job-quality module: wage-bill identity, bounded
compensation ratio, informality composition and the per-country gate."""
import numpy as np
import pytest

from tests.conftest import BUILT_COUNTRIES


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def _scenario(engine, iso3):
    return engine.run_scenario(
        iso3, sector_support={"agriculture": 0.05},
        sme_stimulus=0.01)


def test_wage_bill_identity(engine, iso3):
    """wage-bill change = labour-income coefficients . output change
    = v' L dF (the value-added/compensation identity)."""
    r = _scenario(engine, iso3)
    cd = engine.load_country(iso3)
    q = engine.job_quality(iso3, r)
    dx = np.array([se["output_change_usd_million"]
                   for se in r["sector_effects"]])
    expected = float(cd.labour_income_coefficients @ dx)
    assert q["wage"]["wage_bill_change_usd_million"] == pytest.approx(
        expected, rel=1e-9)


def test_compensation_ratio_bounded(engine, iso3):
    """The weighted average compensation per worker of the change must
    lie within the sector min/max comp per worker."""
    r = _scenario(engine, iso3)
    cd = engine.load_country(iso3)
    comp = cd.labour_income_coefficients * cd.x
    cpw = np.where(cd.employment > 0, comp / cd.employment, 0.0)
    economy = float(comp.sum() / cd.employment.sum())
    ratio = engine.job_quality(iso3, r)["wage"][
        "avg_compensation_ratio_vs_economy"]
    lo, hi = cpw.min() / economy, cpw.max() / economy
    assert lo - 1e-9 <= ratio <= hi + 1e-9


def test_informality_share_bounded(engine, iso3):
    r = _scenario(engine, iso3)
    q = engine.job_quality(iso3, r)
    inf = q["informality"]
    # all five built countries have an informality block
    assert inf is not None, f"{iso3}: expected informality data"
    assert 0.0 <= inf["informal_share_of_change"] <= 1.0
    assert inf["year"]


def test_informality_gate_hidden_without_data(engine):
    """A country whose data carries no informality block reports no
    informality composition (gate hidden, never imputed)."""
    cd = engine.load_country("ZAF")
    # build a copy without the informality block
    import copy
    cd2 = copy.copy(cd)
    cd2.informal_share = None
    cd2.informality_meta = None
    # monkeypatch the cache so job_quality sees the stripped country
    engine._COUNTRY_CACHE["_TESTNOINF"] = cd2
    cd2.iso3 = "_TESTNOINF"
    r = engine.run_scenario("ZAF", sme_stimulus=0.01)
    q = engine.job_quality("_TESTNOINF", r)
    assert q["informality"] is None
    del engine._COUNTRY_CACHE["_TESTNOINF"]


def test_zero_scenario_no_quality_crash(engine, iso3):
    """An empty scenario must not divide by zero."""
    r = engine.run_scenario(iso3)
    q = engine.job_quality(iso3, r)
    assert q["wage"]["avg_compensation_ratio_vs_economy"] is None
