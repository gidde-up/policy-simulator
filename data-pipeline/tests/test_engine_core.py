"""Linearity, decomposition consistency and per-country lever smoke
tests against the built country JSONs."""
import numpy as np
import pytest

from tests.conftest import BUILT_COUNTRIES


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def test_linearity(engine, iso3):
    cd = engine.load_country(iso3)
    dF = np.zeros(len(cd.sectors))
    dF[2] = 100.0
    d1 = engine.decompose(cd, dF, include_type_ii=False)
    d2 = engine.decompose(cd, 2 * dF, include_type_ii=False)
    np.testing.assert_allclose(2 * d1["total"], d2["total"], rtol=1e-10)


def test_decomposition_sums(engine, iso3):
    r = engine.run_scenario(iso3, tariffs={"manufacturing": 0.10},
                            sector_support={"agriculture": 0.05},
                            sme_stimulus=0.01, include_type_ii=True)
    agg = r["aggregate"]
    assert agg["total_jobs"] == pytest.approx(
        agg["direct_jobs"] + agg["indirect_jobs"] + agg["induced_jobs"],
        rel=1e-9)
    sector_total = sum(s["total_jobs"] for s in r["sector_effects"])
    assert sector_total == pytest.approx(agg["total_jobs"], rel=1e-9)


def test_channels_sum_to_total(engine, iso3):
    r = engine.run_scenario(iso3, tariffs={"manufacturing": 0.10},
                            include_retaliation=True)
    ch = r["tariff_channels"]
    channel_sum = sum(v["jobs"] for v in ch.values() if v is not None)
    assert channel_sum == pytest.approx(r["aggregate"]["total_jobs"],
                                        rel=1e-9)


def test_every_lever_smoke(engine, iso3):
    cases = [
        {"tariffs": {"textiles": 0.10}},
        {"tariffs": {"manufacturing": 0.10}, "include_retaliation": True},
        {"sector_support": {"construction": 0.05}},
        {"sector_support": {"construction": 0.05},
         "include_financing_drag": False},
        {"sme_stimulus": 0.02},
        {"tariffs": {"chemicals": 0.05}, "include_type_ii": True},
    ]
    for kwargs in cases:
        r = engine.run_scenario(iso3, **kwargs)
        agg = r["aggregate"]
        assert np.isfinite(agg["total_jobs"]), kwargs
        assert agg["total_jobs_low"] <= agg["total_jobs_high"], kwargs
        assert r["data_source"]["citation"].startswith("OECD ICIO"), kwargs
        assert "research-grade" not in str(r["data_source"]), kwargs


def test_expected_signs(engine, iso3):
    # deficit-financed sector support creates jobs
    r_deficit = engine.run_scenario(iso3,
                                    sector_support={"manufacturing": 0.05},
                                    financing_mode="deficit")
    assert r_deficit["aggregate"]["total_jobs"] > 0
    # a deficit-financed demand stimulus creates jobs
    r = engine.run_scenario(iso3, sme_stimulus=0.01, financing_mode="deficit")
    assert r["aggregate"]["total_jobs"] > 0
    # financing the same support (tax-financed) yields fewer net jobs
    r_tax = engine.run_scenario(iso3,
                                sector_support={"manufacturing": 0.05},
                                financing_mode="tax_financed")
    assert r_tax["aggregate"]["total_jobs"] \
        < r_deficit["aggregate"]["total_jobs"]


def test_induced_labelled(engine, iso3):
    r = engine.run_scenario(iso3, sme_stimulus=0.01, include_type_ii=True)
    assert "upper-bound" in r["induced_note"]
    r2 = engine.run_scenario(iso3, sme_stimulus=0.01, include_type_ii=False)
    assert r2["induced_note"] is None
    assert r2["aggregate"]["induced_jobs"] is None


def test_baseline_is_sector_sum(engine, iso3, country_data):
    r = engine.run_scenario(iso3, sme_stimulus=0.01)
    persons = country_data[iso3]["employment"]["persons"]
    assert r["baseline"]["sector_sum_employment_persons"] == pytest.approx(
        sum(persons), rel=1e-9)


def test_multipliers_match_reports(engine, iso3, country_data):
    """engine.employment_multipliers must reproduce e' L from the JSON."""
    d = country_data[iso3]
    e = np.array(d["employment_coefficients"])
    m1 = e @ np.array(d["L_typeI"])
    mult = engine.employment_multipliers(iso3)
    for k, s in enumerate(d["sectors"]):
        assert mult[s]["type_1"] == pytest.approx(m1[k], rel=1e-9)
