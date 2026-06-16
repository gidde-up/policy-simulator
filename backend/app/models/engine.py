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
    # Miyazawa household closure (optional; absent in toy fixtures).
    # consumption column h_c and labour-income row h_r; used by
    # DirectEmployment shocks to recycle programme wage bills through
    # the Type II inverse.
    consumption_coefficients: np.ndarray = None
    labour_income_coefficients: np.ndarray = None
    # informal employment share by sector (None where the country has no
    # ILOSTAT informality data; np.nan for individual unobserved sectors)
    informal_share: np.ndarray = None
    informality_meta: dict = None

    @classmethod
    def from_dict(cls, d: dict) -> "CountryData":
        def arr(v):
            return np.asarray(v, dtype=float)
        t2 = d.get("type_ii") or {}
        cc = t2.get("consumption_coefficients")
        li = t2.get("labour_income_coefficients")
        inf_block = d.get("informality")
        inf_share = None
        if inf_block:
            shares = inf_block["informal_share_of_employment"]
            inf_share = np.array(
                [shares.get(s) if shares.get(s) is not None else np.nan
                 for s in d["sectors"]], dtype=float)
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
            consumption_coefficients=arr(cc) if cc is not None else None,
            labour_income_coefficients=arr(li) if li is not None else None,
            informal_share=inf_share,
            informality_meta=({k: inf_block[k]
                               for k in ("indicator", "year_used",
                                         "classification")}
                              if inf_block else None),
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
    # extension (Session F) parameters; default 0 so v1 paths are
    # unaffected and the regression lock holds
    export_supply: float = 0.0    # export supply elasticity (positive)
    redundancy: float = 0.0       # investment-incentive redundancy share
    eiip_labour_share: float = 0.0  # labour-based infrastructure labour share
    mpc: float = 1.0              # marginal propensity to consume (financing)


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

    # extension parameters: present only after Session E registration;
    # optional so a v1-era registry still loads (defaults 0)
    ext_ids = {
        "export_supply": f"GLOBAL-export-supply-elasticity-{variant}",
        "redundancy": f"GLOBAL-investment-incentive-redundancy-{variant}",
        "eiip_labour_share": f"GLOBAL-eiip-labour-cost-share-{variant}",
        "mpc": f"GLOBAL-marginal-propensity-to-consume-{variant}",
    }
    # NOTE: ext ids are deliberately NOT added to entry_ids -- only the
    # levers actually used add their assumptions to the response
    # (run_scenario does this), so old-lever scenarios keep their exact
    # v1 assumptions_used list and the regression lock holds.
    ext = {eid_k: (float(by_id[eid]["value"]) if eid in by_id else 0.0)
           for eid_k, eid in ext_ids.items()}

    return EngineParams(
        eps=float(values["eps"]),
        eta=float(values["eta"]),
        retaliation_share=float(values["retaliation_share"]),
        retaliation_top_n=int(values["retaliation_top_n"]),
        fiscal_multiplier=float(values["fiscal_multiplier"]),
        entry_ids=list(ids.values()),
        export_supply=ext["export_supply"],
        redundancy=ext["redundancy"],
        eiip_labour_share=ext["eiip_labour_share"],
        # absent MPC (pre-J registry) -> 1.0 = full crowding out = v1.1.0
        mpc=ext["mpc"] if ext["mpc"] else 1.0,
    )


# --------------------------------------------------------------------
# demand-shock builders (all return 14-vectors in USD million)
# --------------------------------------------------------------------

def _sector_index(cd: CountryData, sector: str) -> int:
    try:
        return cd.sectors.index(sector)
    except ValueError:
        raise KeyError(f"unknown sector '{sector}'; valid: {cd.sectors}")


# --- generalised price-and-demand primitives ------------------------
# Shared by every price-side lever (tariffs, and the Session F
# production/wage subsidies and depreciation). The Leontief cost
# identity p' = p' A_d + c' gives, for any unit-cost change dc,
#   dp = (I - A_d)^-1' dc = L_I' dc.

def _cost_push_prices(cd: CountryData, dc: np.ndarray) -> np.ndarray:
    """Fractional producer-price change from a unit-cost change dc."""
    return cd.L_I.T @ dc


def _downstream_base(cd: CountryData) -> np.ndarray:
    """Final demand exposed to producer-price changes: households,
    government, GFCF and exports (NOT inventories)."""
    return (cd.fd["households"] + cd.fd["government"] + cd.fd["gfcf"]
            + cd.fd["exports"])


def _downstream_dF(cd: CountryData, p: EngineParams,
                   dp: np.ndarray) -> np.ndarray:
    """Demand response to a producer-price change via the compensated
    own-price elasticity (negative for a price rise, positive for a
    cost cut)."""
    return -abs(p.eta) * dp * _downstream_base(cd)


