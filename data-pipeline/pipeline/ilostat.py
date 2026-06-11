"""ILOSTAT bulk API client and parsing.

Used for: (a) per-cell fallback when TiM employment is missing,
(b) the national employment cross-check, (c) labour force baseline.
Values in ILOSTAT are reported in thousands of persons.

ISIC Rev.4 1-digit sections are mapped to the 14 didactic sectors by the
documented classification below. Section C (manufacturing) cannot be
split at 1-digit level; the within-manufacturing allocation is handled in
employment.py (by ICIO gross-output shares, registered per cell).
"""
import csv

import config
from pipeline.errors import PipelineError
from pipeline import download

# Classification judgement (a mapping, not a number), documented here and
# in the registry whenever it is used for a substituted cell.
ISIC1_TO_SECTOR = {
    "A": "agriculture",
    "B": "mining",
    "C": "_manufacturing_group",   # split downstream by ICIO output shares
    "D": "utilities",
    "E": "utilities",
    "F": "construction",
    "G": "trade",
    "H": "transport",
    "I": "other_services",         # accommodation & food
    "J": "other_services",         # information & communication
    "K": "finance",
    "L": "other_services",         # real estate
    "M": "other_services",
    "N": "other_services",
    "O": "public_services",
    "P": "public_services",
    "Q": "public_services",
    "R": "other_services",
    "S": "other_services",
    "T": "other_services",         # household employers
    "U": "other_services",         # extraterritorial
    "X": "other_services",         # not elsewhere classified
}


def _read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        yield from csv.DictReader(f)


def _latest_year_rows(rows, want_classif_prefix, year_target):
    """Pick the year closest to year_target with data; prefer <= splits."""
    by_year = {}
    for r in rows:
        c1 = r.get("classif1", "")
        if not c1.startswith(want_classif_prefix):
            continue
        if r.get("sex") not in ("SEX_T", "", None):
            continue
        try:
            year = int(r["time"])
            val = float(r["obs_value"])
        except (KeyError, ValueError):
            continue
        by_year.setdefault(year, {})[c1] = val
    if not by_year:
        return None, {}
    year = min(by_year.keys(), key=lambda y: (abs(y - year_target), -y))
    return year, by_year[year]


def employment_by_activity(country: str, year_target: int):
    """Employment by ISIC Rev.4 1-digit section, thousands of persons.

    Returns (year_used, {section_letter: thousands}).
    """
    path = download.fetch_ilostat(config.ILOSTAT_EMP_BY_ACTIVITY, country,
                                  params={"sex": "SEX_T",
                                          "timefrom": str(year_target - 4)})
    rows = list(_read_rows(path))
    year, data = _latest_year_rows(rows, "ECO_ISIC4_", year_target)
    if year is None:
        raise PipelineError(
            stage=f"ilostat.employment_by_activity[{country}]",
            expected="ISIC Rev.4 employment by activity",
            found="no ECO_ISIC4_* rows",
            location=str(path),
            action="Check indicator availability; do not substitute.",
        )
    sections = {}
    for c1, val in data.items():
        code = c1.replace("ECO_ISIC4_", "")
        if code == "TOTAL":
            sections["TOTAL"] = val
        elif len(code) == 1 and code.isalpha():
            sections[code] = val
    return year, sections


def national_employment(country: str, year_target: int):
    """Total employment (thousands) and the year it refers to.

    The TOTAL is classification-independent; some countries (e.g. ZAF)
    report activity detail in ISIC Rev.3 only, so the total is accepted
    from ISIC4, ISIC3 or the aggregate classification, in that order.
    """
    path = download.fetch_ilostat(config.ILOSTAT_EMP_BY_ACTIVITY, country,
                                  params={"sex": "SEX_T",
                                          "timefrom": str(year_target - 4)})
    rows = list(_read_rows(path))
    for prefix in ("ECO_ISIC4_", "ECO_ISIC3_", "ECO_AGGREGATE_"):
        year, data = _latest_year_rows(rows, prefix, year_target)
        total = (data or {}).get(f"{prefix}TOTAL")
        if year is not None and total and total > 0:
            return year, total
    raise PipelineError(
        stage=f"ilostat.national_employment[{country}]",
        expected="a TOTAL employment row in any activity classification",
        found="none with positive value",
        location=str(path),
        action="Check ILOSTAT data; do not substitute.",
    )


def labour_force(country: str, year_target: int):
    """Labour force (thousands) and the year it refers to."""
    path = download.fetch_ilostat(config.ILOSTAT_LABOUR_FORCE, country,
                                  params={"sex": "SEX_T",
                                          "timefrom": str(year_target - 4)})
    rows = list(_read_rows(path))
    by_year = {}
    for r in rows:
        c1 = r.get("classif1", "")
        # total aggregate age band
        if c1 not in ("AGE_AGGREGATE_TOTAL", "AGE_YTHADULT_YGE15"):
            continue
        if r.get("sex") not in ("SEX_T", "", None):
            continue
        try:
            year = int(r["time"])
            val = float(r["obs_value"])
        except (KeyError, ValueError):
            continue
        # prefer AGE_AGGREGATE_TOTAL when both exist
        prefer = by_year.get(year)
        if prefer is None or c1 == "AGE_AGGREGATE_TOTAL":
            by_year[year] = val
    if not by_year:
        raise PipelineError(
            stage=f"ilostat.labour_force[{country}]",
            expected="labour force total",
            found="no usable rows",
            location=str(path),
            action="Check indicator availability.",
        )
    year = min(by_year.keys(), key=lambda y: (abs(y - year_target), -y))
    return year, by_year[year]
