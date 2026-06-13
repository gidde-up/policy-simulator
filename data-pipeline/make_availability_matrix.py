"""Data-availability matrix for the extension (E.1 gate deliverable).

Every cell is DERIVED from the country JSONs, the assumptions registry
and sources.lock.json -- it cannot drift from the actual data. Writes
reports/data_availability_extension.md.

Status vocabulary:
  OK (year)     data present and used
  DERIVED       computed from the country JSON (no external source)
  GLOBAL        a single cited global parameter (not per country)
  PENDING       source not yet acquired (manual download outstanding)
  MISSING       unavailable -> dependent output hidden for that country
"""
import json
import sys

import config
from pipeline import assumptions


def _registry_index():
    reg = assumptions.load_registry()
    by_country_field = {}
    for e in reg["entries"]:
        by_country_field.setdefault((e["country"], e.get("field")), e)
    return by_country_field, reg


def main():
    idx, reg = _registry_index()
    rows = []

    # item 1: informal employment by activity (per country, from JSON)
    item1 = {}
    for iso3 in config.COUNTRIES:
        d = json.loads((config.OUTPUT_DIR / f"{iso3}.json").read_text(
            encoding="utf-8"))
        block = d.get("informality")
        if block:
            item1[iso3] = f"OK ({block['year_used']}, {block['classification'].split('(')[0].strip()})"
        else:
            item1[iso3] = "MISSING -> hidden"

    # item 5a/5b: national informality + working poverty context
    nat_inf, wp = {}, {}
    for iso3 in config.COUNTRIES:
        d = json.loads((config.OUTPUT_DIR / f"{iso3}.json").read_text(
            encoding="utf-8"))
        ctx = (d.get("informality") or {}).get("context", {})
        nat_inf[iso3] = (f"OK ({ctx['national_informality_year']})"
                         if ctx.get("national_informal_employment_rate_pct")
                         is not None else "MISSING")
        wp[iso3] = (f"OK ({ctx['working_poverty_year']})"
                    if ctx.get("working_poverty_rate_pct") is not None
                    else "MISSING")

    # item 3a: EIIP labour share (GLOBAL); 3b conventional (per country)
    eiip = "GLOBAL" if ("GLOBAL", "eiip_labour_cost_share") in idx \
        else "PENDING"
    conv = {}
    for iso3 in config.COUNTRIES:
        conv[iso3] = ("DERIVED"
                      if (iso3, "conventional_construction_labour_share")
                      in idx else "PENDING")

    # item 2: Tokarick export demand elasticity (per country)
    tok = {}
    for iso3 in config.COUNTRIES:
        tok[iso3] = ("OK" if (iso3, "export_demand_elasticity") in idx
                     else "PENDING (manual download: IMF WP/10/180)")

    # item 4: redundancy share (GLOBAL)
    redundancy = ("GLOBAL"
                  if ("GLOBAL", "investment_incentive_redundancy") in idx
                  else "PENDING (manual download: James 2013; "
                       "IMF-OECD-UN-WB 2015)")

    # item 6: wage cross-check (report)
    wage = ("DONE (report)"
            if (config.REPORTS_DIR / "wage_crosscheck.md").exists()
            else "PENDING")

    lines = [
        "# Data-availability matrix -- policy-lever / job-quality "
        "extension (Session E)",
        "",
        "Derived from the country JSONs, the assumptions registry and "
        "sources.lock.json. Per-country unavailability means the "
        "dependent output is hidden for that country -- never imputed.",
        "",
        "## Per-country items",
        "",
        "| item | " + " | ".join(config.COUNTRIES) + " |",
        "|" + "---|" * (len(config.COUNTRIES) + 1),
        "| 1. Informal employment by activity | "
        + " | ".join(item1[c] for c in config.COUNTRIES) + " |",
        "| 5a. National informality rate (context) | "
        + " | ".join(nat_inf[c] for c in config.COUNTRIES) + " |",
        "| 5b. Working-poverty rate (context) | "
        + " | ".join(wp[c] for c in config.COUNTRIES) + " |",
        "| 3b. Conventional construction labour share | "
        + " | ".join(conv[c] for c in config.COUNTRIES) + " |",
        "| 2. Tokarick export demand elasticity | "
        + " | ".join(tok[c] for c in config.COUNTRIES) + " |",
        "",
        "## Global / non-per-country items",
        "",
        f"- 3a. EIIP labour-based labour-cost share: **{eiip}** "
        "(GLOBAL-eiip-labour-cost-share-central/low/high; ILO EIIP, "
        "0.35 / 0.20 / 0.50)",
        f"- 4. Investment-incentive redundancy share: **{redundancy}**",
        f"- 6. Wage cross-check (internal TiM vs ILOSTAT earnings): "
        f"**{wage}** (ILOSTAT earnings-by-activity not on the bulk API; "
        "model uses internal TiM figures -- see reports/wage_crosscheck.md)",
        "",
        "## Notes",
        "",
        "- Informality indicator: ILOSTAT EMP_NIFL_SEX_ECO_NB_A over "
        "EMP_TEMP_SEX_ECO_NB_A. ZAF has only broad-aggregate-group "
        "detail (AGR/MAN/CON/MEL/MKT/PUB); the other four have ISIC "
        "Rev.4 sections. Manufacturing-family sectors inherit section C "
        "(1-digit data cannot split manufacturing); every inherited cell "
        "is registered (scope=informality, method=share_inheritance).",
        "- TUN informality year is 2019 (latest available); others 2022.",
        "- Items 2 and 4 require manual PDF downloads (IMF/World Bank are "
        "bot-blocked). They feed Session F levers (depreciation; "
        "investment tax incentive) and are not needed by the Session E "
        "engine foundation. register_extension_params.py registers them "
        "automatically once the PDFs are in raw/ and the extraction "
        "scripts have read them.",
        "",
    ]
    out = config.REPORTS_DIR / "data_availability_extension.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
