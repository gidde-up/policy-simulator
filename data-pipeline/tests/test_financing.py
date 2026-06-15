"""Financing-mode acceptance tests (Workstream C / v1.2).

deficit | tax_financed | full_crowding_out, applied symmetrically to
every positive-cost fiscal lever. Engine-level (the API mode-propagation
check lives in the backend contract smoke, which has FastAPI)."""
import importlib.util
import json

import numpy as np
import pytest

import config
from tests.conftest import BUILT_COUNTRIES

SPENDING_LEVERS = {
    "public_investment":
        lambda gdp: dict(extensions={"public_investment": {"amount_pct_gdp": 0.01}}),
    "public_works":
        lambda gdp: dict(extensions={"public_works": {"budget_pct_gdp": 0.01,
                                                      "method": "labour_based"}}),
    "direct_public_employment":
        lambda gdp: dict(extensions={"direct_public_employment": {"budget_pct_gdp": 0.01}}),
    "production_subsidy":
        lambda gdp: dict(extensions={"production_subsidy": {"manufacturing": 1.0}}),
    "wage_subsidy":
        lambda gdp: dict(extensions={"wage_subsidy": {"manufacturing": 1.0}}),
    "investment_tax_incentive":
        lambda gdp: dict(extensions={"investment_tax_incentive":
                                     {"fiscal_cost_pct_gdp": 0.01, "intensity": 0.30}}),
    "stimulus": lambda gdp: dict(sme_stimulus=0.01),
}


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


@pytest.fixture(scope="module")
def baseline():
    path = config.REPORTS_DIR / "baseline_before_financing_methodology_fix.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _run(engine, iso3, lever, mode):
    return engine.run_scenario(iso3, financing_mode=mode,
                               **SPENDING_LEVERS[lever](None))


def test_deficit_no_withdrawal(engine, iso3):
    for lever in SPENDING_LEVERS:
        f = _run(engine, iso3, lever, "deficit")["financing"]
        assert f["financing_withdrawal_usd_million"] == 0.0, (iso3, lever)
        assert f["financing_offset_jobs"] == 0.0, (iso3, lever)


def test_tax_financed_withdrawal_is_mpc_scaled(engine, iso3):
    for lever in SPENDING_LEVERS:
        f = _run(engine, iso3, lever, "tax_financed")["financing"]
        assert f["financing_withdrawal_usd_million"] == pytest.approx(
            f["fiscal_cost_usd_million"] * f["financing_mpc"], rel=1e-9)


def test_linearity_tax_equals_full_times_mpc(engine, iso3):
    for lever in SPENDING_LEVERS:
        tax = _run(engine, iso3, lever, "tax_financed")
        full = _run(engine, iso3, lever, "full_crowding_out")
        mpc = tax["financing"]["financing_mpc"]
        assert tax["financing"]["financing_offset_jobs"] == pytest.approx(
            full["financing"]["financing_offset_jobs"] * mpc, rel=1e-9), lever


def test_full_crowding_out_matches_baseline(engine, iso3, baseline):
    """full_crowding_out reproduces the v1.1.0 spending-lever numbers
    (the old 100% drag), except the stimulus, which is reformulated."""
    name_map = {
        "public_investment": "public_investment_1pct",
        "public_works": "public_works_1pct",
        "direct_public_employment": "direct_public_employment_1pct",
        "production_subsidy": "production_subsidy_1pct_mfg",
        "wage_subsidy": "wage_subsidy_1pct_mfg",
        "investment_tax_incentive": "investment_tax_incentive_1pct",
    }
    for lever, bkey in name_map.items():
        new = _run(engine, iso3, lever, "full_crowding_out")
        old_net = baseline["lever_scenarios"][bkey][iso3]["net_jobs"]
        assert new["aggregate"]["total_jobs"] == pytest.approx(
            old_net, rel=1e-6, abs=1e-3), (iso3, lever)


