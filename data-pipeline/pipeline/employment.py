"""Employment by ICIO industry from OECD TiM, with documented fallbacks.

Matching strategy per native ICIO industry code, in order:
  1. tim_exact      identical activity code in TiM (expected: both are
                    OECD STI/PIE 2025-vintage classifications)
  2. tim_child_sum  sum of finer TiM codes that exactly partition the
                    ICIO code's ISIC division range
  3. ilostat_residual  ILOSTAT 1-digit section total minus TiM-covered
                    industries of that section, allocated across missing
                    industries by ICIO gross-output shares
Every cell not obtained via (1) is recorded in the assumptions registry.
If a cell cannot be filled by any method, the pipeline stops.

Units: TiM EMPN obs are persons scaled by UNIT_MULT (10^3 = thousands);
converted to persons here. ILOSTAT values are thousands of persons.
"""
import csv
import re
from dataclasses import dataclass

import numpy as np

import config
from pipeline.errors import PipelineError
from pipeline import download, ilostat


@dataclass
class EmploymentCell:
    icio_code: str
    persons: float
    method: str          # tim_exact | tim_child_sum | ilostat_residual
    detail: str = ""


_CODE_RE = re.compile(r"^([A-Z])([0-9T_]*)([A-Z]?)$")


def parse_code(code: str):
    """Return (section_letter, frozenset(divisions)) for an activity code.

    'C10T12' -> ('C', {10,11,12}); 'A01_02' -> ('A', {1,2});
    'D' -> ('D', frozenset()) meaning the whole section.
    ISIC groups (3-digit, e.g. 'C301') and lettered subdivisions
    ('C24A') normalise to their 2-digit division ({30}, {24}); such
    sibling codes are disambiguated by the parent-residual stage.
    """
    m = _CODE_RE.match(code)
    if not m:
        return None
    section, rest, _suffix = m.groups()
    if not rest:
        return (section, frozenset())
    tokens = re.findall(r"([T_])?(\d+)", rest)
    divisions = set()
    prev = None
    for sep, num in tokens:
        n = int(num)
        if len(num) >= 3:
            n = int(num[:2])  # ISIC group -> parent division
        if sep == "T" and prev is not None:
            divisions.update(range(prev, n + 1))
        else:
            divisions.add(n)
        prev = n
    return (section, frozenset(divisions))


