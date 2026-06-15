"""Workstream C deliverable: the financing battery and the preset
old-vs-new comparison.

Runs the v1.2 engine (financing modes deficit | tax_financed |
full_crowding_out) over every spending lever and every country, and
re-runs all 24 presets to compare net signs against the v1.1.0 baseline
snapshot (reports/baseline_before_financing_methodology_fix.json).

Output:
  reports/financing_battery.json   - levers x modes x countries, decomposed
and prints:
  - public investment 1% of GDP, three modes, per country
  - stimulus 1% of GDP, three modes, per country (no longer costless)
  - 24-preset old-vs-new sign table (flagging changed signs)
"""
import importlib.util
import json

import config

MODES = ("deficit", "tax_financed", "full_crowding_out")
LEVER_PCT = 0.01
SPENDING_LEVERS = {
    "public_investment":
        dict(extensions={"public_investment": {"amount_pct_gdp": LEVER_PCT}}),
    "public_works":
        dict(extensions={"public_works": {"budget_pct_gdp": LEVER_PCT,
                                          "method": "labour_based"}}),
    "direct_public_employment":
        dict(extensions={"direct_public_employment": {"budget_pct_gdp": LEVER_PCT}}),
    "production_subsidy":
        dict(extensions={"production_subsidy": {"manufacturing": 1.0}}),
    "wage_subsidy":
        dict(extensions={"wage_subsidy": {"manufacturing": 1.0}}),
    "investment_tax_incentive":
        dict(extensions={"investment_tax_incentive":
                         {"fiscal_cost_pct_gdp": LEVER_PCT, "intensity": 0.30}}),
    "stimulus_household": dict(sme_stimulus=LEVER_PCT),
    "stimulus_government":
        dict(sme_stimulus=LEVER_PCT,
             extensions={"stimulus_target": "government"}),
}


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_engine():
    return _load(config.REPO_ROOT / "backend" / "app" / "models" / "engine.py",
                 "engine")


def capture(engine, iso3, mode, **kw):
    r = engine.run_scenario(iso3, financing_mode=mode, **kw)
    a = r["aggregate"]
    f = r["financing"]
    channels = {k: round(v["jobs"], 2)
                for k, v in (r.get("other_channels") or {}).items()}
    return {
        "country": iso3,
        "mode": mode,
        "net_jobs": round(a["total_jobs"], 2),
        "gross_jobs_before_financing": round(a["gross_jobs_before_financing"], 2),
        "financing_offset_jobs": round(a["financing_offset_jobs"], 2),
        "fiscal_cost_usd_million": round(f["fiscal_cost_usd_million"], 2),
        "financing_withdrawal_usd_million":
            round(f["financing_withdrawal_usd_million"], 2),
        "financing_mpc": f["financing_mpc"],
        "channels": channels,
    }


def sign(x, baseline_emp):
    if abs(x) < 0.001 * baseline_emp:
        return "near_zero"
    return "positive" if x > 0 else "negative"


def main():
    engine = load_engine()
    lp = _load(config.REPO_ROOT / "backend" / "app" / "api" / "lever_params.py",
               "lever_params")
    presets = _load(config.REPO_ROOT / "backend" / "app" / "api"
                    / "presets_data.py", "presets_data").PRESETS

    # --- financing battery ------------------------------------------
    battery = {}
    for lever, kw in SPENDING_LEVERS.items():
        battery[lever] = {iso3: {mode: capture(engine, iso3, mode, **kw)
                                 for mode in MODES}
                          for iso3 in config.COUNTRIES}
    path = config.REPORTS_DIR / "financing_battery.json"
    path.write_text(json.dumps(battery, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"written: {path}\n")

    def table(lever):
        print(f"=== {lever}, 1% of GDP, net jobs by mode ===")
        print(f"{'country':>8} {'deficit':>12} {'tax_fin':>12} "
              f"{'full_CO':>12} {'mpc':>5}")
        for iso3 in config.COUNTRIES:
            row = battery[lever][iso3]
            print(f"{iso3:>8} {row['deficit']['net_jobs']:>12,.0f} "
                  f"{row['tax_financed']['net_jobs']:>12,.0f} "
                  f"{row['full_crowding_out']['net_jobs']:>12,.0f} "
                  f"{row['tax_financed']['financing_mpc']:>5}")
        print()

    table("public_investment")
    table("stimulus_household")
    table("stimulus_government")

    # --- preset old-vs-new ------------------------------------------
    base = json.loads((config.REPORTS_DIR
                       / "baseline_before_financing_methodology_fix.json"
                       ).read_text(encoding="utf-8"))["presets"]
    print("=== 24-preset old-vs-new (default mode = tax_financed) ===")
    print(f"{'id':<28} {'old_net':>10} {'new_net':>10} {'old':>9} "
          f"{'new':>9} {'expects':>9} flag")
    changed = []
    for p in presets:
        r = engine.run_scenario(p["country_code"], **lp.to_engine_kwargs(p["params"]))
        new_net = r["aggregate"]["total_jobs"]
        emp = r["baseline"]["sector_sum_employment_persons"]
        old_net = base[p["id"]]["net_jobs"]
        old_sign = sign(old_net, emp)
        new_sign = sign(new_net, emp)
        exp = p["expected"]["net_sign"]
        flag = ""
        if old_sign != new_sign:
            flag += "SIGN-CHANGED "
        if new_sign != exp:
            flag += "EXPECT-MISMATCH"
            changed.append((p["id"], exp, new_sign, old_net, new_net))
        print(f"{p['id']:<28} {old_net:>10,.0f} {new_net:>10,.0f} "
              f"{old_sign:>9} {new_sign:>9} {exp:>9} {flag}")
    print(f"\npresets whose CURRENT sign no longer matches expected: {len(changed)}")
    for cid, exp, new_sign, old_net, new_net in changed:
        print(f"  {cid}: expects {exp}, now {new_sign} "
              f"(old {old_net:,.0f} -> new {new_net:,.0f})")


if __name__ == "__main__":
    main()
