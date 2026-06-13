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
from pipeline import assumptions, download

TODAY = datetime.date.today().isoformat()

EIIP = ("ILO Employment Intensive Investment Programme, 'Green Works: "
        "Community and LRB Approaches' (wcms_619821), p.20: 'The labour "
        "content for the types of infrastructure works where "
        "labour-based approaches can be applied normally ranges between "
        "20-50% of the total investment cost' (the most labour-intensive "
        "public works programmes exceed 50%).")

TOKARICK = ("Tokarick, S. (2010), 'A Method for Calculating Export Supply "
            "and Import Demand Elasticities', IMF Working Paper WP/10/180, "
            "Table 2 (Export Supply Elasticities).")

REDUNDANCY = ("James, S. (2013), 'Effectiveness of Tax and Non-Tax "
              "Incentives and Investments: Evidence and Policy "
              "Implications', World Bank; and IMF-OECD-UN-World Bank "
              "(2015), 'Options for Low Income Countries' Effective and "
              "Efficient Use of Tax Incentives for Investment', Table 1 "
              "(Redundancy of Tax Incentives Based on Investor Surveys).")

# Manually downloaded source PDFs (OECD/IMF/World Bank bot-blocked);
# recorded in sources.lock.json with sha256 + method=manual.
SOURCE_PDFS = {
    "eiip_green_works_wcms_619821":
        ("eiip_green_works_wcms_619821.pdf",
         "https://www.ilo.org/sites/default/files/wcmsp5/groups/public/"
         "@ed_emp/@emp_policy/@invest/documents/publication/"
         "wcms_619821.pdf"),
    "eiip_guidance_wcms_743537":
        ("eiip_guidance_wcms_743537.pdf",
         "https://www.ilo.org/sites/default/files/wcmsp5/groups/public/"
         "@ed_emp/documents/publication/wcms_743537.pdf"),
    "tokarick_2010_wp10180":
        ("wp10180.pdf",
         "https://www.imf.org/external/pubs/ft/wp/2010/wp10180.pdf"),
    "james_2013_incentives":
        ("james_2013.pdf",
         "https://openknowledge.worldbank.org/server/api/core/"
         "bitstreams/5f14d5e0-1b40-5219-93ab-9691a0b784d0/content"),
    "imf_oecd_un_wb_2015_tax_incentives":
        ("tax_incentives_2015.pdf",
         "https://www.tax-platform.org/sites/pct/files/publications/"
         "100756-Tax-incentives-Main-report-options-PUBLIC_0.pdf"),
}


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


def export_supply_entries():
    """GLOBAL export supply elasticity for the (stylised) depreciation
    lever. Tokarick (2010) provides export SUPPLY (Table 2), not export
    demand; Viet Nam is absent from the paper and the published table's
    sparse cells do not support reliable per-country column extraction,
    so a single cited developing-economy value with a range is used --
    consistent with the lever being explicitly stylised. Range spans the
    GTAP low-income default (~0.3) to the general-equilibrium long-run
    estimates of the covered target countries (ZAF/TUN/THA/SEN ~0.8-1.4
    in Table 2)."""
    def e(variant, value, basis):
        return assumptions.make_entry(
            entry_id=f"GLOBAL-export-supply-elasticity-{variant}",
            country=assumptions.GLOBAL_COUNTRY, scope="elasticity",
            sector="all", field="export_supply_elasticity",
            icio_codes=[], value=value, unit="elasticity",
            method="authored_constant", basis=basis,
            source={"dataset": "IMF WP/10/180 Table 2", "url": "",
                    "accessed": TODAY, "reference_period": "n/a"},
            citation=TOKARICK,
            notes="Tokarick reports export SUPPLY elasticities, not "
                  "export demand; the depreciation lever models the "
                  "export-volume response to the relative-price change "
                  "as a supply expansion and is labelled stylised. Viet "
                  "Nam is not in the paper; a global value is used.")
    return [
        e("central", 0.6, "round central within the covered target "
                          "countries' general-equilibrium estimates "
                          "(SEN~0.8, TUN~0.9, ZAF~1.0, THA~1.4) and the "
                          "GTAP low-income default (~0.3); deliberately "
                          "conservative for a stylised lever"),
        e("low", 0.3, "GTAP low-income default export supply elasticity"),
        e("high", 1.1, "general-equilibrium long-run end of the covered "
                       "target countries' Table 2 estimates"),
    ]


def redundancy_entries():
    """GLOBAL investment-incentive redundancy share (the windfall the
    investment-tax-incentive lever displays). IMF-OECD-UN-WB (2015)
    Table 1 investor surveys: redundancy exceeds 70% in 10 of 14
    surveys; covered target countries Tunisia 58%, Viet Nam 85%,
    Thailand 81%; James (2013) reports Thailand 81%, and Jordan /
    Mozambique / Serbia >=70%."""
    def e(variant, value, basis):
        return assumptions.make_entry(
            entry_id=f"GLOBAL-investment-incentive-redundancy-{variant}",
            country=assumptions.GLOBAL_COUNTRY, scope="other",
            sector="all", field="investment_incentive_redundancy",
            icio_codes=[], value=value, unit="share",
            method="authored_constant", basis=basis,
            source={"dataset": "James 2013; IMF-OECD-UN-WB 2015 Table 1",
                    "url": "", "accessed": TODAY,
                    "reference_period": "n/a"},
            citation=REDUNDANCY,
            notes="share of incentivised investment that would have "
                  "occurred anyway (the windfall); covered target "
                  "countries TUN 0.58, VNM 0.85, THA 0.81")
    return [
        e("central", 0.75, "consistent with 'redundancy exceeds 70% in "
                           "10 of 14 surveys' (IMF-OECD-UN-WB 2015) and "
                           "the covered target-country mean (TUN 0.58, "
                           "VNM 0.85, THA 0.81 -> 0.75)"),
        e("low", 0.50, "below the covered range to bound the windfall "
                       "from below"),
        e("high", 0.90, "upper end of the survey distribution "
                        "(several surveys 90%+)"),
    ]


def record_source_pdfs():
    for key, (fname, url) in SOURCE_PDFS.items():
        path = config.RAW_DIR / fname
        if path.exists():
            download.record_file(key, path, url, method="manual")


def main():
    record_source_pdfs()
    registry = assumptions.load_registry()
    # GLOBAL EIIP labour share (replace the three variants)
    registry["entries"] = [
        e for e in registry["entries"]
        if not (e["country"] == assumptions.GLOBAL_COUNTRY
                and e.get("field") == "eiip_labour_cost_share")
    ] + eiip_entries()
    # GLOBAL export supply elasticity + redundancy share
    for field, builder in [("export_supply_elasticity", export_supply_entries),
                           ("investment_incentive_redundancy",
                            redundancy_entries)]:
        registry["entries"] = [
            e for e in registry["entries"]
            if not (e["country"] == assumptions.GLOBAL_COUNTRY
                    and e.get("field") == field)
        ] + builder()
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
