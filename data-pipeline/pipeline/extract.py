"""Balance gates on native-detail country blocks.

These run immediately after parsing, before any aggregation. They verify
that the parsed blocks reproduce the ICIO accounting identities; failure
means a parsing error, not a data problem, and stops the pipeline.

Identities (per country c, native industry detail, values in USD million):
  column: sum_i Z_all[i,j] + TLS_j + VA_j = OUT_j      (ICIO is balanced)
          where sum_i Z_all[:,j] = Z_dd[:,j].sum() + M[:,j].sum()
  row:    sum_j Z_dd[i,j] + sum_fd F_dom[i,fd] + exports_i = x_i
          (exports computed as the residual, so this holds by
          construction; the substantive check is exports_i >= 0)
  VA:     x_j - intermediates_j - TLS_j  ~  VA_j (within tolerance)
"""
import numpy as np

import config
from pipeline.errors import PipelineError


def derive(blocks: dict, country: str) -> dict:
    """Add derived quantities (exports, A_d, A_m at native detail)."""
    b = blocks[country]
    Z_dd, M, F_dom, x = b["Z_dd"], b["M"], b["F_dom"], b["x"]

    exports = x - Z_dd.sum(axis=1) - F_dom.sum(axis=1)
    b["exports"] = exports

    with np.errstate(divide="ignore", invalid="ignore"):
        inv_x = np.where(x > 0, 1.0 / x, 0.0)
    b["A_d"] = Z_dd * inv_x
    b["A_m"] = M * inv_x
    return b


def check_balances(b: dict, country: str):
    Z_dd, M, va, tls, x = b["Z_dd"], b["M"], b["va"], b["tls"], b["x"]
    out_row = b["out_row"]

    # ICIO values are published rounded to 3 decimals (USD thousand);
    # summing ~4200 rounded cells leaves absolute residue of order 0.01-
    # 0.05 USD million, which inflates RELATIVE gaps on tiny columns
    # (e.g. TUN B07, output 7.9). Gaps below this floor are rounding,
    # not structure.
    abs_floor = 1e-6 * float(np.abs(out_row).sum())

    # Column identity: intermediates + TLS + VA == OUT (column totals).
    # out_row is the OUT special row at c's columns = gross output of
    # using industry j; compare against x (OUT column at c's rows).
    col_lhs = Z_dd.sum(axis=0) + M.sum(axis=0) + tls + va
    rel = _rel_gap(col_lhs, out_row, abs_floor)
    if rel > config.TOL_COLUMN_IDENTITY:
        raise PipelineError(
            stage=f"extract.column_identity[{country}]",
            expected=f"sum(Z)+TLS+VA == OUT within {config.TOL_COLUMN_IDENTITY:.1%}",
            found=f"max relative gap {rel:.4%}",
            action="Parsing error likely; inspect column classification.",
        )

    # OUT row at c's columns must equal OUT column at c's rows (both are
    # gross output of c's industries).
    rel = _rel_gap(out_row, x, abs_floor)
    if rel > config.TOL_COLUMN_IDENTITY:
        raise PipelineError(
            stage=f"extract.output_consistency[{country}]",
            expected="OUT row == OUT column for c's industries",
            found=f"max relative gap {rel:.4%}",
            action="Row/column ordering mismatch; inspect parser.",
        )

    # Derived VA = x - intermediates - TLS vs VA row
    va_derived = x - Z_dd.sum(axis=0) - M.sum(axis=0) - tls
    rel = _rel_gap(va_derived, va, abs_floor)
    if rel > config.TOL_VA_DERIVED:
        raise PipelineError(
            stage=f"extract.va_check[{country}]",
            expected=f"derived VA == VA row within {config.TOL_VA_DERIVED:.0%}",
            found=f"max relative gap {rel:.4%}",
            action="Inspect special-row identification.",
        )

    # Exports residual: tiny negatives can arise from rounding; anything
    # materially negative signals a parsing problem.
    exports = b["exports"]
    floor = -0.001 * max(x.max(), 1.0)
    if exports.min() < floor:
        i = int(exports.argmin())
        raise PipelineError(
            stage=f"extract.exports[{country}]",
            expected="non-negative exports by industry (residual)",
            found=f"exports[{b['industries'][i]}] = {exports[i]:.1f}",
            action="Inspect domestic-use computation.",
        )
    np.clip(exports, 0.0, None, out=exports)

    # Spectral radius of native A_d
    rho = max(abs(np.linalg.eigvals(b["A_d"])))
    if rho >= 1.0:
        raise PipelineError(
            stage=f"extract.spectral[{country}]",
            expected="spectral radius of native A_d < 1",
            found=f"{rho:.4f}",
            action="Matrix not productive; inspect extraction.",
        )


def _rel_gap(a: np.ndarray, b: np.ndarray, abs_floor: float = 0.0) -> float:
    """Max relative gap, ignoring gaps below the absolute rounding floor."""
    gap = np.abs(a - b)
    gap = np.where(gap <= abs_floor, 0.0, gap)
    scale = np.maximum(np.abs(b), np.abs(b).max() * 1e-6 + 1e-9)
    return float(np.max(gap / scale))
