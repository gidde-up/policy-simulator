"""Data and model caveats for one country (Workstream F.3).

Pure assembly from the verified country JSON - no FastAPI dependency, so
it is unit-testable by file-path import (like lever_params.py). Nothing is
hardcoded per country: the employment-validation gap is computed from the
data and a warning is raised only when it is large.
"""

GAP_WARNING_THRESHOLD_PCT = 10.0


def country_caveats(iso3: str, d: dict) -> dict:
    meta = d.get("metadata", {})
    inf = d.get("informality", {})
    ctx = inf.get("context", {})
    bt = d.get("baseline_totals", {})
    emp = d.get("employment", {})
    persons = emp.get("persons", []) if isinstance(emp, dict) else (emp or [])
    sector_sum = float(sum(persons)) if persons else 0.0
    national = float(bt.get("national_employment_persons") or 0.0)
    gap_pct = ((sector_sum - national) / national * 100.0
               if national > 0 else None)
    warnings = []
    if gap_pct is not None and abs(gap_pct) >= GAP_WARNING_THRESHOLD_PCT:
        warnings.append(
            "the model employment denominator (sector-sum, national-accounts "
            "concept) differs from the ILOSTAT labour-force-survey total by "
            f"{gap_pct:+.0f}%; compare countries with care")
    return {
        "io_data": f"OECD ICIO {meta.get('icio_edition')}",
        "io_data_year": meta.get("reference_year"),
        "employment_data": meta.get("employment_source"),
        "employment_data_year": meta.get("reference_year"),
        "compensation_data": meta.get("compensation_source"),
        "informality_indicator": inf.get("indicator"),
        "informality_year": inf.get("year_used"),
        "working_poverty_year": ctx.get("working_poverty_year"),
        "employment_validation_gap_pct": gap_pct,
        "financing_mpc_status": (
            "literature_based (GLOBAL marginal propensity to consume; a "
            "country-specific MPC is not available, so the same central "
            "value is used for every country)"),
        "type_ii_propensity_capped": True,
        "notes": meta.get("notes", []),
        "warnings": warnings,
    }
