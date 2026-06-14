"""Single source of truth for converting an API-shaped scenario params
dict (percent units) into engine.run_scenario keyword arguments
(fractions + the `extensions` dict).

Both the /api/simulate route and the preset test suite import this, so
the live app and the tests can never drift on the percent->fraction
boundary. Pure dict manipulation -- no FastAPI, no numpy -- so the
data-pipeline test venv can load it by file path.

This file (NOT engine.py) owns the unit conversion: the engine is kept
free of magnitude literals (an AST test enforces that).
"""

_PCT = 100.0


def to_engine_kwargs(p: dict) -> dict:
    """p: API-shaped params (percent). Returns run_scenario kwargs
    (excluding iso3 and the scenario name)."""
    ext = {}

    if p.get("stimulus_target", "household") != "household":
        ext["stimulus_target"] = p["stimulus_target"]

    pi = p.get("public_investment")
    if pi and pi.get("amount_pct_gdp", 0):
        ext["public_investment"] = {
            "amount_pct_gdp": pi["amount_pct_gdp"] / _PCT,
            "target": pi.get("target"),
        }

    ps = p.get("production_subsidy") or {}
    ps = {s: v / _PCT for s, v in ps.items() if v}
    if ps:
        ext["production_subsidy"] = ps

    ws = p.get("wage_subsidy") or {}
    ws = {s: v / _PCT for s, v in ws.items() if v}
    if ws:
        ext["wage_subsidy"] = ws

    iti = p.get("investment_tax_incentive")
    if iti and iti.get("fiscal_cost_pct_gdp", 0):
        ext["investment_tax_incentive"] = {
            "fiscal_cost_pct_gdp": iti["fiscal_cost_pct_gdp"] / _PCT,
            "intensity": iti["intensity"] / _PCT,
            "target": iti.get("target"),
        }

    pw = p.get("public_works")
    if pw and pw.get("budget_pct_gdp", 0):
        ext["public_works"] = {
            "budget_pct_gdp": pw["budget_pct_gdp"] / _PCT,
            "method": pw.get("method", "labour_based"),
        }

    dpe = p.get("direct_public_employment")
    if dpe and dpe.get("budget_pct_gdp", 0):
        ext["direct_public_employment"] = {
            "budget_pct_gdp": dpe["budget_pct_gdp"] / _PCT,
        }

    if p.get("depreciation"):
        ext["depreciation"] = p["depreciation"] / _PCT

    return {
        "tariffs": {s: v / _PCT
                    for s, v in (p.get("tariff_changes") or {}).items() if v},
        "sector_support": {s: v / _PCT
                           for s, v in (p.get("sector_support") or {}).items()
                           if v},
        "sme_stimulus": p.get("sme_stimulus", 0) / _PCT,
        "include_type_ii": p.get("include_type_ii", False),
        "include_retaliation": p.get("include_retaliation", False),
        "include_financing_drag": p.get("include_financing_drag", True),
        "extensions": ext or None,
    }
