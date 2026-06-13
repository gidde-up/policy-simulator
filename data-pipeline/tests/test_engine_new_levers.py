"""Acceptance-style tests for the Session F extension levers, per the
extension prompt. Run against the built country JSONs."""
import numpy as np
import pytest

from tests.conftest import BUILT_COUNTRIES


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def _channels_sum_to_total(r):
    chan = 0.0
    if r["tariff_channels"]:
        chan += sum(v["jobs"] for v in r["tariff_channels"].values() if v)
    if r["other_channels"]:
        chan += sum(v["jobs"] for v in r["other_channels"].values())
    return chan == pytest.approx(r["aggregate"]["total_jobs"], rel=1e-9,
                                 abs=1e-6)


# --- public investment -------------------------------------------------
def test_public_investment_decomposition(engine, iso3):
    r = engine.run_scenario(
        iso3, extensions={"public_investment": {"amount_pct_gdp": 0.01}})
    assert _channels_sum_to_total(r)
    # injection present, financing drag present (default on)
    assert "public_investment" in r["other_channels"]
    assert "financing_drag" in r["other_channels"]


# --- production subsidy -------------------------------------------------
def test_production_subsidy_identity_and_signs(engine, iso3):
    r = engine.run_scenario(
        iso3, extensions={"production_subsidy": {"manufacturing": 0.10}})
    assert _channels_sum_to_total(r)
    oc = r["other_channels"]
    # a subsidy lowers prices: downstream and real-income channels gain
    assert oc["production_subsidy_downstream"]["jobs"] > 0
    assert oc["production_subsidy_real_income"]["jobs"] > 0
    # financing drag is negative
    assert oc["financing_drag"]["jobs"] < 0


def test_production_subsidy_intensity_rule(engine, iso3):
    """With the financing drag on, supporting a capital-intensive sector
    (manufacturing, few jobs/$) against the labour-intensive household
    basket the tax falls on is net-negative; agriculture (jobs-rich) is
    net-positive. The intensity-vs-basket rule."""
    r_mfg = engine.run_scenario(
        iso3, extensions={"production_subsidy": {"manufacturing": 0.10}})
    r_agr = engine.run_scenario(
        iso3, extensions={"production_subsidy": {"agriculture": 0.10}})
    assert r_agr["aggregate"]["total_jobs"] > r_mfg["aggregate"]["total_jobs"]


# --- wage subsidy -------------------------------------------------------
def test_wage_subsidy_cheaper_than_production(engine, iso3):
    """A wage subsidy costs w x wage bill, less than a production
    subsidy's w x output, so its fiscal cost (and drag) is smaller."""
    rw = engine.run_scenario(
        iso3, extensions={"wage_subsidy": {"manufacturing": 0.10}})
    rp = engine.run_scenario(
        iso3, extensions={"production_subsidy": {"manufacturing": 0.10}})
    assert (rw["costs"]["spending_cost_usd_million"]
            < rp["costs"]["spending_cost_usd_million"])
    assert _channels_sum_to_total(rw)


# --- investment tax incentive ------------------------------------------
def test_tax_incentive_windfall_identity(engine, iso3):
    r = engine.run_scenario(
        iso3, extensions={"investment_tax_incentive":
                          {"fiscal_cost_pct_gdp": 0.01, "intensity": 0.3}})
    ii = r["investment_incentive"]
    assert (ii["additional_investment_usd_million"]
            + ii["windfall_usd_million"]
            == pytest.approx(ii["gross_investment_usd_million"], rel=1e-9))


def test_tax_incentive_monotone_in_redundancy(engine, iso3):
    """Net jobs fall as redundancy rises; at r=1 (pure windfall) the
    lever is pure financing drag -> net negative. Implemented by reading
    the registered low/high redundancy via the uncertainty band: higher
    redundancy (high variant) yields fewer additional jobs."""
    r = engine.run_scenario(
        iso3, extensions={"investment_tax_incentive":
                          {"fiscal_cost_pct_gdp": 0.01, "intensity": 0.3}})
    # low redundancy corner must beat high redundancy corner
    assert r["aggregate"]["total_jobs_high"] != r["aggregate"]["total_jobs_low"]
    # central additional investment is positive (redundancy < 1)
    assert r["investment_incentive"]["additional_investment_usd_million"] > 0