def _hh_spread(cd: CountryData, amount: float) -> np.ndarray:
    """Spread a household demand change across the domestic household
    consumption vector."""
    hh = cd.fd["households"]
    return amount * hh / float(hh.sum())


def _real_income_dF(cd: CountryData, dp: np.ndarray,
                    dp_import_final: np.ndarray) -> np.ndarray:
    """Household demand change from the consumer price index move: the
    cost-push on domestic goods plus the direct price change on
    imported final goods, spread over domestic consumption."""
    hh_dom = cd.fd["households"]
    hh_imp = cd.fd_imported["households"]
    hh_total = float(hh_dom.sum() + hh_imp.sum())
    pidx = float((hh_dom / hh_total) @ dp)
    pidx += float((hh_imp / hh_total) @ dp_import_final)
    loss = pidx * hh_total
    return _hh_spread(cd, -loss)


def _tariff_dp_m(cd: CountryData, tariffs: dict) -> np.ndarray:
    """Imported-input price rise vector from tariff rates."""
    dp_m = np.zeros(len(cd.sectors))
    for s, t in tariffs.items():
        dp_m[_sector_index(cd, s)] = t
    return dp_m


def price_effects(cd: CountryData, tariffs: dict, p: EngineParams) -> np.ndarray:
    """Fractional producer-price rises dp from imported-input cost push:
    dp' = dp_m' A_m (I - A_d)^-1."""
    return _cost_push_prices(cd, cd.A_m.T @ _tariff_dp_m(cd, tariffs))


def tariff_substitution_dF(cd, tariffs, p):
    dF = np.zeros(len(cd.sectors))
    for s, t in tariffs.items():
        i = _sector_index(cd, s)
        cut_share = min(abs(p.eps) * t, 1)  # import reduction, capped
        dF[i] += cut_share * cd.imports_by_product[i] * cd.domestic_absorption[i]
    return dF


def tariff_downstream_dF(cd, tariffs, p):
    return _downstream_dF(cd, p, price_effects(cd, tariffs, p))


def tariff_real_income_dF(cd, tariffs, p):
    return _real_income_dF(cd, price_effects(cd, tariffs, p),
                           _tariff_dp_m(cd, tariffs))


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


def stimulus_dF(cd, rate_of_gdp: float, p: EngineParams = None):
    """Household-transfer stimulus (v1.2): the transfer is spent on the
    household consumption basket, with the basket's import content as
    leakage. Saving leakage is handled symmetrically on the financing
    side (the tax-financing MPC), so there is no separate first-round
    fiscal multiplier (the v1.1.0 0.5 factor is deprecated)."""
    return _compose_with_leakage(cd, rate_of_gdp * cd.gdp, "household")


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


def _va_coeff(cd: CountryData) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(cd.x > 0, cd.va / cd.x, 0)


def _aggregate(cd: CountryData, channels: dict, direct_employment: list,
               include_type_ii: bool) -> dict:
    """Sum the demand channels, decompose, then layer in programme
    employment: jobs enter directly (no output-route indirect effect),
    and when Type II is on their wage bill is recycled through the
    household closure as consumption (e * L_II * h_c * W). With no
    direct employment the result equals decompose() exactly (the v1
    path -- the regression lock depends on this)."""
    n = len(cd.sectors)
    dF = sum(channels.values(), np.zeros(n))
    dec = decompose(cd, dF, include_type_ii)
    direct = dec["direct"].copy()
    indirect = dec["indirect"].copy()
    induced = dec["induced"].copy()
    dx = dec["dx"].copy()
    dva = dec["dva"].copy()
    va_coeff = _va_coeff(cd)

    direct_channels: dict = {}
    for de in direct_employment:
        i = _sector_index(cd, de.sector)
        direct[i] += de.jobs
        ch_jobs = de.jobs
        if include_type_ii:
            if cd.consumption_coefficients is None:
                raise ValueError(
                    "Type II requested but the country has no Miyazawa "
                    "consumption_coefficients (no type_ii block)")
            dF_w = cd.consumption_coefficients * de.wage_bill
            induced_w = cd.e * (cd.L_II @ dF_w)
            induced += induced_w
            dxw = cd.L_II @ dF_w
            dx += dxw
            dva += va_coeff * dxw
            ch_jobs += float(induced_w.sum())
        direct_channels[de.channel] = (
            direct_channels.get(de.channel, 0.0) + ch_jobs)

    return {
        "channels": channels,
        "direct_employment_channels": direct_channels,
        "direct": direct,
        "indirect": indirect,
        "induced": induced,
        "total": direct + indirect + induced,
        "dx": dx,
        "dva": dva,
    }