def fill_from_tim(tim: dict[str, float], industries: list[str],
                  x_native, prefix: str):
    """Stages 1-3 of the matching cascade, shared by EMPN and LABR.

    1. <prefix>_exact            identical code in TiM
    2. <prefix>_child_sum        finer TiM codes partition the target
    3. <prefix>_parent_residual  a coarser TiM code covers a sibling
       group (identical division signature, e.g. C24 covering C24A/C24B);
       the parent value minus already-filled siblings is allocated over
       missing siblings by native gross-output shares.

    Returns (values ndarray with NaN where unfilled, [EmploymentCell]).
    """
    import numpy as np

    values = np.full(len(industries), np.nan)
    cells: list[EmploymentCell] = []
    tim_parsed = {c: parse_code(c) for c in tim}

    # stage 1: exact
    for i, code in enumerate(industries):
        if code in tim:
            values[i] = tim[code]
            cells.append(EmploymentCell(code, tim[code], f"{prefix}_exact"))

    # stage 2: child-sum
    for i, code in enumerate(industries):
        if not np.isnan(values[i]):
            continue
        target = parse_code(code)
        if target is None or not target[1]:
            continue
        sec, divs = target
        parts = [(c, p) for c, p in tim_parsed.items()
                 if p and p[0] == sec and p[1] and p[1] < divs]
        covered, total, ok = set(), 0.0, True
        for c, p in parts:
            if p[1] & covered:
                ok = False
                break
            covered |= p[1]
            total += tim[c]
        if ok and covered == set(divs):
            values[i] = total
            cells.append(EmploymentCell(
                code, total, f"{prefix}_child_sum",
                detail=f"sum of {sorted(c for c, _ in parts)}"))

    # stage 3: parent-residual over sibling groups
    sig_groups: dict[tuple, list[int]] = {}
    for i, code in enumerate(industries):
        p = parse_code(code)
        if p and p[1]:
            sig_groups.setdefault((p[0], p[1]), []).append(i)
    for (sec, divs), members in sig_groups.items():
        missing = [i for i in members if np.isnan(values[i])]
        if not missing:
            continue
        # parent TiM code: the canonical string for this signature,
        # not string-equal to any member (no self-parenting)
        if len(divs) == 1:
            parent = f"{sec}{next(iter(divs)):02d}"
        else:
            lo, hi = min(divs), max(divs)
            parent = (f"{sec}{lo:02d}T{hi:02d}"
                      if divs == frozenset(range(lo, hi + 1)) else None)
        if (parent is None or parent not in tim
                or any(industries[i] == parent for i in members)):
            continue
        filled_sum = sum(values[i] for i in members if not np.isnan(values[i]))
        residual = tim[parent] - filled_sum
        x_missing = np.array([x_native[i] for i in missing])
        if residual < -max(1.0, 0.01 * abs(tim[parent])) or x_missing.sum() <= 0:
            continue
        residual = max(residual, 0.0)
        shares = x_missing / x_missing.sum()
        for share, i in zip(shares, missing):
            values[i] = residual * share
            cells.append(EmploymentCell(
                industries[i], float(values[i]), f"{prefix}_parent_residual",
                detail=(f"TiM {parent} minus filled siblings, allocated by "
                        f"ICIO output share {share:.3f}")))
    return values, cells


# unit handling per measure: accepted UNIT_MEASURE code and the target
# unit multiplier (EMPN -> persons (10^0); LABR -> USD million (10^6),
# matching ICIO valuation). Observations are scaled by
# 10^(UNIT_MULT - target_mult). Other unit measures (e.g. LABR as PT_VA,
# percentage of value added) are skipped.
MEASURE_UNITS = {
    "EMPN": ("PS", 0),
    "LABR": ("USD", 6),
}


def load_tim_csv(path, measure: str, country: str, year: int) -> dict[str, float]:
    """Parse a TiM SDMX csvfilewithlabels export -> {activity_code: persons
    (EMPN) or USD million (LABR)}."""
    if measure not in MEASURE_UNITS:
        raise PipelineError(
            stage="employment.load_tim",
            expected=f"measure in {sorted(MEASURE_UNITS)}",
            found=measure,
            action="Add explicit unit handling for the new measure.",
        )
    unit_code, target_mult = MEASURE_UNITS[measure]

    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        required = ["MEASURE", "REF_AREA", "ACTIVITY", "TIME_PERIOD",
                    "OBS_VALUE", "UNIT_MEASURE", "UNIT_MULT"]
        missing = [c for c in required if c not in fields]
        if missing:
            raise PipelineError(
                stage="employment.load_tim",
                expected=f"columns {required} in TiM CSV",
                found=f"missing {missing}; have {fields[:15]}...",
                location=str(path),
                action="Re-export with format=csvfilewithlabels.",
            )
        for r in reader:
            if r["MEASURE"] != measure or r["REF_AREA"] != country:
                continue
            if str(r["TIME_PERIOD"]) != str(year):
                continue
            if r["UNIT_MEASURE"] != unit_code:
                continue
            cp = r.get("COUNTERPART_AREA", "")
            if cp not in ("W", "WLD", "_T", ""):
                continue
            rows.append(r)

    if not rows:
        raise PipelineError(
            stage="employment.load_tim",
            expected=(f"{measure} rows in unit {unit_code} for {country}, "
                      f"{year} in TiM CSV"),
            found="none",
            location=str(path),
            action=("Check the SDMX export covers this country/measure/"
                    "year/unit; do not substitute."),
        )

    out = {}
    for r in rows:
        code = r["ACTIVITY"]
        try:
            val = float(r["OBS_VALUE"])
        except (ValueError, TypeError):
            continue  # empty cell in TiM
        if r.get("UNIT_MULT") in ("", None):
            raise PipelineError(
                stage="employment.load_tim",
                expected="UNIT_MULT present on every observation",
                found=f"empty for {code}",
                location=str(path),
                action="Unit scaling must be explicit; inspect the export.",
            )
        val *= 10.0 ** (int(float(r["UNIT_MULT"])) - target_mult)
        # duplicates (e.g. several counterpart codes): keep first, verify equal
        if code in out and abs(out[code] - val) > max(1.0, 0.001 * abs(val)):
            raise PipelineError(
                stage="employment.load_tim",
                expected=f"consistent duplicate observations for {code}",
                found=f"{out[code]} vs {val}",
                location=str(path),
                action="Inspect counterpart/unit dimensions in the export.",
            )
        out.setdefault(code, val)
    return out


