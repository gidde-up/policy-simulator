"""Session F verifier deliverable: one run per new lever per country,
central parameters, channels decomposed. Output:
reports/engine_lever_battery.json (independently reproducible)."""
import importlib.util
import json

import config

LEVERS = {
    "public_investment_1pct_broad":
        dict(extensions={"public_investment": {"amount_pct_gdp": 0.01}}),
    "stimulus_2pct_government":
        dict(sme_stimulus=0.02, extensions={"stimulus_target": "government"}),
    "production_subsidy_mfg_10":
        dict(extensions={"production_subsidy": {"manufacturing": 0.10}}),
    "wage_subsidy_mfg_10":
        dict(extensions={"wage_subsidy": {"manufacturing": 0.10}}),
    "tax_incentive_1pct_s30":
        dict(extensions={"investment_tax_incentive":
                         {"fiscal_cost_pct_gdp": 0.01, "intensity": 0.30}}),
    "public_works_1pct_labour_based":
        dict(extensions={"public_works":
                         {"budget_pct_gdp": 0.01, "method": "labour_based"}}),
    "public_works_1pct_conventional":
        dict(extensions={"public_works":
                         {"budget_pct_gdp": 0.01, "method": "conventional"}}),
    "direct_public_employment_1pct":
        dict(extensions={"direct_public_employment": {"budget_pct_gdp": 0.01}}),
    "depreciation_10pct":
        dict(extensions={"depreciation": 0.10}),
}


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "engine", config.REPO_ROOT / "backend" / "app" / "models" / "engine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    engine = load_engine()
    out = {"description": "Session F lever battery: one run per new lever "
                          "per country, central parameters (rates as "
                          "fractions, USD million / persons)",
           "countries": config.COUNTRIES, "runs": {}}
    for iso3 in config.COUNTRIES:
        out["runs"][iso3] = {}
        for name, kw in LEVERS.items():
            r = engine.run_scenario(iso3, **kw)
            out["runs"][iso3][name] = {
                "net_jobs": round(r["aggregate"]["total_jobs"], 1),
                "pct_of_baseline": round(
                    r["aggregate"]["share_of_baseline_employment"] * 100, 4),
                "channels": {k: round(v["jobs"], 1)
                             for k, v in (r["other_channels"] or {}).items()},
                "spending_usd_million": round(
                    r["costs"]["spending_cost_usd_million"], 1),
                "investment_incentive": r.get("investment_incentive"),
                "job_years": bool(r.get("job_years_note")),
            }
    path = config.REPORTS_DIR / "engine_lever_battery.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"written: {path}")


if __name__ == "__main__":
    main()