def evaluate_scenario(cd: CountryData, p: EngineParams, shocks: list,
                      include_type_ii: bool,
                      include_financing_drag: bool = True) -> dict:
    """General shock-list evaluator (used by the DirectEmployment
    tests). Returns aggregate decomposition vectors plus the channels."""
    channels, direct_employment = _evaluate_channel_dFs(
        cd, p, shocks, include_financing_drag)
    return _aggregate(cd, channels, direct_employment, include_type_ii)


# --------------------------------------------------------------------
# composable typed shocks
#
# Every lever compiles to a list of typed shocks; one evaluator turns
# them into per-channel final-demand vectors (and, for programme
# employment, direct jobs that bypass the output-employment route).
# The v1 levers re-expressed this way reproduce their original numbers
# (regression-locked); Session F levers reuse the same path.
# --------------------------------------------------------------------

@dataclass
class DemandShock:
    """A final-demand change (USD million), already computed."""
    vector: np.ndarray
    channel: str


@dataclass
class ImportPriceShock:
    """A fractional import-price rise by product, propagated through the
    domestic cost structure into downstream and real-income responses."""
    dp_m: np.ndarray
    channel_downstream: str
    channel_real_income: str
    dp_import_final: np.ndarray   # direct price change on imported final goods


@dataclass
class DomesticCostShock:
    """A fractional unit-cost change by origin sector (e.g. a production
    subsidy dc[j] = -s, or a wage subsidy dc[j] = -w*labour_share_j),
    propagated through the same price model."""
    dc: np.ndarray
    channel_downstream: str
    channel_real_income: str


@dataclass
class DirectEmployment:
    """Programme jobs created outside the output-employment coefficient
    route (public works wage component, direct public hiring)."""
    jobs: float
    wage_bill: float              # USD million
    sector: str
    channel: str


@dataclass
class FiscalCost:
    """Spending that accumulates into costs and, when drag_eligible,
    into the tax-financing drag on household consumption."""
    amount: float                 # USD million
    drag_eligible: bool


def _evaluate_channel_dFs(cd, p, shocks, drag_factor):
    """Single evaluation pass over a shock list, in emission order.
    `drag_factor` is the financing withdrawal per unit of fiscal cost:
    0 (deficit), MPC (tax-financed), or 1 (full crowding-out). The
    financing-drag channel is reserved at the first drag-eligible
    FiscalCost so its dict position matches the v1 channel order.
    (A boolean True/False still works: True -> 1.0, False -> 0.0.)"""
    n = len(cd.sectors)
    channels: dict = {}
    drag_total = 0.0
    drag_reserved = False
    direct_employment: list = []

    def add(channel, vec):
        channels[channel] = (channels[channel] + vec
                             if channel in channels else vec)

    for s in shocks:
        if isinstance(s, DemandShock):
            add(s.channel, s.vector)
        elif isinstance(s, ImportPriceShock):
            dp = _cost_push_prices(cd, cd.A_m.T @ s.dp_m)
            add(s.channel_downstream, _downstream_dF(cd, p, dp))
            add(s.channel_real_income,
                _real_income_dF(cd, dp, s.dp_import_final))
        elif isinstance(s, DomesticCostShock):
            dp = _cost_push_prices(cd, s.dc)
            add(s.channel_downstream, _downstream_dF(cd, p, dp))
            add(s.channel_real_income,
                _real_income_dF(cd, dp, np.zeros(n)))
        elif isinstance(s, FiscalCost):
            if s.drag_eligible and drag_factor:
                drag_total += s.amount
                if not drag_reserved:
                    channels["financing_drag"] = np.zeros(n)  # reserve slot
                    drag_reserved = True
        elif isinstance(s, DirectEmployment):
            direct_employment.append(s)

    if drag_reserved:
        channels["financing_drag"] = financing_drag_dF(
            cd, drag_total * drag_factor)
    return channels, direct_employment


def compile_tariffs(cd, p, tariffs, include_retaliation):
    shocks = [DemandShock(tariff_substitution_dF(cd, tariffs, p),
                          "tariff_substitution")]
    dp_m = _tariff_dp_m(cd, tariffs)
    shocks.append(ImportPriceShock(dp_m, "tariff_downstream",
                                   "tariff_real_income", dp_m))
    if include_retaliation:
        shocks.append(DemandShock(tariff_retaliation_dF(cd, tariffs, p),
                                  "tariff_retaliation"))
    return shocks


def compile_sector_support(cd, support):
    total = float(sum(rate * cd.x[_sector_index(cd, s)]
                      for s, rate in support.items()))
    return [DemandShock(sector_support_dF(cd, support), "sector_support"),
            FiscalCost(total, drag_eligible=True)]


def compile_stimulus(cd, p, rate_of_gdp):
    return compile_stimulus_variant(cd, p, rate_of_gdp, "household")


