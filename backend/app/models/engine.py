"""Demand-driven Leontief engine over the verified country JSONs.

Data: backend/app/data/countries/{ISO3}.json, computed by /data-pipeline
from OECD ICIO 2025 (year 2022) + OECD TiM 2025 + ILOSTAT. Behavioural
parameters: backend/app/data/assumptions.json (GLOBAL-* entries, each
with a full citation). This module contains NO behavioural constants;
an AST test enforces that no numeric literal outside {0, 1, 2} appears.

Units: all flows in USD million (current prices, reference year 2022);
employment in persons; all rates as FRACTIONS (percent-to-fraction
conversion happens in the API layer, never here).

Core: dF (final-demand shock, 14-vector) -> dE = e_hat L dF with
  direct   = e * dF
  indirect = e * ((L_I - I) dF)
  induced  = e * ((L_II - L_I) dF)     [Type II toggle only; labelled
             an upper bound -- the household closure caps the
             consumption propensity at 1]
  dx = L dF;  dVA = (VA/x) * dx

Tariff on sector s at rate t -- four channels:
  (i)   import substitution: import demand falls by |eps|*t (capped at
        the full import flow); the share captured domestically equals
        the sector's domestic absorption share (data-derived).
  (ii)  downstream cost: imported-input price rise propagates through
        the cost structure, dp' = dp_m' A_m (I - A_d)^-1; final demand
        for domestic output (incl. exports) falls by |eta| * dp.
  (iii) real income: the consumer price increase (cost-push plus the
        direct price rise on imported final goods of s) reduces
        household consumption across all sectors.
  (iv)  retaliation (toggle, default off, stylised): export demand in
        the top-N export sectors falls by t_bar * retaliation share,
        t_bar = import-weighted average tariff across tariffed sectors.

Government sector support: dF_s += rate_s * x_s; the financing drag
toggle (default on) subtracts the same total from household consumption
(tax-financed), spread by the household consumption vector.

SME / demand stimulus: dF += multiplier * amount * household shares,
amount = rate * GDP; the multiplier is the cited first-round
translation into domestic demand (leakages), NOT the I-O multiplier.
"""
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_COUNTRIES_DIR = _DATA_DIR / "countries"
_ASSUMPTIONS_PATH = _DATA_DIR / "assumptions.json"

_FD_KEYS = ["households", "government", "gfcf", "inventories", "exports"]


@dataclass
class CountryData:
    iso3: str
    name: str
    sectors: list
    A_d: np.ndarray
    A_m: np.ndarray
    L_I: np.ndarray
    L_II: np.ndarray
    x: np.ndarray
    va: np.ndarray
    e: np.ndarray                 # jobs per USD million of gross output
    employment: np.ndarray        # persons by sector
    fd: dict                      # domestic final demand vectors
    fd_imported: dict             # imported final demand vectors
    imports_intermediate: np.ndarray   # by product (supplying industry)
    imports_final: np.ndarray
    domestic_absorption: np.ndarray    # share, by product
    metadata: dict
    baseline_totals: dict

    @classmethod
    def from_dict(cls, d: dict) -> "CountryData":
        def arr(v):
            return np.asarray(v, dtype=float)
        return cls(
            iso3=d["metadata"]["iso3"],
            name=d["metadata"]["country"],
            sectors=list(d["sectors"]),
            A_d=arr(d["A_d"]),
            A_m=arr(d["A_m"]),
            L_I=arr(d["L_typeI"]),
            L_II=arr(d["L_typeII"]),
            x=arr(d["x"]),
            va=arr(d["VA"]),
            e=arr(d["employment_coefficients"]),
            employment=arr(d["employment"]["persons"]),
            fd={k: arr(d["final_demand"][k]) for k in _FD_KEYS},
            fd_imported={k: arr(d["imported_final_demand"][k])
                         for k in d["imported_final_demand"]},
            imports_intermediate=arr(d["imports_by_product"]["intermediate"]),
            imports_final=arr(d["imports_by_product"]["final"]),
            domestic_absorption=arr(d["import_shares"]["domestic_absorption"]),
            metadata=d["metadata"],
            baseline_totals=d["baseline_totals"],
        )

    @property
    def baseline_employment(self) -> float:
        """Sector-sum employment (national-accounts concept): the
        denominator for %-of-employment readings, NOT the ILOSTAT
        LFS total (different concept; see JSON metadata notes)."""
        return float(self.employment.sum())

    @property
    def gdp(self) -> float:
        return float(self.baseline_totals["gdp_usd_million"])

    @property
    def imports_by_product(self) -> np.ndarray:
        return self.imports_intermediate + self.imports_final


