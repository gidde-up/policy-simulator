"""Workstream A baseline: snapshot the v1.1.0 engine outputs BEFORE the
financing-drag correction and the Senegal-elasticity correction, so the
changes can be compared. Output:
reports/baseline_before_financing_methodology_fix.json

Run this against the committed v1.1.0 engine behaviour (drag = full
withdrawal, SEN elasticity = the v1.1.0 value) before editing the drag.
"""
import importlib.util
import json

import config

LEVER_PCT = 0.01   # 1% of GDP for the fiscal levers
SCENARIOS = {
    "public_investment_1pct":
        dict(extensions={"public_investment": {"amount_pct_gdp": LEVER_PCT}}),
    "public_works_1pct":
        dict(extensions={"public_works": {"budget_pct_gdp": LEVER_PCT,
                                          "method": "labour_based"}}),
    "direct_public_employment_1pct":
        dict(extensions={"direct_public_employment": {"budget_pct_gdp": LEVER_PCT}}),
    "production_subsidy_1pct_mfg":
        dict(extensions={"production_subsidy": {"manufacturing": 1.0}}),
    "wage_subsidy_1pct_mfg":
        dict(extensions={"wage_subsidy": {"manufacturing": 1.0}}),
    "investment_tax_incentive_1pct":
        dict(extensions={"investment_tax_incentive":
                         {"fiscal_cost_pct_gdp": LEVER_PCT, "intensity": 0.30}}),
    "stimulus_1pct_household": dict(sme_stimulus=LEVER_PCT),
    "depreciation_10pct": dict(extensions={"depreciation": 0.10}),
}


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "engine", config.REPO_ROOT / "backend" / "app" / "models" / "engine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_presets():
    path = config.REPO_ROOT / "backend" / "app" / "api" / "presets_data.py"
    spec = importlib.util.spec_from_file_location("presets_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRESETS


def capture(engine, iso3, **kw):
    r = engine.run_scenario(iso3, **kw)
    a = r["aggregate"]
    drag = (r.get("other_channels") or {}).get("financing_drag")
    return {
        "country": iso3,
        "net_jobs": a["total_jobs"],
        "direct_jobs": a["direct_jobs"],
        "indirect_jobs": a["indirect_jobs"],
        "induced_jobs": a["induced_jobs"],
        "financing_drag_jobs": (drag["jobs"] if drag else 0.0),
        "spending_cost_usd_million": r["costs"]["spending_cost_usd_million"],
        "tariff_revenue_usd_million": r["costs"]["tariff_revenue_usd_million"],
        "uncertainty": r["uncertainty"],
        "financing_mode": "full_crowding_out (v1.1.0 default; "
                          "include_financing_drag=True)",
    }


def main():
    engine = load_engine()
    out = {
        "description": "v1.1.0 baseline snapshot before the financing and "
                       "Senegal-elasticity corrections (Workstreams C, D)",
        "conversion_helper": "backend/app/api/lever_params.py:"
                             "to_engine_kwargs (percent->fraction)",
        "lever_scenarios": {}, "presets": {},
    }
    from tests.conftest import BUILT_COUNTRIES  # noqa
    for name, kw in SCENARIOS.items():
        out["lever_scenarios"][name] = {
            iso3: capture(engine, iso3, **kw) for iso3 in config.COUNTRIES}

    # Senegal 10% manufacturing tariff (D will change this)
    out["sen_manufacturing_tariff_10pct"] = capture(
        engine, "SEN", tariffs={"manufacturing": 0.10})

    # all presets
    spec_lp = importlib.util.spec_from_file_location(
        "lever_params",
        config.REPO_ROOT / "backend" / "app" / "api" / "lever_params.py")
    lp = importlib.util.module_from_spec(spec_lp)
    spec_lp.loader.exec_module(lp)
    for p in load_presets():
        out["presets"][p["id"]] = capture(
            engine, p["country_code"], **lp.to_engine_kwargs(p["params"]))

    path = config.REPORTS_DIR / "baseline_before_financing_methodology_fix.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"written: {path}")
    print(f"lever scenarios: {len(out['lever_scenarios'])}, "
          f"presets: {len(out['presets'])}")


if __name__ == "__main__":
    main()