# --------------------------------------------------------------------
# extension levers (Session F)
# --------------------------------------------------------------------

def _normalised(vec: np.ndarray) -> np.ndarray:
    s = float(vec.sum())
    return vec / s if s > 0 else vec * 0


def _compose_domestic(cd, amount: float, v_dom: np.ndarray) -> np.ndarray:
    """Distribute `amount` across a domestic final-demand vector's
    product composition (no import leakage)."""
    return amount * _normalised(v_dom)


def _compose_with_leakage(cd, amount: float, choice: str) -> np.ndarray:
    """Distribute `amount` like a baseline demand vector; the imported
    share of that vector leaks abroad (only the domestic part hits
    domestic producers)."""
    vecs = {"government": ("government",), "investment": ("gfcf",),
            "household": ("households",)}
    key = vecs[choice][0]
    v_dom = cd.fd[key]
    v_imp = cd.fd_imported.get(key, np.zeros(len(cd.sectors)))
    total = float(v_dom.sum() + v_imp.sum())
    return amount * v_dom / total if total > 0 else v_dom * 0


def _require_labour_coeffs(cd):
    if cd.labour_income_coefficients is None:
        raise ValueError("lever needs labour_income_coefficients "
                         "(no type_ii block in the country data)")
    return cd.labour_income_coefficients


def compile_public_investment(cd, amount, target=None):
    """Public investment: allocate by the domestic GFCF composition, or
    fully into a target sector. Fiscal cost = the injection (drag on)."""
    if target:
        dF = np.zeros(len(cd.sectors))
        dF[_sector_index(cd, target)] = amount
    else:
        dF = _compose_domestic(cd, amount, cd.fd["gfcf"])
    return [DemandShock(dF, "public_investment"),
            FiscalCost(amount, drag_eligible=True)]


def compile_stimulus_variant(cd, p, rate_of_gdp, target):
    """Stimulus with a composition choice. Household transfer keeps the
    Batini first-round multiplier; government/investment purchases enter
    at full value with the chosen vector's import share as leakage."""
    amount = rate_of_gdp * cd.gdp
    if target == "household":
        dF = stimulus_dF(cd, rate_of_gdp, p)
    else:
        dF = _compose_with_leakage(cd, amount, target)
    # symmetric financing (v1.2): the stimulus is subject to the chosen
    # financing mode like every other fiscal lever -- it is no longer
    # costless to finance
    return [DemandShock(dF, "sme_stimulus"),
            FiscalCost(amount, drag_eligible=True)]


def compile_production_subsidy(cd, subsidies):
    """Subsidy rate s on sector j: unit-cost cut dc[j] = -s, propagated
    through the price model (downstream demand gain + real-income gain).
    Fiscal cost = s x baseline output (drag on)."""
    dc = np.zeros(len(cd.sectors))
    fiscal = 0.0
    for s, rate in subsidies.items():
        i = _sector_index(cd, s)
        dc[i] += -rate
        fiscal += rate * cd.x[i]
    return [DomesticCostShock(dc, "production_subsidy_downstream",
                              "production_subsidy_real_income"),
            FiscalCost(fiscal, drag_eligible=True)]


def compile_wage_subsidy(cd, subsidies):
    """Subsidy rate w on sector j's labour costs: dc[j] = -w x labour
    share (compensation/output). Fiscal cost = w x wage bill (drag on).
    Excluded by construction: hiring responses beyond the demand
    channel, displacement, deadweight (see docs/levers)."""
    h_r = _require_labour_coeffs(cd)
    dc = np.zeros(len(cd.sectors))
    fiscal = 0.0
    for s, rate in subsidies.items():
        i = _sector_index(cd, s)
        dc[i] += -rate * float(h_r[i])
        fiscal += rate * float(h_r[i]) * cd.x[i]   # w x wage bill
    return [DomesticCostShock(dc, "wage_subsidy_downstream",
                              "wage_subsidy_real_income"),
            FiscalCost(fiscal, drag_eligible=True)]


def compile_public_works(cd, p, budget, method):
    """Public works: budget split into a labour-based wage component
    (direct job-years) and a materials component (construction input
    column). Labour share from EIIP (labour-based) or the country's own
    construction labour share (conventional)."""
    i = _sector_index(cd, "construction")
    h_r = _require_labour_coeffs(cd)
    lam = (p.eiip_labour_share if method == "labour_based"
           else float(h_r[i]))
    wage_bill = lam * budget
    comp_i = float(h_r[i]) * cd.x[i]                # construction wage bill
    comp_per_worker = comp_i / cd.employment[i]
    direct_jobs = wage_bill / comp_per_worker
    materials = (1 - lam) * budget
    materials_dF = materials * _normalised(cd.A_d[:, i])
    return [DirectEmployment(direct_jobs, wage_bill, "construction",
                             "public_works_direct"),
            DemandShock(materials_dF, "public_works_materials"),
            FiscalCost(budget, drag_eligible=True)]