_COUNTRY_CACHE: dict = {}
_PARAMS_CACHE: list = []


def available_countries() -> list:
    return sorted(p.stem for p in _COUNTRIES_DIR.glob("*.json"))


def load_country(iso3: str) -> CountryData:
    if iso3 not in _COUNTRY_CACHE:
        path = _COUNTRIES_DIR / f"{iso3}.json"
        if not path.exists():
            raise KeyError(f"no verified country data for {iso3}; "
                           f"available: {available_countries()}")
        _COUNTRY_CACHE[iso3] = CountryData.from_dict(
            json.loads(path.read_text(encoding="utf-8")))
    return _COUNTRY_CACHE[iso3]


@dataclass
class EngineParams:
    eps: float                    # import demand elasticity (negative)
    eta: float                    # own-price demand elasticity (negative)
    retaliation_share: float
    retaliation_top_n: int
    fiscal_multiplier: float
    entry_ids: list = field(default_factory=list)


def _registry():
    return json.loads(_ASSUMPTIONS_PATH.read_text(encoding="utf-8"))


def load_params(variant: str = "central", iso3: str | None = None
                ) -> EngineParams:
    """variant: central | low | high (parameter-magnitude variants for
    the uncertainty range). For the central import demand elasticity a
    country-specific cited value ({ISO3}-import-demand-elasticity-central,
    KNO 2008 Table 1 import-weighted averages) takes precedence over the
    GLOBAL median."""
    by_id = {e["id"]: e for e in _registry()["entries"]}

    def get(eid):
        if eid not in by_id:
            raise RuntimeError(
                f"engine parameter {eid} missing from assumptions.json; "
                "run data-pipeline/register_engine_params.py")
        return by_id[eid]

    eps_id = f"GLOBAL-import-demand-elasticity-{variant}"
    if variant == "central" and iso3:
        country_eps = f"{iso3}-import-demand-elasticity-central"
        if country_eps in by_id:
            eps_id = country_eps

    ids = {
        "eps": eps_id,
        "eta": f"GLOBAL-own-price-demand-elasticity-{variant}",
        "retaliation_share": "GLOBAL-retaliation-share",
        "retaliation_top_n": "GLOBAL-retaliation-top-sectors",
        "fiscal_multiplier": f"GLOBAL-fiscal-multiplier-{variant}",
    }
    values = {k: get(eid)["value"] for k, eid in ids.items()}
    return EngineParams(
        eps=float(values["eps"]),
        eta=float(values["eta"]),
        retaliation_share=float(values["retaliation_share"]),
        retaliation_top_n=int(values["retaliation_top_n"]),
        fiscal_multiplier=float(values["fiscal_multiplier"]),
        entry_ids=list(ids.values()),
    )


# --------------------------------------------------------------------
# demand-shock builders (all return 14-vectors in USD million)
# --------------------------------------------------------------------

def _sector_index(cd: CountryData, sector: str) -> int:
    try:
        return cd.sectors.index(sector)
    except ValueError:
        raise KeyError(f"unknown sector '{sector}'; valid: {cd.sectors}")


def price_effects(cd: CountryData, tariffs: dict, p: EngineParams) -> np.ndarray:
    """Fractional producer-price rises dp from imported-input cost push:
    dp' = dp_m' A_m (I - A_d)^-1."""
    dp_m = np.zeros(len(cd.sectors))
    for s, t in tariffs.items():
        dp_m[_sector_index(cd, s)] = t
    return cd.L_I.T @ (cd.A_m.T @ dp_m)


def tariff_substitution_dF(cd, tariffs, p):
    dF = np.zeros(len(cd.sectors))
    for s, t in tariffs.items():
        i = _sector_index(cd, s)
        cut_share = min(abs(p.eps) * t, 1)  # import reduction, capped
        dF[i] += cut_share * cd.imports_by_product[i] * cd.domestic_absorption[i]
    return dF


def tariff_downstream_dF(cd, tariffs, p):
    dp = price_effects(cd, tariffs, p)
    f_base = (cd.fd["households"] + cd.fd["government"] + cd.fd["gfcf"]
              + cd.fd["exports"])
    return -abs(p.eta) * dp * f_base


