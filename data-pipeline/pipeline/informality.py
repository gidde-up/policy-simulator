"""Informal-employment shares by didactic sector, per country.

Source: ILOSTAT EMP_NIFL_SEX_ECO_NB_A (informal employment by economic
activity, thousands) over EMP_TEMP_SEX_ECO_NB_A (total employment, same
classification and year). share = informal / total.

Granularity differs by country (discovered by
probe_ilostat_informality.py, 2026-06-12):
  - VNM, THA, SEN: ISIC Rev.4 sections, year 2022
  - TUN: ISIC Rev.4 sections, year 2019 (latest available)
  - ZAF: ILOSTAT broad aggregate groups only (AGR/MAN/CON/MEL/MKT/PUB);
    every sector inherits its group's rate (registered per cell)

Mappings are committed concordances:
  - ISIC4 sections -> 14 sectors: reuses ISIC1_TO_SECTOR
    (pipeline/ilostat.py). Sectors fed by several sections aggregate
    properly (sum informal / sum total). The five manufacturing-family
    sectors inherit section C's rate (1-digit data cannot split C);
    one registry entry per inherited cell.
  - ECO_AGGREGATE groups -> 14 sectors: AGGREGATE_TO_SECTORS below;
    every cell is an inheritance (registered).

Where a section/group has no data: share = None -> the UI hides the
informality block content for that sector; nothing is imputed.
"""
import csv

import config
from pipeline import download, ilostat
from pipeline.errors import PipelineError

INFORMAL_INDICATOR = "EMP_NIFL_SEX_ECO_NB_A"
TOTAL_INDICATOR = config.ILOSTAT_EMP_BY_ACTIVITY  # EMP_TEMP_SEX_ECO_NB_A
NATIONAL_RATE_INDICATORS = ["EMP_NIFL_SEX_RT_A", "SDG_0831_SEX_ECO_RT_A"]
WORKING_POVERTY_INDICATOR = "SDG_0111_SEX_AGE_RT_A"

MANUFACTURING_FAMILY = ["manufacturing", "textiles", "automotive",
                        "food_processing", "chemicals"]

# committed concordance: ILOSTAT broad aggregate groups -> didactic
# sectors (used only where ISIC4 sections are unavailable, e.g. ZAF).
# Group definitions per ILOSTAT: AGR agriculture; MAN manufacturing;
# CON construction; MEL mining, energy and utilities; MKT market
# services; PUB public/non-market services.
AGGREGATE_TO_SECTORS = {
    "AGR": ["agriculture"],
    "MEL": ["mining", "utilities"],
    "MAN": MANUFACTURING_FAMILY,
    "CON": ["construction"],
    "MKT": ["trade", "transport", "finance", "other_services"],
    "PUB": ["public_services"],
}


def _rows(indicator, iso3, timefrom="2015"):
    path = download.fetch_ilostat(indicator, iso3,
                                  params={"sex": "SEX_T",
                                          "timefrom": timefrom})
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _values_by_year(rows, prefix):
    """{year: {classif_code_without_prefix: value}} for SEX_T rows."""
    out = {}
    for r in rows:
        c1 = r.get("classif1", "")
        if not c1.startswith(prefix):
            continue
        if r.get("sex") not in ("SEX_T", "", None):
            continue
        try:
            year = int(r["time"])
            val = float(r["obs_value"])
        except (KeyError, ValueError):
            continue
        out.setdefault(year, {})[c1.replace(prefix, "")] = val
    return out


def _pick_year(years):
    if not years:
        return None
    return min(years, key=lambda y: (abs(y - config.REFERENCE_YEAR), -y))


def build_country_informality(iso3: str):
    """Returns (block_dict, registry_cells) or (None, []) if no usable
    sector-level data exists.

    registry_cells: list of (sector, share, basis) for every cell whose
    value is INHERITED rather than directly observed/aggregated.
    """
    informal_rows = _rows(INFORMAL_INDICATOR, iso3)
    total_rows = _rows(TOTAL_INDICATOR, iso3)

    # try ISIC4 sections first
    inf4 = _values_by_year(informal_rows, "ECO_ISIC4_")
    tot4 = _values_by_year(total_rows, "ECO_ISIC4_")
    years4 = [y for y in inf4 if y in tot4
              and any(len(k) == 1 and k.isalpha() for k in inf4[y])]
    if years4:
        year = _pick_year(years4)
        return _build_from_isic4(iso3, inf4[year], tot4[year], year)

    # fall back to broad aggregate groups (e.g. ZAF)
    infA = _values_by_year(informal_rows, "ECO_AGGREGATE_")
    totA = _values_by_year(total_rows, "ECO_AGGREGATE_")
    yearsA = [y for y in infA if y in totA]
    if yearsA:
        year = _pick_year(yearsA)
        return _build_from_aggregate(iso3, infA[year], totA[year], year)

    return None, []