def compile_direct_public_employment(cd, budget):
    """Government hiring in public services: wage component (direct jobs
    + Type II income recycling) plus a non-wage operating component on
    the public-services input column. Fiscal cost = full budget."""
    i = _sector_index(cd, "public_services")
    h_r = _require_labour_coeffs(cd)
    wage_share = float(h_r[i])
    wage_bill = wage_share * budget
    comp_i = wage_share * cd.x[i]
    comp_per_worker = comp_i / cd.employment[i]
    direct_jobs = wage_bill / comp_per_worker
    operating = (1 - wage_share) * budget
    operating_dF = operating * _normalised(cd.A_d[:, i])
    return [DirectEmployment(direct_jobs, wage_bill, "public_services",
                             "direct_public_employment"),
            DemandShock(operating_dF, "direct_public_employment_operating"),
            FiscalCost(budget, drag_eligible=True)]


def compile_depreciation(cd, p, d):
    """Stylised depreciation rate d: all imported prices rise by d
    (downstream cost + real-income loss); exports expand by the export
    supply elasticity x d. No fiscal cost; no forced net sign."""
    n = len(cd.sectors)
    dp_m = np.full(n, float(d))
    dF_exports = p.export_supply * d * cd.fd["exports"]
    return [ImportPriceShock(dp_m, "depreciation_downstream",
                             "depreciation_real_income", dp_m),
            DemandShock(dF_exports, "depreciation_exports")]


def _compile_scenario(cd, p, tariffs, sector_support, sme_stimulus,
                      include_retaliation):
    """v1 levers as a shock list, emitted in the v1 channel order."""
    shocks = []
    if tariffs:
        shocks += compile_tariffs(cd, p, tariffs, include_retaliation)
    if sector_support:
        shocks += compile_sector_support(cd, sector_support)
    if sme_stimulus > 0:
        shocks += compile_stimulus(cd, p, sme_stimulus)
    return shocks


def _scenario_channels(cd, p, tariffs, sector_support, sme_stimulus,
                       include_retaliation, include_financing_drag):
    """The v1 channel dict, now produced via the shock pipeline."""
    shocks = _compile_scenario(cd, p, tariffs, sector_support,
                               sme_stimulus, include_retaliation)
    channels, _ = _evaluate_channel_dFs(cd, p, shocks,
                                        include_financing_drag)
    return channels


def _tax_incentive_breakdown(cd, p, iti):
    """gross / additional / windfall investment from a tax incentive of
    fiscal cost X at intensity s, with redundancy share r."""
    X = iti["fiscal_cost_pct_gdp"] * cd.gdp
    gross = X / iti["intensity"]
    additional = (1 - p.redundancy) * gross
    windfall = p.redundancy * gross
    return X, gross, additional, windfall


def _compile_all(cd, p, tariffs, sector_support, sme_stimulus,
                 include_retaliation, ext):
    """Full lever set: v1 levers first (in v1 order, so old-only
    scenarios are byte-identical to _compile_scenario), then the
    Session F extension levers."""
    shocks = []
    if tariffs:
        shocks += compile_tariffs(cd, p, tariffs, include_retaliation)
    if sector_support:
        shocks += compile_sector_support(cd, sector_support)
    if sme_stimulus > 0:
        shocks += compile_stimulus_variant(
            cd, p, sme_stimulus, ext.get("stimulus_target", "household"))

    pi = ext.get("public_investment")
    if pi and pi.get("amount_pct_gdp", 0) > 0:
        shocks += compile_public_investment(
            cd, pi["amount_pct_gdp"] * cd.gdp, pi.get("target"))
    ps = ext.get("production_subsidy")
    if ps:
        shocks += compile_production_subsidy(cd, ps)
    ws = ext.get("wage_subsidy")
    if ws:
        shocks += compile_wage_subsidy(cd, ws)
    iti = ext.get("investment_tax_incentive")
    if iti and iti.get("fiscal_cost_pct_gdp", 0) > 0:
        X, gross, additional, _ = _tax_incentive_breakdown(cd, p, iti)
        if iti.get("target"):
            dF = np.zeros(len(cd.sectors))
            dF[_sector_index(cd, iti["target"])] = additional
        else:
            dF = _compose_domestic(cd, additional, cd.fd["gfcf"])
        shocks += [DemandShock(dF, "investment_incentive"),
                   FiscalCost(X, drag_eligible=True)]
    pw = ext.get("public_works")
    if pw and pw.get("budget_pct_gdp", 0) > 0:
        shocks += compile_public_works(
            cd, p, pw["budget_pct_gdp"] * cd.gdp,
            pw.get("method", "labour_based"))
    dpe = ext.get("direct_public_employment")
    if dpe and dpe.get("budget_pct_gdp", 0) > 0:
        shocks += compile_direct_public_employment(
            cd, dpe["budget_pct_gdp"] * cd.gdp)
    dep = ext.get("depreciation", 0) or 0
    if dep > 0:
        shocks += compile_depreciation(cd, p, dep)
    return shocks


