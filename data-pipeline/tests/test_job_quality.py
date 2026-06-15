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
    # gained/lost present and both "not applicable" (no movement)
    assert q["gained"]["total_jobs"] == 0
    assert q["lost"]["total_jobs"] == 0
    assert q["gained"]["avg_compensation_ratio_vs_economy"] is None
    assert q["lost"]["avg_compensation_ratio_vs_economy"] is None


# --------------------------------------------------------------------
# Workstream G: gained vs lost split
# --------------------------------------------------------------------
def _cpw(cd):
    """sector compensation per worker and the economy mean."""
    import numpy as np
    comp = cd.labour_income_coefficients * cd.x
    cpw = np.where(cd.employment > 0, comp / cd.employment, 0.0)
    return cpw, float(comp.sum() / cd.employment.sum())


def _result_from(cd, dE):
    return {"sector_effects": [
        {"total_jobs": float(dE[k]), "output_change_usd_million": 0.0}
        for k in range(len(cd.sectors))]}


def test_gained_lost_weighting(engine, iso3):
    """One high-wage sector gaining and one low-wage sector losing:
    the gained and lost weighted averages use their own baskets."""
    import numpy as np
    cd = engine.load_country(iso3)
    cpw, economy = _cpw(cd)
    valid = np.where(cd.employment > 0)[0]
    kg = valid[int(np.argmax(cpw[valid]))]   # highest comp per worker
    kl = valid[int(np.argmin(cpw[valid]))]   # lowest comp per worker
    assert kg != kl
    dE = np.zeros(len(cd.sectors))
    dE[kg] = 1000.0
    dE[kl] = -500.0
    q = engine.job_quality(iso3, _result_from(cd, dE))
    assert q["gained"]["total_jobs"] == pytest.approx(1000.0)
    assert q["lost"]["total_jobs"] == pytest.approx(500.0)
    # single sector in each basket -> ratio equals that sector's ratio
    assert q["gained"]["avg_compensation_ratio_vs_economy"] == pytest.approx(
        cpw[kg] / economy, rel=1e-9)
    assert q["lost"]["avg_compensation_ratio_vs_economy"] == pytest.approx(
        cpw[kl] / economy, rel=1e-9)
    # the gaining basket pays more than the losing basket here
    assert (q["gained"]["avg_compensation_ratio_vs_economy"]
            > q["lost"]["avg_compensation_ratio_vs_economy"])


def test_no_losses_not_applicable(engine, iso3):
    """A gains-only change reports the lost profile as not applicable and
    does not crash or divide by zero."""
    import numpy as np
    cd = engine.load_country(iso3)
    dE = np.zeros(len(cd.sectors))
    dE[int(np.where(cd.employment > 0)[0][0])] = 250.0
    q = engine.job_quality(iso3, _result_from(cd, dE))
    assert q["gained"]["total_jobs"] == pytest.approx(250.0)
    assert q["lost"]["total_jobs"] == 0
    assert q["lost"]["avg_compensation_usd_million"] is None
    assert q["lost"]["avg_compensation_ratio_vs_economy"] is None
    assert q["lost"]["informal_share"] is None
    assert "not applicable" in q["lost"]["informality_note"].lower()


def test_missing_informality_excluded_not_zero(engine):
    """If a gaining sector has no informality datum, it is excluded from
    the weighted informality (never treated as zero) and the coverage
    fraction reflects the omission."""
    import copy
    import numpy as np
    cd = engine.load_country("ZAF")
    if cd.informal_share is None:
        pytest.skip("no informality data")
    cd2 = copy.copy(cd)
    share = cd.informal_share.copy()
    valid = np.where(cd.employment > 0)[0]
    a, b = int(valid[0]), int(valid[1])
    known = 0.40
    share[a] = known     # sector a: known informality
    share[b] = np.nan    # sector b: missing
    cd2.informal_share = share
    cd2.iso3 = "_TESTNAN"
    engine._COUNTRY_CACHE["_TESTNAN"] = cd2
    try:
        dE = np.zeros(len(cd.sectors))
        dE[a] = 100.0
        dE[b] = 100.0     # equal weight on a (known) and b (missing)
        q = engine.job_quality("_TESTNAN", _result_from(cd2, dE))
        g = q["gained"]
        # informal share is the KNOWN sector's value, not (0.40+0)/2 = 0.20
        assert g["informal_share"] == pytest.approx(known, rel=1e-9)
        assert g["informality_coverage"] == pytest.approx(0.5, rel=1e-9)
    finally:
        del engine._COUNTRY_CACHE["_TESTNAN"]
