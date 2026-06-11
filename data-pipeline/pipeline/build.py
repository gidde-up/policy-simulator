"""Per-country build orchestration.

Order: acquire -> parse (or cache) -> balance gates -> aggregate ->
employment -> Type II -> assemble JSON -> validation gates -> write to
staging -> atomic move into backend/app/data/countries/. Nothing is
written to backend/app/data/ unless every gate passed.
"""
import datetime
import json
import os

import numpy as np

import config
from pipeline import (aggregate, assumptions, concordance, download,
                      employment, extract, icio_parse, ilostat, miyazawa,
                      validate)
from pipeline.errors import PipelineError


def _round(arr, nd=6):
    return np.round(np.asarray(arr, dtype=float), nd).tolist()


def _method_map(method: str) -> tuple[str, str]:
    """cell.method -> (registry scope, registry method)."""
    return {
        "tim_child_sum": ("employment", "child_sum"),
        "tim_parent_residual": ("employment", "proportional_allocation"),
        "ilostat_residual": ("employment", "ILOSTAT_fallback"),
        "labr_child_sum": ("labour_compensation", "child_sum"),
        "labr_parent_residual": ("labour_compensation",
                                 "proportional_allocation"),
        "labr_economy_share": ("labour_compensation", "economy_share"),
    }[method]


