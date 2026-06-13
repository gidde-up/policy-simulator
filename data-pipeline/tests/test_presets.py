"""Every curated scenario must run on the engine and 'tell a true
story': the sign/structure claims its walkthrough makes are asserted
here against the actual engine output (Phase 3 requirement)."""
import importlib.util

import pytest

import config


@pytest.fixture(scope="module")
def presets():
    path = (config.REPO_ROOT / "backend" / "app" / "api"
            / "presets_data.py")
    spec = importlib.util.spec_from_file_location("presets_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRESETS


def _run(engine, preset):
    p = preset["params"]
    ext = _extensions_from_params(p)
    return engine.run_scenario(
        preset["country_code"],
        tariffs={s: v / 100 for s, v in p.get("tariff_changes", {}).items()},
        sector_support={s: v / 100
                        for s, v in p.get("sector_support", {}).items()},
        sme_stimulus=p.get("sme_stimulus", 0) / 100,
        extensions=ext or None,
    )


def _extensions_from_params(p: dict) -> dict:
    """Mirror of routes.py: build the engine `extensions` dict from a
    preset's API-shaped params (percent -> fraction)."""
    ext = {}
    if p.get("stimulus_target", "household") != "household":
        ext["stimulus_target"] = p["stimulus_target"]
    if p.get("public_investment"):
        pi = p["public_investment"]
        ext["public_investment"] = {
            "amount_pct_gdp": pi["amount_pct_gdp"] / 100,
            "target": pi.get("target")}
    if p.get("production_subsidy"):
        ext["production_subsidy"] = {s: v / 100
                                     for s, v in p["production_subsidy"].items()}
    if p.get("wage_subsidy"):
        ext["wage_subsidy"] = {s: v / 100
                               for s, v in p["wage_subsidy"].items()}
    if p.get("investment_tax_incentive"):
        iti = p["investment_tax_incentive"]
        ext["investment_tax_incentive"] = {
            "fiscal_cost_pct_gdp": iti["fiscal_cost_pct_gdp"] / 100,
            "intensity": iti["intensity"] / 100,
            "target": iti.get("target")}
    if p.get("public_works"):
        pw = p["public_works"]
        ext["public_works"] = {
            "budget_pct_gdp": pw["budget_pct_gdp"] / 100,
            "method": pw.get("method", "labour_based")}
    if p.get("direct_public_employment"):
        dpe = p["direct_public_employment"]
        ext["direct_public_employment"] = {
            "budget_pct_gdp": dpe["budget_pct_gdp"] / 100}
    if p.get("depreciation"):
        ext["depreciation"] = p["depreciation"] / 100
    return ext


def test_presets_structure(presets):
    assert len(presets) == 24
    ids = [p["id"] for p in presets]
    assert len(set(ids)) == len(presets)
    for p in presets:
        assert p["country_code"] in config.COUNTRIES
        assert p["walkthrough"], p["id"]
        assert p["expected"]["net_sign"] in ("positive", "negative",
                                             "near_zero")


def test_presets_tell_true_stories(engine, presets, capsys):
    for preset in presets:
        r = _run(engine, preset)
        net = r["aggregate"]["total_jobs"]
        baseline = r["baseline"]["sector_sum_employment_persons"]
        exp = preset["expected"]
        print(f"{preset['id']}: net {net:,.0f} ({net / baseline:+.3%})")
        if exp["net_sign"] == "positive":
            assert net > 0, f"{preset['id']}: claims positive, got {net:,.0f}"
        elif exp["net_sign"] == "negative":
            assert net < 0, f"{preset['id']}: claims negative, got {net:,.0f}"
        else:  # near_zero: the walkthrough says "approximately zero"
            assert abs(net) < 0.001 * baseline, (
                f"{preset['id']}: claims near-zero, got {net:,.0f} "
                f"({net / baseline:+.3%})")
        if exp.get("has_tariff_channels"):
            assert r["tariff_channels"] is not None, preset["id"]
        else:
            assert r["tariff_channels"] is None, preset["id"]
        if exp.get("gains_positive"):
            gain = r["tariff_channels"]["protected_sector_gain"]
            assert gain and gain["jobs"] > 0, preset["id"]
        if exp.get("has_windfall"):
            assert r.get("investment_incentive"), preset["id"]
            assert r["investment_incentive"]["windfall_usd_million"] > 0
        if exp.get("has_job_years"):
            assert r.get("job_years_note"), preset["id"]