# parameter-registry ids each extension lever relies on (appended to
# assumptions_used only when the lever is active, so v1 scenarios keep
# their exact assumptions list)
_LEVER_ASSUMPTIONS = {
    "production_subsidy": ["GLOBAL-own-price-demand-elasticity-central"],
    "wage_subsidy": ["GLOBAL-own-price-demand-elasticity-central"],
    "investment_tax_incentive":
        ["GLOBAL-investment-incentive-redundancy-central"],
    "depreciation": ["GLOBAL-export-supply-elasticity-central",
                     "GLOBAL-own-price-demand-elasticity-central"],
}


_FINANCING_MODES = ("deficit", "tax_financed", "full_crowding_out")


def _resolve_financing(p, financing_mode, include_financing_drag):
    """Returns (mode, drag_factor, deprecated_used). The financing
    withdrawal per unit of fiscal cost is 0 (deficit), MPC (tax-financed)
    or 1 (full crowding-out). The old boolean is a deprecated alias."""
    deprecated = False
    if include_financing_drag is not None:
        deprecated = True
        mode = "full_crowding_out" if include_financing_drag else "deficit"
    else:
        mode = financing_mode
    if mode not in _FINANCING_MODES:
        raise ValueError(f"financing_mode must be one of {_FINANCING_MODES}")
    factor = {"deficit": 0.0, "tax_financed": p.mpc,
              "full_crowding_out": 1.0}[mode]
    return mode, factor, deprecated


