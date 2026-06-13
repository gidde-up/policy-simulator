"""Discovers which ILOSTAT informality indicator exists per country.

Tried in order (first id with usable per-section rows wins, recorded in
sources.lock.json by the fetch helper and printed here for the record):
  1. IFL_4IEM_SEX_ECO_NB_A   (informality database family, per spec)
  2. EMP_NIFL_SEX_ECO_NB_A   (legacy: informal employment by activity)
plus context indicators (national rates):
  - informality rate candidates (national, no sector detail needed)
  - SDG 1.1.1 working poverty rate

Read-only probe: prints what exists; the registration/JSON writing is
done by add_informality.py after human review of this output.
"""
import csv
import sys

import config
from pipeline import download
from pipeline.errors import PipelineError

SECTOR_CANDIDATES = ["IFL_4IEM_SEX_ECO_NB_A", "EMP_NIFL_SEX_ECO_NB_A"]
NATIONAL_RATE_CANDIDATES = ["IFL_4IEM_SEX_RT_A", "EMP_NIFL_SEX_RT_A",
                            "SDG_0831_SEX_ECO_RT_A"]
WORKING_POVERTY_CANDIDATES = ["SDG_0111_SEX_AGE_RT_A"]


def probe(indicator, iso3, params=None):
    try:
        path = download.fetch_ilostat(indicator, iso3, params=params)
    except PipelineError:
        return None
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return rows or None


def summarise_sector_rows(rows):
    by_year = {}
    for r in rows:
        c1 = r.get("classif1", "")
        if r.get("sex") not in ("SEX_T", "", None):
            continue
        try:
            year = int(r["time"])
            float(r["obs_value"])
        except (KeyError, ValueError):
            continue
        by_year.setdefault(year, set()).add(c1)
    return by_year


def main():
    print("=== sector-level informal employment ===")
    for iso3 in config.COUNTRIES:
        found = False
        for ind in SECTOR_CANDIDATES:
            rows = probe(ind, iso3, params={"sex": "SEX_T",
                                            "timefrom": "2015"})
            if not rows:
                continue
            by_year = summarise_sector_rows(rows)
            isic4 = {y: sorted(c for c in cs if "ISIC4" in c)
                     for y, cs in by_year.items()}
            years_with_isic4 = [y for y, cs in isic4.items() if cs]
            if not years_with_isic4:
                print(f"  {iso3} {ind}: rows but no ISIC4 sections "
                      f"(classifs: {sorted(set().union(*by_year.values()))[:8]})")
                continue
            best = min(years_with_isic4,
                       key=lambda y: (abs(y - config.REFERENCE_YEAR), -y))
            print(f"  {iso3} {ind}: years {sorted(years_with_isic4)}; "
                  f"best {best} with {len(isic4[best])} ISIC4 classifs")
            found = True
            break
        if not found:
            print(f"  {iso3}: NO sector-level informality indicator found")

    print("\n=== national informality rate ===")
    for iso3 in config.COUNTRIES:
        for ind in NATIONAL_RATE_CANDIDATES:
            rows = probe(ind, iso3, params={"sex": "SEX_T",
                                            "timefrom": "2015"})
            if rows:
                years = sorted({r["time"] for r in rows
                                if r.get("obs_value")})
                print(f"  {iso3} {ind}: years {years[-5:]}")
                break
        else:
            print(f"  {iso3}: NO national informality rate found")

    print("\n=== working poverty rate (SDG 1.1.1) ===")
    for iso3 in config.COUNTRIES:
        for ind in WORKING_POVERTY_CANDIDATES:
            rows = probe(ind, iso3, params={"sex": "SEX_T",
                                            "timefrom": "2015"})
            if rows:
                years = sorted({r["time"] for r in rows
                                if r.get("obs_value")})
                print(f"  {iso3} {ind}: years {years[-5:]}")
                break
        else:
            print(f"  {iso3}: NO working poverty rate found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