def build_country(country: str, struct=None):
    year = config.REFERENCE_YEAR

    # --- native blocks (cache-aware) ---------------------------------
    blocks = icio_parse.load_cached_blocks(country, year)
    if blocks is None:
        zip_path = download.acquire_icio()
        if struct is None:
            struct = icio_parse.read_structure(zip_path, year)
        parsed = icio_parse.extract_country_blocks(zip_path, year, struct,
                                                   [country])
        icio_parse.cache_blocks(parsed, year)
        blocks = parsed[country]

    b = extract.derive({country: blocks}, country)
    extract.check_balances(b, country)
    industries = b["industries"]

    # --- concordance ---------------------------------------------------
    mapping = concordance.load_concordance()
    concordance.validate_against(mapping, industries)
    S = concordance.aggregator(mapping, industries)

    # --- aggregate -------------------------------------------------------
    agg = aggregate.aggregate_blocks(b, S, country)
    fd = aggregate.final_demand_vectors(agg)

    # --- employment ------------------------------------------------------
    emp = employment.build_employment(country, industries, b["x"], S, year)

    # --- Type II ----------------------------------------------------------
    t2 = miyazawa.build_type_ii(country, year, industries, b["x"], S, agg, fd)

    # --- baselines ---------------------------------------------------------
    emp_year, national_emp_thousands = ilostat.national_employment(country, year)
    lf_year, lf_thousands = ilostat.labour_force(country, year)

    # --- registry entries --------------------------------------------------
    entries = []
    prov_by_sector: dict[str, list[str]] = {s: [] for s in config.SECTORS_14}
    counter = 0
    for cell in emp["cells"] + t2["cells"]:
        if cell.method in ("tim_exact", "labr_exact"):
            continue
        counter += 1
        scope, method = _method_map(cell.method)
        sector = (cell.icio_code if cell.icio_code in config.SECTORS_14
                  else mapping.get(cell.icio_code, cell.icio_code))
        entry_id = f"{country}-{year}-{scope}-{cell.icio_code}-{counter}"
        src = {"dataset": ("OECD TiM 2025 (DSD_TIM_2025@DF_TIM_2025)"
                           if "labr" in cell.method or "tim" in cell.method
                           else f"ILOSTAT {config.ILOSTAT_EMP_BY_ACTIVITY}"),
               "url": (download.TIM_URL_TEMPLATE.split("?")[0]
                       if "tim" in cell.method or "labr" in cell.method
                       else config.ILOSTAT_BASE),
               "accessed": datetime.date.today().isoformat(),
               "reference_period": str(year)}
        if cell.method == "ilostat_residual":
            src["dataset"] = f"ILOSTAT {config.ILOSTAT_EMP_BY_ACTIVITY}"
            src["url"] = config.ILOSTAT_BASE
        entries.append(assumptions.make_entry(
            entry_id=entry_id, country=country, scope=scope, sector=sector,
            field="employment" if scope == "employment" else "compensation",
            icio_codes=[cell.icio_code], value=cell.persons,
            unit="persons" if scope == "employment" else "USD million",
            method=method, basis=cell.detail, source=src))
        if sector in prov_by_sector:
            prov_by_sector[sector].append(entry_id)

    if t2["propensity_capped"]:
        counter += 1
        entry_id = f"{country}-{year}-consumption_propensity-cap-{counter}"
        entries.append(assumptions.make_entry(
            entry_id=entry_id, country=country,
            scope="consumption_propensity", sector="all",
            field="household_consumption_column",
            icio_codes=[], value=1.0, unit="ratio", method="cap",
            basis=(f"implied propensity to consume out of labour income "
                   f"{t2['propensity']:.3f} > 1; consumption column scaled "
                   "to propensity 1 in the Miyazawa closure"),
            source={"dataset": "derived from OECD ICIO 2025 + TiM 2025",
                    "url": config.ICIO_DATASET_PAGE,
                    "accessed": datetime.date.today().isoformat(),
                    "reference_period": str(year)},
            notes="Households consume out of non-labour income too; the "
                  "closure only recycles labour income."))

    # --- assemble JSON ------------------------------------------------------
    lock = json.loads(config.SOURCES_LOCK.read_text(encoding="utf-8"))
    access_dates = {k: v["access_date"] for k, v in lock["sources"].items()}

    x = agg["x"]
    e_coeff = emp["persons_14"] / x  # jobs per USD million gross output

    M_col = agg["M"].sum(axis=0)
    Z_col = agg["Z"].sum(axis=0)
    imp_share_intermediate = M_col / np.maximum(M_col + Z_col, 1e-9)
    f_dom_tot = sum(fd["domestic"][k] for k in
                    ["households", "government", "gfcf", "inventories"])
    f_imp_tot = sum(fd["imported"][k] for k in
                    ["households", "government", "gfcf", "inventories"])
    imp_share_final = f_imp_tot / np.maximum(f_imp_tot + f_dom_tot, 1e-9)

    coverage = emp["coverage"]
    fallback_used = any(k != "tim_exact" for k in coverage)
    emp_source = "OECD TiM 2025 (EMPN)"
    if fallback_used:
        emp_source += (f"; fallbacks: {', '.join(sorted(k for k in coverage
                                                        if k != 'tim_exact'))}"
                       f" (see assumptions registry)")

    data = {
        "metadata": {
            "country": config.COUNTRY_NAMES[country],
            "iso3": country,
            "reference_year": year,
            "icio_edition": config.ICIO_EDITION,
            "icio_version": "regular (SML): 80 economies + ROW",
            "employment_source": emp_source,
            "compensation_source": "OECD TiM 2025 (LABR)",
            "access_dates": access_dates,
            "pipeline_version": config.PIPELINE_VERSION,
            "built": datetime.date.today().isoformat(),
            "units": {
                "flows": "USD million, current prices, reference year",
                "employment": "persons",
                "employment_coefficients":
                    "jobs per USD million of gross output",
            },
            "notes": [
                "households final demand = HFCE + NPISH",
                "inventories kept so that x = Z*1 + F*1 balances",
                "exports computed as residual: x - domestic intermediate "
                "use - domestic final demand",
                "GDP proxy = sum(VA) + sum(TLS) (market prices)",
            ],
        },
        "sectors": config.SECTORS_14,
        "A_d": _round(agg["A_d"]),
        "A_m": _round(agg["A_m"]),
        "L_typeI": _round(agg["L_typeI"]),
        "L_typeII": _round(t2["L_typeII"]),
        "x": _round(x, 3),
        "VA": _round(agg["va"], 3),
        "TLS": _round(agg["tls"], 3),
        "employment": {
            "persons": _round(emp["persons_14"], 1),
            "coverage": coverage,
            "provenance": {k: v for k, v in prov_by_sector.items() if v},
        },
        "employment_coefficients": _round(e_coeff),
        "final_demand": {k: _round(v, 3)
                         for k, v in fd["domestic"].items()},
        "imported_final_demand": {k: _round(v, 3)
                                  for k, v in fd["imported"].items()},
        "import_shares": {
            "intermediate": _round(imp_share_intermediate),
            "final": _round(imp_share_final),
        },
        "type_ii": {
            "compensation_of_employees": _round(t2["compensation_14"], 3),
            "labour_income_coefficients": _round(t2["labour_income_coeff"]),
            "consumption_coefficients": _round(t2["consumption_coeff"]),
            "propensity_out_of_labour_income": round(t2["propensity"], 4),
            "propensity_capped": t2["propensity_capped"],
            "economy_labour_share": round(t2["economy_labour_share"], 4),
        },
        "baseline_totals": {
            "gdp_usd_million": round(float(agg["va"].sum()
                                           + agg["tls"].sum()), 1),
            "national_employment_persons": national_emp_thousands * 1000.0,
            "national_employment_year": emp_year,
            "labour_force_persons": lf_thousands * 1000.0,
            "labour_force_year": lf_year,
            "source": f"ILOSTAT ({config.ILOSTAT_EMP_BY_ACTIVITY}, "
                      f"{config.ILOSTAT_LABOUR_FORCE})",
        },
    }

    # --- validation gates ----------------------------------------------------
    ok, results = validate.run_all(data)
    if not ok:
        failed = [(n, det) for n, p, det in results if not p]
        raise PipelineError(
            stage=f"build.validate[{country}]",
            expected="all validation checks pass",
            found="; ".join(f"{n}: {det}" for n, det in failed),
            action="Inspect the failed checks; nothing was written.",
        )

    # --- write: staging then atomic move ---------------------------------------
    config.STAGING_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    staged = config.STAGING_DIR / f"{country}.json"
    staged.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    final = config.OUTPUT_DIR / f"{country}.json"
    os.replace(staged, final)

    # registry update (idempotent per country)
    registry = assumptions.load_registry()
    assumptions.replace_country_entries(registry, country, entries)
    assumptions.write_registry(registry)

    # report
    extra = [
        "## Coverage",
        "",
        f"- TiM employment cells: {coverage}",
        f"- Type II propensity: {t2['propensity']:.3f}"
        f"{' (capped at 1)' if t2['propensity_capped'] else ''}",
        f"- Economy-wide labour share (observed sectors): "
        f"{t2['economy_labour_share']:.3f}",
        f"- Registry entries written: {len(entries)}",
        "",
        "## Type I / Type II employment multipliers (jobs per USD million "
        "of final demand)",
        "",
        "| sector | e (direct) | Type I | Type II |",
        "|---|---|---|---|",
    ]
    e = np.array(data["employment_coefficients"])
    mI = e @ np.array(data["L_typeI"])
    mII = e @ np.array(data["L_typeII"])
    for k, s in enumerate(config.SECTORS_14):
        extra.append(f"| {s} | {e[k]:.2f} | {mI[k]:.2f} | {mII[k]:.2f} |")

    report = validate.render_report(country, data, results, extra)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (config.REPORTS_DIR / f"validation_report_{country}.md").write_text(
        report, encoding="utf-8")

    return data, results
