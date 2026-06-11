"""Type II (induced effects) via the Miyazawa household-endogenisation.

Augmented coefficient matrix (15 x 15):
    A* = [ A_d   h_c ]
         [ h_r'   0  ]
  h_r[j] = compensation of employees in sector j per unit of gross output
           (labour income row), from TiM LABR (USD million, same valuation
           as ICIO);
  h_c[i] = household final consumption of sector i per unit of total
           labour income (consumption column), domestic HFCE only.

L_typeII is the upper-left 14 x 14 block of (I - A*)^-1.

Fallback chain for missing LABR cells (each registered):
  labr_exact -> labr_child_sum -> economy-wide labour share of VA applied
  to the missing industries' estimated VA (sector VA allocated by native
  output shares). The economy-wide share is computed from the LABR cells
  that ARE observed, never typed in.
If the implied aggregate propensity to consume out of labour income
exceeds 1, the consumption column is scaled to propensity 1 and the cap
is registered.
"""
import numpy as np

import config
from pipeline.errors import PipelineError
from pipeline import download, employment


def build_type_ii(country: str, year: int, industries: list[str],
                  x_native: np.ndarray, S: np.ndarray, agg: dict,
                  fd_vectors: dict):
    """Returns dict with L_typeII, compensation by sector, provenance."""
    labr_path = download.acquire_tim(config.TIM_MEASURE_COMPENSATION,
                                     config.COUNTRIES, year)
    labr = employment.load_tim_csv(labr_path, config.TIM_MEASURE_COMPENSATION,
                                   country, year)

    n_native = len(industries)
    comp_native, cells = employment.fill_from_tim(labr, industries,
                                                  x_native, "labr")
    obs_native = ~np.isnan(comp_native)
    va_14 = agg["va"]
    x_14 = agg["x"]
    comp_obs_14 = S @ np.nan_to_num(comp_native, nan=0.0)

    # economy-wide labour share computed from fully observed sectors only
    n14 = len(config.SECTORS_14)
    fully_observed = []
    for k in range(n14):
        members = np.where(S[k] == 1)[0]
        if obs_native[members].all():
            fully_observed.append(k)
    if not fully_observed:
        raise PipelineError(
            stage=f"miyazawa.labour_share[{country}]",
            expected="at least one fully LABR-observed sector",
            found="none",
            action="LABR coverage too sparse; stop.",
        )
    economy_share = (sum(comp_obs_14[k] for k in fully_observed)
                     / sum(va_14[k] for k in fully_observed))

    # fill missing native industries: VA estimated by output share within
    # the sector, compensation = economy-wide labour share x that VA
    comp_14 = comp_obs_14.copy()
    for k in range(n14):
        members = np.where(S[k] == 1)[0]
        missing = [i for i in members if not obs_native[i]]
        if not missing:
            continue
        x_sector = x_native[members].sum()
        if x_sector <= 0:
            continue
        va_missing = va_14[k] * (x_native[missing].sum() / x_sector)
        est = economy_share * va_missing
        comp_14[k] += est
        cells.append(employment.EmploymentCell(
            config.SECTORS_14[k], float(est), "labr_economy_share",
            detail=(f"missing native industries "
                    f"{[industries[i] for i in missing]}; economy-wide "
                    f"labour share {economy_share:.3f} applied to VA "
                    f"estimated by native output shares")))

    # compensation cannot exceed value added
    over = comp_14 > va_14 * 1.001
    if np.any(over):
        ks = [config.SECTORS_14[k] for k in np.where(over)[0]]
        raise PipelineError(
            stage=f"miyazawa.comp_vs_va[{country}]",
            expected="compensation of employees <= value added per sector",
            found=f"violated in {ks}",
            action="Inspect LABR units/valuation vs ICIO.",
        )

    h_r = comp_14 / x_14

    hh = fd_vectors["domestic"]["households"]
    total_comp = comp_14.sum()
    propensity = float(hh.sum() / total_comp)
    capped = propensity > 1.0
    hh_used = hh * (total_comp / hh.sum()) if capped else hh
    h_c = hh_used / total_comp

    A_star = np.zeros((n14 + 1, n14 + 1))
    A_star[:n14, :n14] = agg["A_d"]
    A_star[:n14, n14] = h_c
    A_star[n14, :n14] = h_r

    rho = max(abs(np.linalg.eigvals(A_star)))
    if rho >= 1.0:
        raise PipelineError(
            stage=f"miyazawa.spectral[{country}]",
            expected="spectral radius of augmented matrix < 1",
            found=f"{rho:.4f}",
            action="Inspect h_r / h_c construction.",
        )
    L_star = np.linalg.inv(np.eye(n14 + 1) - A_star)
    L_II = L_star[:n14, :n14]

    if np.min(L_II - agg["L_typeI"]) < -1e-9:
        raise PipelineError(
            stage=f"miyazawa.dominance[{country}]",
            expected="L_typeII >= L_typeI element-wise",
            found=f"min gap {np.min(L_II - agg['L_typeI']):.2e}",
            action="Numerical issue; inspect.",
        )

    return {
        "L_typeII": L_II,
        "compensation_14": comp_14,
        "labour_income_coeff": h_r,
        "consumption_coeff": h_c,
        "propensity": propensity,
        "propensity_capped": capped,
        "economy_labour_share": float(economy_share),
        "cells": cells,
    }