def tariff_real_income_dF(cd, tariffs, p):
    dp = price_effects(cd, tariffs, p)
    hh_dom = cd.fd["households"]
    hh_imp = cd.fd_imported["households"]
    hh_total = float(hh_dom.sum() + hh_imp.sum())
    pidx = float((hh_dom / hh_total) @ dp)
    for s, t in tariffs.items():
        i = _sector_index(cd, s)
        pidx += t * float(hh_imp[i]) / hh_total
    loss = pidx * hh_total
    return -loss * hh_dom / float(hh_dom.sum())


def tariff_retaliation_dF(cd, tariffs, p):
    if not tariffs:
        return np.zeros(len(cd.sectors))
    weights = np.array([cd.imports_by_product[_sector_index(cd, s)]
                        for s in tariffs])
    rates = np.array(list(tariffs.values()))
    t_bar = float(rates @ weights / weights.sum()) if weights.sum() > 0 \
        else float(rates.mean())
    dF = np.zeros(len(cd.sectors))
    top = np.argsort(cd.fd["exports"])[-p.retaliation_top_n:]
    dF[top] = -t_bar * p.retaliation_share * cd.fd["exports"][top]
    return dF


def sector_support_dF(cd, support: dict):
    dF = np.zeros(len(cd.sectors))
    for s, rate in support.items():
        i = _sector_index(cd, s)
        dF[i] += rate * cd.x[i]
    return dF


def financing_drag_dF(cd, total_spending: float):
    hh = cd.fd["households"]
    return -total_spending * hh / float(hh.sum())


def stimulus_dF(cd, rate_of_gdp: float, p: EngineParams):
    amount = rate_of_gdp * cd.gdp
    hh = cd.fd["households"]
    return p.fiscal_multiplier * amount * hh / float(hh.sum())


# --------------------------------------------------------------------
# decomposition and scenario runner
# --------------------------------------------------------------------

def decompose(cd: CountryData, dF: np.ndarray, include_type_ii: bool) -> dict:
    n = len(cd.sectors)
    direct = cd.e * dF
    indirect = cd.e * ((cd.L_I - np.eye(n)) @ dF)
    if include_type_ii:
        induced = cd.e * ((cd.L_II - cd.L_I) @ dF)
        L = cd.L_II
    else:
        induced = np.zeros(n)
        L = cd.L_I
    dx = L @ dF
    with np.errstate(divide="ignore", invalid="ignore"):
        va_coeff = np.where(cd.x > 0, cd.va / cd.x, 0)
    return {
        "direct": direct,
        "indirect": indirect,
        "induced": induced,
        "total": direct + indirect + induced,
        "dx": dx,
        "dva": va_coeff * dx,
    }


def _channel_dFs(cd, p, tariffs, sector_support, sme_stimulus,
                 include_retaliation, include_financing_drag):
    channels = {}
    if tariffs:
        channels["tariff_substitution"] = tariff_substitution_dF(cd, tariffs, p)
        channels["tariff_downstream"] = tariff_downstream_dF(cd, tariffs, p)
        channels["tariff_real_income"] = tariff_real_income_dF(cd, tariffs, p)
        if include_retaliation:
            channels["tariff_retaliation"] = tariff_retaliation_dF(
                cd, tariffs, p)
    if sector_support:
        channels["sector_support"] = sector_support_dF(cd, sector_support)
        if include_financing_drag:
            total = float(sum(rate * cd.x[_sector_index(cd, s)]
                              for s, rate in sector_support.items()))
            channels["financing_drag"] = financing_drag_dF(cd, total)
    if sme_stimulus > 0:
        channels["sme_stimulus"] = stimulus_dF(cd, sme_stimulus, p)
    return channels