def run_scenario(iso3: str, tariffs: dict | None = None,
                 sector_support: dict | None = None,
                 sme_stimulus: float = 0,
                 include_type_ii: bool = False,
                 include_retaliation: bool = False,
                 financing_mode: str = "tax_financed",
                 include_financing_drag: bool | None = None,
                 extensions: dict | None = None) -> dict:
    """All rates are fractions; returns USD million / persons.

    `financing_mode` (deficit | tax_financed | full_crowding_out;
    default tax_financed) chooses the financing withdrawal. The legacy
    `include_financing_drag` boolean is a deprecated alias
    (True -> full_crowding_out, False -> deficit). `extensions` carries
    the Session F levers; with default financing_mode=full_crowding_out
    and no extensions the result reproduces the v1.0.0 contract.
    """
    cd = load_country(iso3)
    tariffs = tariffs or {}
    sector_support = sector_support or {}
    ext = extensions or {}

    p = load_params("central", iso3)
    mode, drag_factor, deprecated_used = _resolve_financing(
        p, financing_mode, include_financing_drag)
    shocks = _compile_all(cd, p, tariffs, sector_support, sme_stimulus,
                          include_retaliation, ext)
    channels, direct_employment = _evaluate_channel_dFs(
        cd, p, shocks, drag_factor)
    main = _aggregate(cd, channels, direct_employment, include_type_ii)

    channel_jobs = {
        name: {
            "jobs": float(decompose(cd, cdF, include_type_ii)["total"].sum()),
            "demand_usd_million": float(cdF.sum()),
        }
        for name, cdF in channels.items()
    }
    for ch, jobs in main["direct_employment_channels"].items():
        wage = float(sum(de.wage_bill for de in direct_employment
                         if de.channel == ch))
        channel_jobs[ch] = {"jobs": float(jobs), "demand_usd_million": wage}

    # uncertainty: corner evaluations over parameter variants
    totals = [float(main["total"].sum())]
    for variant in ("low", "high"):
        pv = load_params(variant, iso3)
        _, drag_v, _ = _resolve_financing(pv, financing_mode,
                                          include_financing_drag)
        shv = _compile_all(cd, pv, tariffs, sector_support, sme_stimulus,
                           include_retaliation, ext)
        chv, dev = _evaluate_channel_dFs(cd, pv, shv, drag_v)
        aggv = _aggregate(cd, chv, dev, include_type_ii)
        totals.append(float(aggv["total"].sum()))

    # costs
    revenue = float(sum(
        t * cd.imports_by_product[_sector_index(cd, s)]
        * (1 - min(abs(p.eps) * t, 1))
        for s, t in tariffs.items()))
    spending = float(sum(s.amount for s in shocks
                         if isinstance(s, FiscalCost)))
    total_jobs = float(main["total"].sum())

    # --- financing object (gross before financing / net after) -------
    drag_eligible_cost = float(sum(s.amount for s in shocks
                                   if isinstance(s, FiscalCost)
                                   and s.drag_eligible))
    drag_channel = channel_jobs.get("financing_drag")
    financing_offset_jobs = float(drag_channel["jobs"]) if drag_channel else 0.0
    financing_withdrawal = drag_eligible_cost * drag_factor
    gross_jobs_before = total_jobs - financing_offset_jobs
    dx_net = float(main["dx"].sum())
    drag_dx = (float(decompose(cd, channels["financing_drag"],
                               include_type_ii)["dx"].sum())
               if "financing_drag" in channels else 0.0)
    mpc_central = load_params("central", iso3).mpc
    financing = {
        "mode": mode,
        "label": {"deficit": "Deficit-financed, no immediate offset",
                  "tax_financed": "Tax-financed, MPC-scaled offset",
                  "full_crowding_out": "Full crowding-out upper bound"}[mode],
        "fiscal_cost_usd_million": drag_eligible_cost,
        "financing_withdrawal_usd_million": financing_withdrawal,
        "financing_mpc": (mpc_central if mode == "tax_financed" else None),
        "financing_mpc_source": (
            "GLOBAL-marginal-propensity-to-consume-central (stylised "
            "developing-economy central; Haavelmo 1945 framing)"
            if mode == "tax_financed" else None),
        "financing_mpc_status": ("literature_based"
                                 if mode == "tax_financed" else None),
        "household_consumption_vector_source":
            "OECD ICIO 2025 household final demand (HFCE+NPISH)",
        "financing_offset_jobs": financing_offset_jobs,
        "financing_offset_output": drag_dx,
        "caveat": ("the offset is scaled by the marginal propensity to "
                   "consume; it is a simplified static assumption and "
                   "does not model fiscal sustainability, interest rates, "
                   "expectations, debt dynamics or tax incidence"
                   if mode == "tax_financed" else
                   ("gross demand effect before any financing offset"
                    if mode == "deficit" else
                    "deliberately strong upper bound: every unit of "
                    "fiscal cost reduces household consumption one for one")),
        "deprecated_input_used": deprecated_used,
    }

    baseline_emp = cd.baseline_employment
    meta = cd.metadata
    resp = {
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
            "gross_jobs_before_financing": gross_jobs_before,
            "net_jobs_after_financing": total_jobs,
            "financing_offset_jobs": financing_offset_jobs,
        },
        "financing": financing,
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
            "financing_drag_included": "financing_drag" in channels,
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
        "assumptions_used": _assumptions_used(p, ext),
    }

    # extension-only response keys (absent for v1 scenarios, so the
    # regression lock's key-set check is unaffected)
    iti = ext.get("investment_tax_incentive")
    if iti and iti.get("fiscal_cost_pct_gdp", 0) > 0:
        X, gross, additional, windfall = _tax_incentive_breakdown(cd, p, iti)
        resp["investment_incentive"] = {
            "fiscal_cost_usd_million": float(X),
            "gross_investment_usd_million": float(gross),
            "additional_investment_usd_million": float(additional),
            "windfall_usd_million": float(windfall),
            "redundancy_share": float(p.redundancy),
            "note": "the windfall is investment that would have occurred "
                    "anyway (redundancy); only the additional investment "
                    "creates demand",
        }
    if (ext.get("public_works", {}).get("budget_pct_gdp", 0) > 0
            or ext.get("direct_public_employment", {}).get(
                "budget_pct_gdp", 0) > 0):
        resp["job_years_note"] = (
            "programme jobs are reported as JOB-YEARS, not permanent "
            "posts; one job-year is one person employed for one year")
        resp["employment_programme_note"] = (
            "Public employment programmes (EIIP / EPWP-style) are an "
            "intervention on a different plane from the other levers. They "
            "create temporary job-years, not permanent posts, usually at "
            "low or stipend-level pay and outside standard employment "
            "relations. Their cost-per-job and headline job count are "
            "therefore NOT comparable with permanent-job levers - it is "
            "apples to oranges. The model also assumes constant returns, so "
            "it does not capture the project-pipeline, institutional and "
            "fiscal limits that make large marginal expansion difficult "
            "where such a programme already operates at scale (for example "
            "South Africa's EPWP). The job-quality figures use host-sector "
            "averages and so overstate the actual pay and conditions of "
            "programme work.")
    return resp


def _assumptions_used(p, ext: dict) -> list:
    used = list(p.entry_ids)
    for lever, ids in _LEVER_ASSUMPTIONS.items():
        active = ext.get(lever)
        if active:
            for i in ids:
                if i not in used:
                    used.append(i)
    return used


