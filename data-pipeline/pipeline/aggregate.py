"""Aggregation of native-detail blocks to the 14 didactic sectors.

Aggregation uses the 14 x n indicator matrix S from the concordance:
  Z_14 = S Z S',  M_14 = S M S',  F_14 = S F,  x_14 = S x, etc.
Coefficients are recomputed on the aggregates (not aggregated from
native coefficients), as specified:
  A_d = Z_dd diag(x)^-1,  A_m = M diag(x)^-1,  L_I = (I - A_d)^-1.
"""
import numpy as np

import config
from pipeline.errors import PipelineError


def aggregate_blocks(b: dict, S: np.ndarray, country: str) -> dict:
    Z = S @ b["Z_dd"] @ S.T
    M = S @ b["M"] @ S.T
    F_dom = S @ b["F_dom"]
    F_imp = S @ b["F_imp"]
    x = S @ b["x"]
    va = S @ b["va"]
    tls = S @ b["tls"]
    exports = S @ b["exports"]

    if np.any(x <= 0):
        k = int(np.argmin(x))
        raise PipelineError(
            stage=f"aggregate[{country}]",
            expected="strictly positive gross output in all 14 sectors",
            found=f"x[{config.SECTORS_14[k]}] = {x[k]:.1f}",
            action="Inspect concordance and source data.",
        )

    inv_x = 1.0 / x
    A_d = Z * inv_x
    A_m = M * inv_x

    rho = max(abs(np.linalg.eigvals(A_d)))
    if rho >= 1.0:
        raise PipelineError(
            stage=f"aggregate.spectral[{country}]",
            expected="spectral radius of 14-sector A_d < 1",
            found=f"{rho:.4f}",
            action="Inspect aggregation.",
        )
    L_I = np.linalg.inv(np.eye(len(config.SECTORS_14)) - A_d)

    # aggregation must preserve the column identity
    col_lhs = Z.sum(axis=0) + M.sum(axis=0) + tls + va
    scale = np.maximum(np.abs(x), 1e-9)
    rel = float(np.max(np.abs(col_lhs - x) / scale))
    if rel > config.TOL_COLUMN_IDENTITY:
        raise PipelineError(
            stage=f"aggregate.column_identity[{country}]",
            expected="identities preserved after aggregation",
            found=f"max relative gap {rel:.4%}",
            action="Aggregation bug; S must be a 0/1 partition matrix.",
        )

    fd = dict(zip(b["fd_categories"], F_dom.T))
    fd_imp = dict(zip(b["fd_categories"], F_imp.T))

    return {
        "Z": Z, "M": M, "x": x, "va": va, "tls": tls,
        "A_d": A_d, "A_m": A_m, "L_typeI": L_I,
        "exports": exports,
        "fd_dom": fd, "fd_imp": fd_imp,
        "spectral_radius": rho,
    }


def final_demand_vectors(agg: dict) -> dict:
    """Map ICIO FD categories to the model's didactic categories.

    households  = HFCE + NPISH (non-profits serving households folded in;
                  documented in JSON metadata)
    government  = GGFC
    gfcf        = GFCF
    inventories = INVNT (kept so x = Z*1 + F*1 balances)
    exports     = residual row computation from extract.py
    DPABR (direct purchases abroad by residents) = household consumption
                  supplied from abroad; folded into IMPORTED household
                  demand. Domestic supply into DPABR must be ~0 (a country
                  cannot domestically supply purchases made abroad);
                  violations stop the build.
    Any other discovered category (NONRES, FD) stops the build -- its
    treatment must be decided and documented, not guessed.
    """
    dom, imp = agg["fd_dom"], agg["fd_imp"]
    known = {"HFCE", "NPISH", "GGFC", "GFCF", "INVNT", "DPABR"}
    extra = [k for k in dom if k not in known]
    if extra:
        raise PipelineError(
            stage="aggregate.final_demand",
            expected=f"FD categories within {sorted(known)}",
            found=f"additional categories {extra}",
            action="Decide and document their treatment before proceeding.",
        )
    zeros = np.zeros(len(config.SECTORS_14))

    dpabr_dom = dom.get("DPABR", zeros)
    hh_dom = dom.get("HFCE", zeros) + dom.get("NPISH", zeros)
    if float(np.abs(dpabr_dom).sum()) > 0.005 * float(hh_dom.sum()):
        raise PipelineError(
            stage="aggregate.final_demand",
            expected="domestic supply into DPABR ~ 0",
            found=f"{float(dpabr_dom.sum()):.1f} USD million "
                  f"({float(np.abs(dpabr_dom).sum()) / float(hh_dom.sum()):.2%} "
                  "of household demand)",
            action="Inspect DPABR semantics in this edition before mapping.",
        )

    out = {
        # tiny domestic DPABR (rounding) kept with households for balance
        "households": hh_dom + dpabr_dom,
        "government": dom.get("GGFC", zeros),
        "gfcf": dom.get("GFCF", zeros),
        "inventories": dom.get("INVNT", zeros),
        "exports": agg["exports"],
    }
    out_imp = {
        "households": (imp.get("HFCE", zeros) + imp.get("NPISH", zeros)
                       + imp.get("DPABR", zeros)),
        "government": imp.get("GGFC", zeros),
        "gfcf": imp.get("GFCF", zeros),
        "inventories": imp.get("INVNT", zeros),
    }
    return {"domestic": out, "imported": out_imp}