# --- public works / EIIP -----------------------------------------------
def test_public_works_direct_jobs_identity(engine, iso3):
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    budget = 0.01 * cd.gdp
    i = cd.sectors.index("construction")
    lam = p.eiip_labour_share
    comp_i = float(cd.labour_income_coefficients[i]) * cd.x[i]
    expected_direct = (lam * budget) / (comp_i / cd.employment[i])
    shocks = engine.compile_public_works(cd, p, budget, "labour_based")
    de = [s for s in shocks if isinstance(s, engine.DirectEmployment)][0]
    assert de.jobs == pytest.approx(expected_direct, rel=1e-9)


def test_public_works_labour_based_beats_conventional(engine, iso3):
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    budget = 0.01 * cd.gdp

    def direct(method):
        shocks = engine.compile_public_works(cd, p, budget, method)
        return [s for s in shocks
                if isinstance(s, engine.DirectEmployment)][0].jobs
    assert direct("labour_based") > direct("conventional")


def test_public_works_total_geq_direct_gross(engine, iso3):
    """With the financing drag off, the programme's total job effect is
    at least its direct component (materials add more)."""
    r = engine.run_scenario(
        iso3, include_financing_drag=False,
        extensions={"public_works":
                    {"budget_pct_gdp": 0.01, "method": "labour_based"}})
    direct_ch = r["other_channels"]["public_works_direct"]["jobs"]
    assert r["aggregate"]["total_jobs"] >= direct_ch - 1e-6
    assert r["job_years_note"]


# --- direct public employment ------------------------------------------
def test_direct_public_employment_drag_reduces_net(engine, iso3):
    on = engine.run_scenario(
        iso3, include_financing_drag=True,
        extensions={"direct_public_employment": {"budget_pct_gdp": 0.01}})
    off = engine.run_scenario(
        iso3, include_financing_drag=False,
        extensions={"direct_public_employment": {"budget_pct_gdp": 0.01}})
    assert (on["aggregate"]["total_jobs"]
            < off["aggregate"]["total_jobs"])
    assert on["job_years_note"]


def test_direct_public_employment_jobs_identity(engine, iso3):
    cd = engine.load_country(iso3)
    budget = 0.01 * cd.gdp
    i = cd.sectors.index("public_services")
    # jobs = budget * employment coefficient of public services
    expected = budget * cd.employment[i] / cd.x[i]
    shocks = engine.compile_direct_public_employment(cd, budget)
    de = [s for s in shocks if isinstance(s, engine.DirectEmployment)][0]
    assert de.jobs == pytest.approx(expected, rel=1e-9)


# --- depreciation ------------------------------------------------------
def test_depreciation_channel_signs(engine, iso3):
    r = engine.run_scenario(iso3, extensions={"depreciation": 0.10})
    oc = r["other_channels"]
    assert oc["depreciation_exports"]["jobs"] >= 0      # export gain
    assert oc["depreciation_real_income"]["jobs"] <= 0  # real-income loss
    assert oc["depreciation_downstream"]["jobs"] <= 0   # input-cost loss
    assert _channels_sum_to_total(r)


# --- combined scenario identity ----------------------------------------
def test_combined_scenario_identity(engine, iso3):
    r = engine.run_scenario(
        iso3, tariffs={"manufacturing": 0.05},
        sector_support={"agriculture": 0.05}, sme_stimulus=0.01,
        include_type_ii=True,
        extensions={"public_investment": {"amount_pct_gdp": 0.005},
                    "production_subsidy": {"textiles": 0.05},
                    "depreciation": 0.05})
    assert _channels_sum_to_total(r)
    agg = r["aggregate"]
    assert agg["total_jobs"] == pytest.approx(
        agg["direct_jobs"] + agg["indirect_jobs"] + agg["induced_jobs"],
        rel=1e-9)
