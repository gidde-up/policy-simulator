"""The six validation checks -- single source of truth.

Used twice: as hard gates inside build.py (before anything is written to
backend/app/data/) and as thin pytest wrappers in tests/. Each check
returns (passed: bool, details: str); check 4 additionally returns soft
flags that do not fail the build.
"""
import numpy as np

import config


def check_coefficient_sums(d: dict):
    """1. colsum(A_d) + colsum(A_m) + VA-coeff + TLS-coeff ~= 1 (+-1%)."""
    A_d = np.array(d["A_d"])
    A_m = np.array(d["A_m"])
    x = np.array(d["x"])
    va = np.array(d["VA"])
    tls = np.array(d["TLS"])
    sums = A_d.sum(axis=0) + A_m.sum(axis=0) + va / x + tls / x
    gap = float(np.max(np.abs(sums - 1.0)))
    return gap <= config.TOL_COEFF_SUM, (
        f"max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = {gap:.5f} "
        f"(tolerance {config.TOL_COEFF_SUM})")


def check_nonnegative(d: dict):
    """2. A_d, A_m, employment, x, VA >= 0 (negative inventories allowed)."""
    problems = []
    for key in ["A_d", "A_m", "x", "VA", "employment", "employment_coefficients"]:
        arr = np.array(d[key] if key != "employment"
                       else d["employment"]["persons"])
        if np.min(arr) < 0:
            problems.append(f"{key} min={np.min(arr):.4g}")
    neg_inv = float(np.min(np.array(d["final_demand"]["inventories"])))
    flag = f"inventories min={neg_inv:.1f} (negative cells permitted)" \
        if neg_inv < 0 else ""
    return not problems, ("; ".join(problems) or "all non-negative") + \
        (f" | {flag}" if flag else "")


def check_spectral_radius(d: dict):
    """3. spectral radius of A_d < 1."""
    rho = max(abs(np.linalg.eigvals(np.array(d["A_d"]))))
    return rho < 1.0, f"spectral radius(A_d) = {rho:.4f}"


def check_output_multipliers(d: dict):
    """4. Type I output multipliers: hard (1.0, 3.5), soft [1.1, 2.5]."""
    m = np.array(d["L_typeI"]).sum(axis=0)
    lo_h, hi_h = config.MULTIPLIER_HARD_RANGE
    lo_s, hi_s = config.MULTIPLIER_SOFT_RANGE
    hard_ok = bool(np.all(m > lo_h) and np.all(m < hi_h))
    flags = [f"{s}={v:.3f}" for s, v in zip(config.SECTORS_14, m)
             if not (lo_s <= v <= hi_s)]
    detail = ("multipliers: " +
              ", ".join(f"{s}={v:.2f}"
                        for s, v in zip(config.SECTORS_14, m)))
    if flags:
        detail += f" | FLAGGED outside [{lo_s}, {hi_s}]: {', '.join(flags)}"
    return hard_ok, detail


def check_employment_total(d: dict):
    """5. sum of sectoral employment within 10% of ILOSTAT national."""
    sector_sum = float(np.sum(d["employment"]["persons"]))
    national = float(d["baseline_totals"]["national_employment_persons"])
    gap = abs(sector_sum - national) / national
    return gap <= config.EMPLOYMENT_GAP_MAX, (
        f"sector sum {sector_sum:,.0f} vs ILOSTAT national {national:,.0f} "
        f"({d['baseline_totals']['national_employment_year']}): "
        f"gap {gap:.2%} (max {config.EMPLOYMENT_GAP_MAX:.0%})")


def check_type_ii_dominance(d: dict):
    """6 (structural part). L_typeII >= L_typeI element-wise."""
    gap = float(np.min(np.array(d["L_typeII"]) - np.array(d["L_typeI"])))
    return gap >= -1e-9, f"min(L_II - L_I) = {gap:.2e}"


ALL_CHECKS = [
    check_coefficient_sums,
    check_nonnegative,
    check_spectral_radius,
    check_output_multipliers,
    check_employment_total,
    check_type_ii_dominance,
]


def run_all(d: dict):
    """Returns (all_passed, [(name, passed, details)])."""
    results = []
    for fn in ALL_CHECKS:
        passed, details = fn(d)
        results.append((fn.__name__, passed, details))
    return all(r[1] for r in results), results


def render_report(country: str, d: dict, results, extra_lines=None) -> str:
    meta = d["metadata"]
    lines = [
        f"# Validation report -- {meta['country']} ({country})",
        "",
        f"- ICIO edition: {meta['icio_edition']}, reference year "
        f"{meta['reference_year']}",
        f"- Employment source: {meta['employment_source']}",
        f"- Pipeline version: {meta['pipeline_version']}, built "
        f"{meta['built']}",
        "",
        "## Checks",
        "",
    ]
    for name, passed, details in results:
        status = "PASS" if passed else "FAIL"
        lines.append(f"- **{status}** `{name}`: {details}")
    if extra_lines:
        lines += [""] + list(extra_lines)
    lines.append("")
    return "\n".join(lines)