def _share(inf, tot, keys):
    """Aggregated share over the given classification keys; None when
    either side lacks all keys or the denominator is zero."""
    i = sum(inf[k] for k in keys if k in inf)
    t = sum(tot[k] for k in keys if k in tot)
    have_i = any(k in inf for k in keys)
    have_t = any(k in tot for k in keys)
    if not (have_i and have_t) or t <= 0:
        return None
    return round(min(i / t, 1.0), 4)


def _build_from_isic4(iso3, inf, tot, year):
    # sections feeding each sector, from the committed 1-digit concordance
    sections_by_sector: dict[str, list[str]] = {}
    for sec, sector in ilostat.ISIC1_TO_SECTOR.items():
        if sector == "_manufacturing_group":
            continue  # section C handled via family inheritance below
        sections_by_sector.setdefault(sector, []).append(sec)

    shares = {}
    cells = []
    observed = sorted(set(inf) & set(tot))
    for sector, secs in sections_by_sector.items():
        shares[sector] = _share(inf, tot, secs)
    c_share = _share(inf, tot, ["C"])
    for sector in MANUFACTURING_FAMILY:
        shares[sector] = c_share
        if c_share is not None:
            cells.append((sector, c_share,
                          f"inherited from ISIC Rev.4 section C "
                          f"(1-digit data cannot split manufacturing), "
                          f"{INFORMAL_INDICATOR}, year {year}"))

    block = {
        "indicator": INFORMAL_INDICATOR,
        "denominator_indicator": TOTAL_INDICATOR,
        "classification": "ISIC Rev.4 sections",
        "year_used": year,
        "informal_share_of_employment": {s: shares.get(s)
                                         for s in config.SECTORS_14},
        "coverage": {"classifs_observed": observed},
        "manufacturing_family_inherited_from_section_C": c_share is not None,
    }
    return block, cells


def _build_from_aggregate(iso3, inf, tot, year):
    shares = {}
    cells = []
    observed = sorted(set(inf) & set(tot))
    for group, sectors in AGGREGATE_TO_SECTORS.items():
        g_share = _share(inf, tot, [group])
        for sector in sectors:
            shares[sector] = g_share
            if g_share is not None:
                cells.append((sector, g_share,
                              f"inherited from ILOSTAT broad aggregate "
                              f"group {group} (no ISIC4 section detail "
                              f"published for {iso3}), "
                              f"{INFORMAL_INDICATOR}, year {year}"))

    block = {
        "indicator": INFORMAL_INDICATOR,
        "denominator_indicator": TOTAL_INDICATOR,
        "classification": "ILOSTAT broad aggregate groups "
                          "(AGR/MAN/CON/MEL/MKT/PUB)",
        "year_used": year,
        "informal_share_of_employment": {s: shares.get(s)
                                         for s in config.SECTORS_14},
        "coverage": {"classifs_observed": observed},
        "manufacturing_family_inherited_from_section_C": False,
    }
    return block, cells


def national_context(iso3: str):
    """National informality rate and working-poverty rate (context
    indicators only; never used in simulation arithmetic)."""
    ctx = {"note": "context indicators only; not used in simulation "
                   "arithmetic"}

    for ind in NATIONAL_RATE_INDICATORS:
        try:
            rows = _rows(ind, iso3)
        except PipelineError:
            continue
        # prefer an explicit total classif when present
        by_year = {}
        for r in rows:
            if r.get("sex") not in ("SEX_T", "", None):
                continue
            c1 = r.get("classif1", "") or ""
            if c1 and not c1.endswith("TOTAL"):
                continue
            try:
                by_year[int(r["time"])] = float(r["obs_value"])
            except (KeyError, ValueError):
                continue
        if by_year:
            year = _pick_year(list(by_year))
            ctx["national_informal_employment_rate_pct"] = round(
                by_year[year], 1)
            ctx["national_informality_year"] = year
            ctx["national_informality_indicator"] = ind
            break

    try:
        rows = _rows(WORKING_POVERTY_INDICATOR, iso3)
        by_year = {}
        for r in rows:
            if r.get("sex") not in ("SEX_T", "", None):
                continue
            c1 = r.get("classif1", "") or ""
            if "YGE15" not in c1 and "TOTAL" not in c1:
                continue
            try:
                by_year[int(r["time"])] = float(r["obs_value"])
            except (KeyError, ValueError):
                continue
        if by_year:
            year = _pick_year(list(by_year))
            ctx["working_poverty_rate_pct"] = round(by_year[year], 1)
            ctx["working_poverty_year"] = year
            ctx["working_poverty_indicator"] = WORKING_POVERTY_INDICATOR
    except PipelineError:
        pass

    return ctx