def job_quality(iso3: str, result: dict) -> dict:
    """Composition indicators of a scenario's job change. Every figure
    describes the MIX of the jobs gained/lost, on the assumption that
    created/lost jobs mirror each sector's existing characteristics --
    NOT a quality forecast. Computed from the scenario's sector effects,
    so it is a pure post-processing of run_scenario (which is therefore
    left untouched, and its regression lock unaffected)."""
    cd = load_country(iso3)
    dE = np.array([se["total_jobs"] for se in result["sector_effects"]])
    dx = np.array([se["output_change_usd_million"]
                   for se in result["sector_effects"]])

    # comp per worker by sector (USD million / person) and economy mean
    comp = (cd.labour_income_coefficients * cd.x
            if cd.labour_income_coefficients is not None
            else _va_coeff(cd) * cd.x)        # fallback: VA per worker
    with np.errstate(divide="ignore", invalid="ignore"):
        comp_per_worker = np.where(cd.employment > 0,
                                   comp / cd.employment, 0.0)
    economy_comp_per_worker = float(comp.sum() / cd.employment.sum())

    # (a) wage-bill effect: dW = compensation coefficient . dx
    h_r = (cd.labour_income_coefficients
           if cd.labour_income_coefficients is not None else _va_coeff(cd))
    wage_bill_change = float(h_r @ dx)

    # (b) average compensation of the net jobs moved, vs economy mean
    abs_w = np.abs(dE)
    denom = float(abs_w.sum())
    if denom > 0:
        avg_comp = float((abs_w @ comp_per_worker) / denom)
        comp_ratio = avg_comp / economy_comp_per_worker \
            if economy_comp_per_worker > 0 else None
    else:
        avg_comp, comp_ratio = None, None

    wage = {
        "wage_bill_change_usd_million": wage_bill_change,
        "avg_compensation_ratio_vs_economy": comp_ratio,
        "caveat": "created/lost jobs are assumed to share each sector's "
                  "existing average compensation; this is the wage mix of "
                  "the change, not a wage forecast",
    }

    # informality composition (gated: hidden where no data)
    informality = None
    if cd.informal_share is not None and denom > 0:
        mask = ~np.isnan(cd.informal_share)
        w = abs_w[mask]
        if float(w.sum()) > 0:
            share = float((w @ cd.informal_share[mask]) / w.sum())
            informality = {
                "informal_share_of_change": share,
                "indicator": cd.informality_meta.get("indicator"),
                "year": cd.informality_meta.get("year_used"),
                "caveat": "share of the jobs moved that fall in activities "
                          "where employment is predominantly informal "
                          "(sector-mix basis); not a prediction that these "
                          "specific jobs are informal",
            }

    # --- gained vs lost profiles (Workstream G) ---------------------
    # weights are the per-sector gains (positive dE) and losses (|negative
    # dE|). Each profile reports its own weighted average compensation and
    # informality. Missing informality sectors are excluded (never zero),
    # and a coverage fraction is reported.
    def _profile(weights):
        total = float(weights.sum())
        if total <= 0:
            return {
                "total_jobs": total,
                "avg_compensation_usd_million": None,
                "avg_compensation_ratio_vs_economy": None,
                "informal_share": None,
                "informality_coverage": None,
                "informality_note": "not applicable (no jobs in this group)",
            }
        avg_c = float((weights @ comp_per_worker) / total)
        ratio = (avg_c / economy_comp_per_worker
                 if economy_comp_per_worker > 0 else None)
        inf_share, coverage, note = None, None, "no informality data for this country"
        if cd.informal_share is not None:
            m = ~np.isnan(cd.informal_share)
            wc = weights[m]
            covered = float(wc.sum())
            if covered > 0:
                inf_share = float((wc @ cd.informal_share[m]) / covered)
                coverage = covered / total
                note = ("share of this group in predominantly-informal "
                        "activities, over the sectors that have informality "
                        "data (see coverage)")
            else:
                note = "no informality data for the sectors in this group"
        return {
            "total_jobs": total,
            "avg_compensation_usd_million": avg_c,
            "avg_compensation_ratio_vs_economy": ratio,
            "informal_share": inf_share,
            "informality_coverage": coverage,
            "informality_note": note,
        }

    gained = _profile(np.where(dE > 0, dE, 0.0))
    lost = _profile(np.where(dE < 0, -dE, 0.0))

    return {
        "wage": wage,
        "informality": informality,
        "gained": gained,
        "lost": lost,
        "net_composition_note": "the wage-bill and informality figures above "
                                "are net/compositional indicators of the whole "
                                "change, not the quality of newly created jobs",
        "caveat": "These indicators describe the sectoral composition of "
                  "simulated employment changes. They do not predict the wage, "
                  "contract status, or informality status of individual workers.",
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
