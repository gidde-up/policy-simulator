"""Wage cross-check (E.1 item 6).

Reports the internal, IO-consistent compensation per worker by sector
(TiM compensation of employees / TiM employment, from the country
JSONs) and attempts to cross-check it against ILOSTAT mean nominal
earnings by economic activity. The ILOSTAT earnings-by-activity
indicators (EAR_4MTH_SEX_ECO_*) are NOT served by the rplumber bulk API
(HTTP 400, verified 2026-06-13), so the external comparison could not be
run programmatically; the internal figures are reported for
transparency and the documented modelling choice stands: the model uses
the internal TiM-based compensation figures, for consistency with the
input-output accounts.

Writes reports/wage_crosscheck.md.
"""
import json
import sys

import httpx

import config

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
EARNINGS_INDICATOR = "EAR_4MTH_SEX_ECO_CUR_NB_A"


def ilostat_earnings_available(iso3: str) -> tuple[bool, int]:
    url = (f"{config.ILOSTAT_BASE}?id={EARNINGS_INDICATOR}"
           f"&ref_area={iso3}&format=.csv&timefrom=2018")
    try:
        with httpx.Client(timeout=60, headers={"User-Agent": UA}) as c:
            r = c.get(url)
        return (r.status_code == 200 and len(r.content) > 200,
                r.status_code)
    except httpx.HTTPError:
        return False, 0


def main():
    lines = [
        "# Wage cross-check (internal TiM vs ILOSTAT earnings)",
        "",
        "Internal compensation per worker = TiM compensation of employees "
        "/ TiM employment, by sector, from the verified country JSONs "
        "(USD thousand per worker per year, current 2022 USD).",
        "",
    ]

    # external availability probe
    lines.append("## ILOSTAT earnings-by-activity availability")
    lines.append("")
    any_available = False
    for iso3 in config.COUNTRIES:
        ok, status = ilostat_earnings_available(iso3)
        any_available = any_available or ok
        lines.append(f"- {iso3}: {EARNINGS_INDICATOR} -> "
                     f"{'available' if ok else f'NOT available (HTTP {status})'}")
    lines += [
        "",
        "The ILOSTAT mean-earnings-by-economic-activity series is not "
        "retrievable through the rplumber bulk API for these countries "
        "(HTTP 400). The programmatic external cross-check could not be "
        "performed; the internal figures below are reported for "
        "transparency.",
        "",
        "## Internal compensation per worker by sector (USD thousand/year)",
        "",
        "| sector | " + " | ".join(config.COUNTRIES) + " |",
        "|" + "---|" * (len(config.COUNTRIES) + 1),
    ]

    internal = {}
    for iso3 in config.COUNTRIES:
        d = json.loads((config.OUTPUT_DIR / f"{iso3}.json").read_text(
            encoding="utf-8"))
        comp = d["type_ii"]["compensation_of_employees"]   # USD million
        persons = d["employment"]["persons"]
        # USD million / persons = USD million per person; *1000 -> USD
        # thousand per person
        internal[iso3] = [
            (comp[k] / persons[k] * (10 ** 3)) if persons[k] > 0 else None
            for k in range(len(config.SECTORS_14))
        ]

    for k, sector in enumerate(config.SECTORS_14):
        row = [f"{internal[iso3][k]:.1f}" if internal[iso3][k] is not None
               else "n/a" for iso3 in config.COUNTRIES]
        lines.append(f"| {sector} | " + " | ".join(row) + " |")

    lines += [
        "",
        "## Conclusion",
        "",
        "The model uses the internal TiM-based compensation figures "
        "shown above. They are, by construction, consistent with the "
        "OECD ICIO value-added accounts that drive every other model "
        "quantity; an ILOSTAT labour-force-survey earnings series would "
        "introduce a different statistical concept (gross monthly "
        "earnings of employees, survey-based, excluding employers' "
        "social contributions and the self-employed). For an "
        "accounting-consistent input-output simulator, IO consistency is "
        "the correct priority. This choice is documented here and in the "
        "methodology.",
        "",
    ]

    out = config.REPORTS_DIR / "wage_crosscheck.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written: {out}")
    print(f"ILOSTAT earnings available for any country: {any_available}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