def match_industries(tim: dict[str, float], industries: list[str],
                     x_native: np.ndarray, country: str, year: int,
                     ilostat_fallback: bool = True):
    """Fill employment for every native ICIO industry. Returns
    (persons ndarray, [EmploymentCell])."""
    persons, cells = fill_from_tim(tim, industries, x_native, "tim")

    missing_idx = [i for i in range(len(industries)) if np.isnan(persons[i])]
    if missing_idx and ilostat_fallback:
        ilo_year, sections = ilostat.employment_by_activity(country, year)
        # group missing industries by section
        by_section: dict[str, list[int]] = {}
        for i in missing_idx:
            p = parse_code(industries[i])
            if p is None:
                continue
            by_section.setdefault(p[0][0], []).append(i)
        for sec, idxs in by_section.items():
            if sec not in sections:
                continue
            sec_total_persons = sections[sec] * 1000.0
            # TiM-covered employment already assigned within this section
            covered = sum(
                persons[j] for j in range(len(industries))
                if not np.isnan(persons[j])
                and (parse_code(industries[j]) or ("?",))[0][0] == sec)
            residual = sec_total_persons - covered
            if residual <= 0:
                continue
            x_sec = np.array([x_native[i] for i in idxs])
            if x_sec.sum() <= 0:
                continue
            shares = x_sec / x_sec.sum()
            for share, i in zip(shares, idxs):
                persons[i] = residual * share
                cells.append(EmploymentCell(
                    industries[i], float(persons[i]), "ilostat_residual",
                    detail=(f"ILOSTAT {config.ILOSTAT_EMP_BY_ACTIVITY} "
                            f"section {sec} ({ilo_year}) minus TiM-covered, "
                            f"allocated by ICIO output share {share:.3f}")))

    still_missing = [industries[i] for i in range(len(industries))
                     if np.isnan(persons[i])]
    if still_missing:
        raise PipelineError(
            stage=f"employment.match[{country}]",
            expected="employment for every native ICIO industry",
            found=f"unfillable: {still_missing}",
            action=("No TiM match, no valid child-sum, no ILOSTAT residual. "
                    "Stop; do not substitute."),
        )
    return persons, cells


def build_employment(country: str, industries: list[str],
                     x_native: np.ndarray, S: np.ndarray, year: int):
    """Full employment block: native persons, 14-sector persons,
    coefficients, provenance cells, coverage stats."""
    tim_path = download.acquire_tim(config.TIM_MEASURE_EMPLOYMENT,
                                    ["ZAF", "TUN"], year)
    tim = load_tim_csv(tim_path, config.TIM_MEASURE_EMPLOYMENT, country, year)
    persons, cells = match_industries(tim, industries, x_native, country, year)

    e14 = S @ persons
    methods = {}
    for c in cells:
        methods[c.method] = methods.get(c.method, 0) + 1

    return {
        "persons_native": persons,
        "persons_14": e14,
        "cells": cells,
        "coverage": methods,
    }