def run_scenario(iso3: str, tariffs: dict | None = None,
                 sector_support: dict | None = None,
                 sme_stimulus: float = 0,
                 include_type_ii: bool = False,
                 include_retaliation: bool = False,
                 include_financing_drag: bool = True) -> dict:
    """All rates are fractions; returns USD million / persons."""
    cd = load_country(iso3)
    tariffs = tariffs or {}
    sector_support = sector_support or {}

    p = load_params("central", iso3)
    channels = _channel_dFs(cd, p, tariffs, sector_support, sme_stimulus,
                            include_retaliation, include_financing_drag)
    dF = sum(channels.values(), np.zeros(len(cd.sectors)))
    main = decompose(cd, dF, include_type_ii)

    channel_jobs = {
        name: {
            "jobs": float(decompose(cd, cdF, include_type_ii)["total"].sum()),
            "demand_usd_million": float(cdF.sum()),
        }
        for name, cdF in channels.items()
    }

    # uncertainty: corner evaluations over parameter variants
    totals = [float(main["total"].sum())]
    for variant in ("low", "high"):
        pv = load_params(variant, iso3)
        chv = _channel_dFs(cd, pv, tariffs, sector_support, sme_stimulus,
                           include_retaliation, include_financing_drag)
        dFv = sum(chv.values(), np.zeros(len(cd.sectors)))
        totals.append(float(decompose(cd, dFv, include_type_ii)["total"].sum()))

    # costs
    revenue = float(sum(
        t * cd.imports_by_product[_sector_index(cd, s)]
        * (1 - min(abs(p.eps) * t, 1))
        for s, t in tariffs.items()))
    spending = float(sum(rate * cd.x[_sector_index(cd, s)]
                         for s, rate in sector_support.items()))
    spending += sme_stimulus * cd.gdp
    total_jobs = float(main["total"].sum())

    baseline_emp = cd.baseline_employment
    meta = cd.metadata
    return {
        "country": iso3,
        "sectors": cd.sectors,
        "aggregate": {
            "direct_jobs": float(main["direct"].sum()),
            "indirect_jobs": float(main["indirect"].sum()),
            "induced_jobs": (float(main["induced"].sum())
                             if include_type_ii else None),
            "total_jobs": total_jobs,
            "total_jobs_low": min(totals),
            "total_jobs_high": max(totals),
            # fraction; the API layer converts to percent
            "share_of_baseline_employment": total_jobs / baseline_emp,
        },
        "baseline": {
            "sector_sum_employment_persons": baseline_emp,
            "reference_year": meta["reference_year"],
            "note": ("denominator = sector-sum employment (TiM, "
                     "national-accounts concept); ILOSTAT LFS total "
                     "differs (see country metadata)"),
        },
        "sector_effects": [
            {
                "sector": s,
                "direct_jobs": float(main["direct"][k]),
                "indirect_jobs": float(main["indirect"][k]),
                "induced_jobs": (float(main["induced"][k])
                                 if include_type_ii else None),
                "total_jobs": float(main["total"][k]),
                "output_change_usd_million": float(main["dx"][k]),
                "value_added_change_usd_million": float(main["dva"][k]),
            }
            for k, s in enumerate(cd.sectors)
        ],
        "tariff_channels": ({
            "protected_sector_gain": channel_jobs.get("tariff_substitution"),
            "downstream_cost": channel_jobs.get("tariff_downstream"),
            "real_income_loss": channel_jobs.get("tariff_real_income"),
            "retaliation": channel_jobs.get("tariff_retaliation"),
        } if tariffs else None),
        "other_channels": {k: v for k, v in channel_jobs.items()
                           if not k.startswith("tariff_")} or None,
        "costs": {
            "tariff_revenue_usd_million": revenue,
            "spending_cost_usd_million": spending,
            "net_fiscal_usd_million": revenue - spending,
            # USD million per job; the API layer converts to USD
            "cost_per_job_fiscal_usd_million":
                (spending / total_jobs
                 if spending > 0 and total_jobs > 0 else None),
            "financing_drag_included": bool(include_financing_drag
                                            and sector_support),
        },
        "induced_note": ("upper-bound illustration of induced effects "
                         "(the household closure caps the consumption "
                         "propensity at 1); the sign of small net "
                         "results can flip under this closure"
                         if include_type_ii else None),
        "uncertainty": {
            "low": min(totals),
            "high": max(totals),
            "basis": "parameter range (elasticities, fiscal multiplier) "
                     "from the assumptions registry; not a statistical "
                     "confidence interval",
        },
        "data_source": {
            "citation": (f"OECD ICIO {meta['icio_edition']}, year "
                         f"{meta['reference_year']}; employment: "
                         f"{meta['employment_source']}"),
            "reference_year": meta["reference_year"],
            "notes": "; ".join(meta.get("notes", [])),
        },
        "assumptions_used": p.entry_ids,
    }


def employment_multipliers(iso3: str) -> dict:
    """direct / type_1 / type_2 jobs per USD million of final demand."""
    cd = load_country(iso3)
    m1 = cd.e @ cd.L_I
    m2 = cd.e @ cd.L_II
    return {
        s: {
            "direct": float(cd.e[k]),
            "indirect": float(m1[k] - cd.e[k]),
            "induced": float(m2[k] - m1[k]),
            "type_1": float(m1[k]),
            "type_2": float(m2[k]),
        }
        for k, s in enumerate(cd.sectors)
    }
