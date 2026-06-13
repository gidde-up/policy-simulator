"""Registers the extension (Sessions E-H) behavioural parameters that
are NOT import-demand elasticities (those stay in
register_engine_params.py). Idempotent per (country, scope/field).

Implemented this session (sources in hand):
  - GLOBAL-eiip-labour-cost-share-{central,low,high}: labour content of
    labour-based infrastructure, from the ILO EIIP literature.
  - {ISO3}-conventional-construction-labour-share: DATA-DERIVED from
    each country JSON (construction compensation / output) -- the
    conventional-method counterpart for the public-works lever.

Pending (manual PDF downloads not yet in raw/ -- see
make_availability_matrix.py): Tokarick (2010) export demand
elasticities; investment-incentive redundancy share (James 2013;
IMF-OECD-UN-WB 2015). Their registration blocks run automatically once
the PDFs are present and the extraction scripts have been pointed at
them; until then those rows show PENDING in the availability matrix.
"""
import datetime
import json
import sys

import config
from pipeline import assumptions

TODAY = datetime.date.today().isoformat()

EIIP = ("ILO Employment Intensive Investment Programme, 'Green Works: "
        "Community and LRB Approaches' (wcms_619821), p.20: 'The labour "
        "content for the types of infrastructure works where "
        "labour-based approaches can be applied normally ranges between "
        "20-50% of the total investment cost' (the most labour-intensive "
        "public works programmes exceed 50%).")


def _eiip_entry(variant, value, basis):
    return assumptions.make_entry(
        entry_id=f"GLOBAL-eiip-labour-cost-share-{variant}",
        country=assumptions.GLOBAL_COUNTRY, scope="labour_content",
        sector="construction", field="eiip_labour_cost_share",
        icio_codes=[], value=value, unit="share",
        method="authored_constant", basis=basis,
        source={"dataset": "ILO EIIP literature", "url": "",
                "accessed": TODAY, "reference_period": "n/a"},
        citation=EIIP,
        notes="labour-based infrastructure method; the conventional "
              "method's labour share is data-derived per country "
              "({ISO3}-conventional-construction-labour-share)")


def eiip_entries():
    return [
        _eiip_entry("central", 0.35,
                    "midpoint of the ILO EIIP 20-50% labour-content range "
                    "for labour-based methods"),
        _eiip_entry("low", 0.20, "bottom of the ILO EIIP 20-50% range"),
        _eiip_entry("high", 0.50, "top of the ILO EIIP 20-50% range "
                                  "(labour-based; PWP can exceed this)"),
    ]


def conventional_construction_entries():
    """One DATA-DERIVED entry per country: construction-sector
    compensation of employees / gross output, read from the verified
    country JSON. No hand-typed numbers."""
    entries = []
    k = config.SECTORS_14.index("construction")
    for iso3 in config.COUNTRIES:
        path = config.OUTPUT_DIR / f"{iso3}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        comp = d["type_ii"]["compensation_of_employees"][k]
        x = d["x"][k]
        share = round(comp / x, 4)
        entries.append(assumptions.make_entry(
            entry_id=f"{iso3}-conventional-construction-labour-share",
            country=iso3, scope="labour_content", sector="construction",
            field="conventional_construction_labour_share",
            icio_codes=[], value=share, unit="share",
            method="data_derived",
            basis=f"construction-sector compensation of employees "
                  f"({comp:.1f}) / gross output ({x:.1f}) USD million, "
                  f"from {iso3}.json (OECD ICIO 2025 + TiM 2025)",
            source={"dataset": f"derived from backend/app/data/countries/"
                               f"{iso3}.json",
                    "url": config.ICIO_DATASET_PAGE,
                    "accessed": TODAY,
                    "reference_period": str(config.REFERENCE_YEAR)}))
    return entries


def main():
    registry = assumptions.load_registry()
    # GLOBAL EIIP labour share (replace the three variants)
    registry["entries"] = [
        e for e in registry["entries"]
        if not (e["country"] == assumptions.GLOBAL_COUNTRY
                and e.get("field") == "eiip_labour_cost_share")
    ] + eiip_entries()
    # per-country conventional construction labour share (data-derived)
    for e in conventional_construction_entries():
        registry["entries"] = [
            x for x in registry["entries"]
            if not (x["country"] == e["country"]
                    and x.get("field") == e["field"])
        ] + [e]
    assumptions.write_registry(registry)
    n_eiip = 3
    n_conv = len(config.COUNTRIES)
    print(f"registered {n_eiip} EIIP + {n_conv} conventional-construction "
          "labour-share entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