def test_symmetry_equal_cost_identical_withdrawal(engine, iso3):
    """Two different levers with the same fiscal cost under the same mode
    produce the same financing-withdrawal vector (financing depends only
    on cost and mode, not the lever)."""
    cd = engine.load_country(iso3)
    amount = 0.01 * cd.gdp
    # public investment of `amount`
    r1 = engine.run_scenario(
        iso3, financing_mode="tax_financed",
        extensions={"public_investment": {"amount_pct_gdp": 0.01}})
    # sector support tuned to the same fiscal cost
    k = cd.sectors.index("construction")
    rate = amount / cd.x[k]
    r2 = engine.run_scenario(iso3, financing_mode="tax_financed",
                             sector_support={"construction": rate})
    assert (r1["financing"]["fiscal_cost_usd_million"]
            == pytest.approx(r2["financing"]["fiscal_cost_usd_million"], rel=1e-9))
    assert (r1["financing"]["financing_offset_jobs"]
            == pytest.approx(r2["financing"]["financing_offset_jobs"], rel=1e-9))


def test_stimulus_symmetry_with_government_purchase(engine, iso3):
    """A household transfer and a government-consumption purchase of equal
    size, same mode, use the same withdrawal logic (offset per fiscal
    unit identical)."""
    transfer = engine.run_scenario(iso3, sme_stimulus=0.01,
                                   financing_mode="tax_financed")
    govt = engine.run_scenario(iso3, sme_stimulus=0.01,
                               extensions={"stimulus_target": "government"},
                               financing_mode="tax_financed")
    def per_unit(r):
        f = r["financing"]
        return f["financing_offset_jobs"] / f["fiscal_cost_usd_million"]
    assert per_unit(transfer) == pytest.approx(per_unit(govt), rel=1e-9)


def test_ordering_deficit_gt_tax_gt_full(engine, iso3):
    """Financing strictly reduces net jobs: deficit > tax_financed >
    full_crowding_out for positive-cost fiscal levers."""
    for lever in SPENDING_LEVERS:
        d = _run(engine, iso3, lever, "deficit")["aggregate"]["total_jobs"]
        t = _run(engine, iso3, lever, "tax_financed")["aggregate"]["total_jobs"]
        f = _run(engine, iso3, lever, "full_crowding_out")["aggregate"]["total_jobs"]
        assert d > t > f, (iso3, lever, d, t, f)


def test_haavelmo_government_consumption(engine, iso3):
    """A tax-financed government-consumption injection is bounded and
    sits between the deficit and full-crowding-out results (the
    balanced-budget result is positive but modest, not forced)."""
    kw = dict(sme_stimulus=0.01,
              extensions={"stimulus_target": "government"})
    d = engine.run_scenario(iso3, financing_mode="deficit", **kw)["aggregate"]["total_jobs"]
    t = engine.run_scenario(iso3, financing_mode="tax_financed", **kw)["aggregate"]["total_jobs"]
    f = engine.run_scenario(iso3, financing_mode="full_crowding_out", **kw)["aggregate"]["total_jobs"]
    assert f < t < d
    # modest, not a large forced positive: |tax-financed| well below gross
    assert abs(t) < abs(d)


def test_deprecated_boolean_alias(engine, iso3):
    full = engine.run_scenario(iso3, sme_stimulus=0.01,
                               financing_mode="full_crowding_out")
    alias_true = engine.run_scenario(iso3, sme_stimulus=0.01,
                                     include_financing_drag=True)
    assert alias_true["financing"]["mode"] == "full_crowding_out"
    assert alias_true["financing"]["deprecated_input_used"] is True
    assert alias_true["aggregate"]["total_jobs"] == pytest.approx(
        full["aggregate"]["total_jobs"], rel=1e-12)


def _load_lever_params():
    path = config.REPO_ROOT / "backend" / "app" / "api" / "lever_params.py"
    spec = importlib.util.spec_from_file_location("lever_params", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_route_helper_passes_financing_mode():
    """The shared percent->fraction helper (used by the API and the
    preset tests) carries financing_mode through; default tax_financed."""
    lp = _load_lever_params()
    kw = lp.to_engine_kwargs({"public_investment": {"amount_pct_gdp": 1.0}})
    assert kw["financing_mode"] == "tax_financed"
    assert kw["extensions"]["public_investment"]["amount_pct_gdp"] == 0.01
    kw2 = lp.to_engine_kwargs({"financing_mode": "deficit",
                               "sme_stimulus": 2})
    assert kw2["financing_mode"] == "deficit"
    assert kw2["sme_stimulus"] == 0.02
