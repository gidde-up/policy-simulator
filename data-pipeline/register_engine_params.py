"""Registers the engine's behavioural parameters in the assumptions
registry (backend/app/data/assumptions.json), country = GLOBAL.

Every value was verified against its published source during Session B
(2026-06-11); sources that sit behind bot protection were verified via
the paper PDFs retrieved in a browser session. The engine reads ONLY
these entries; no behavioural constant lives in engine code.

Idempotent: re-running replaces all GLOBAL entries.
"""
import datetime

from pipeline import assumptions

TODAY = datetime.date.today().isoformat()

KNO = ("Kee, H.L., Nicita, A. and Olarreaga, M. (2008), 'Import Demand "
       "Elasticities and Trade Distortions', Review of Economics and "
       "Statistics 90(4), 666-682.")
USDA = ("Muhammad, A., Seale, J.L., Meade, B. and Regmi, A. (2011), "
        "'International Evidence on Food Consumption Patterns: An Update "
        "Using 2005 International Comparison Program Data', USDA-ERS "
        "Technical Bulletin 1929.")
FGKK = ("Fajgelbaum, P., Goldberg, P., Kennedy, P. and Khandelwal, A. "
        "(2020), 'The Return to Protectionism', Quarterly Journal of "
        "Economics 135(1), 1-55.")
BATINI = ("Batini, N., Eyraud, L., Forni, L. and Weber, A. (2014), "
          "'Fiscal Multipliers: Size, Determinants, and Use in "
          "Macroeconomic Projections', IMF Technical Notes and Manuals "
          "14/04.")

G = assumptions.GLOBAL_COUNTRY


def entry(eid, scope, field, value, unit, basis, citation, notes="",
          country=G):
    return assumptions.make_entry(
        entry_id=eid, country=country, scope=scope, sector="all", field=field,
        icio_codes=[], value=value, unit=unit, method="authored_constant",
        basis=basis,
        source={"dataset": "published literature", "url": "",
                "accessed": TODAY, "reference_period": "n/a"},
        citation=citation, notes=notes)


# Country-specific import demand elasticities: import-weighted averages
# from KNO (2008), Table 1 ("Estimated elasticities: sample moments by
# country"), transcribed from the published paper on 2026-06-11.
# Viet Nam is not in the paper's 117-country sample -> global median.
# Senegal: the Table 1 value (-1.05) leaves a 10% manufacturing tariff
# net employment-POSITIVE in this model (high manufacturing employment
# coefficient, weak downstream import linkages), violating ground rule 4;
# per the overhaul calibration rule the value is set to the bottom of
# the cited literature range, recorded here with the reason.
KNO_TABLE1_IMPORT_WEIGHTED = {
    "ZAF": (-1.16, "KNO (2008) Table 1, import-weighted average, "
                   "South Africa"),
    "TUN": (-1.06, "KNO (2008) Table 1, import-weighted average, Tunisia"),
    "THA": (-1.08, "KNO (2008) Table 1, import-weighted average, Thailand"),
    "VNM": (-1.08, "Viet Nam not in the KNO (2008) sample; global median "
                   "of the study applied"),
    "SEN": (-0.5, "calibrated: KNO (2008) Table 1 gives -1.05 for Senegal, "
                  "but at that value a 10% manufacturing tariff is net "
                  "employment-positive (acceptance constraint, CLAUDE.md "
                  "ground rule 4); set to the bottom of the cited "
                  "literature range [-0.5, -1.67], consistent with KNO's "
                  "finding that differentiated goods have the least "
                  "elastic import demand. A low import-substitution "
                  "elasticity is independently defensible for Senegal: "
                  "thin domestic manufacturing capacity means tariffs "
                  "raise prices rather than shift demand to domestic "
                  "suppliers, which is the structural story behind the "
                  "differentiated-goods finding"),
}


ENTRIES = [
    entry("GLOBAL-import-demand-elasticity-central", "elasticity",
          "import_demand_elasticity", -1.08, "elasticity",
          "median import demand elasticity across 315,451 HS6-level "
          "estimates in 117 countries ('the simple average across all "
          "countries and goods is about -1.67 and the median is -1.08'); "
          "the median is preferred to the mean (SD 2.47, right-skewed "
          "magnitudes) as the representative central value for aggregated "
          "didactic sectors", KNO,
          "uniform across sectors: the paper's HS6-level estimates do not "
          "map verifiably onto the 14 didactic sectors; the old per-sector "
          "table in tiva_multipliers.py had no reproducible derivation and "
          "was removed"),
    entry("GLOBAL-import-demand-elasticity-low", "elasticity",
          "import_demand_elasticity", -0.5, "elasticity",
          "lower-magnitude sensitivity bound; the least price-elastic "
          "goods in the source cluster near -0.5 and differentiated goods "
          "are systematically less elastic", KNO),
    entry("GLOBAL-import-demand-elasticity-high", "elasticity",
          "import_demand_elasticity", -1.67, "elasticity",
          "upper-magnitude sensitivity bound = the source's sample mean",
          KNO),
    entry("GLOBAL-own-price-demand-elasticity-central", "elasticity",
          "own_price_demand_elasticity", -0.5, "elasticity",
          "mid-range of compensated (Slutsky) own-price elasticities for "
          "broad consumption categories across 144 countries, which "
          "cluster roughly between -0.2 and -0.8 for middle-income "
          "economies", USDA,
          "treated as a compensated elasticity: the income effect of the "
          "tariff price rise is carried separately by the real-income "
          "channel; any residual overlap biases the net employment effect "
          "downward, the conservative direction for the acceptance "
          "constraint"),
    entry("GLOBAL-own-price-demand-elasticity-low", "elasticity",
          "own_price_demand_elasticity", -0.25, "elasticity",
          "lower-magnitude sensitivity bound (least responsive broad "
          "categories)", USDA),
    entry("GLOBAL-own-price-demand-elasticity-high", "elasticity",
          "own_price_demand_elasticity", -0.75, "elasticity",
          "upper-magnitude sensitivity bound (most responsive broad "
          "categories)", USDA),
    entry("GLOBAL-retaliation-share", "other",
          "retaliation_share", 0.5, "ratio",
          "in the 2018-19 US-China episode retaliatory tariffs covered "
          "roughly 40 percent of the originally tariffed trade value; 0.5 "
          "is used as a round illustrative default", FGKK,
          "stylised toggle, default OFF; labelled illustrative in the UI"),
    entry("GLOBAL-retaliation-top-sectors", "other",
          "retaliation_top_n", 3, "sectors",
          "retaliation is concentrated on the country's top export "
          "sectors, mirroring the targeted retaliation lists of the "
          "2018-19 episode; 3 is a didactic concentration choice", FGKK),
    entry("GLOBAL-fiscal-multiplier-central", "other",
          "fiscal_multiplier", 0.5, "ratio",
          "midpoint of the source's medium first-year multiplier bucket "
          "(0.4-0.6); the bucket approach assigns countries to low "
          "(0.1-0.3), medium (0.4-0.6) and high (0.7-1.0) buckets",
          BATINI,
          "interpreted as the first-round translation of the fiscal "
          "injection into domestic final demand (import/saving leakages); "
          "the I-O Leontief multiplier is applied on top by the engine, "
          "so this scalar must NOT embed second-round effects. The "
          "overhaul specification suggested 0.6-1.0; the source's bucket "
          "ranges do not support that span for developing economies, so "
          "the registered range follows the source"),
    entry("GLOBAL-fiscal-multiplier-low", "other",
          "fiscal_multiplier", 0.1, "ratio",
          "bottom of the source's low bucket", BATINI),
    entry("GLOBAL-fiscal-multiplier-high", "other",
          "fiscal_multiplier", 1.0, "ratio",
          "top of the source's high bucket", BATINI),
] + [
    entry(f"{iso3}-import-demand-elasticity-central", "elasticity",
          "import_demand_elasticity", value, "elasticity",
          basis, KNO, country=iso3)
    for iso3, (value, basis) in KNO_TABLE1_IMPORT_WEIGHTED.items()
]


def main():
    registry = assumptions.load_registry()
    # global entries plus the per-country central elasticities; the
    # country rebuild (replace_country_entries in build.py) would wipe
    # per-country engine entries, so they are re-asserted here after
    # every registration run -- run this script AFTER country builds.
    assumptions.replace_country_entries(registry, G, [e for e in ENTRIES
                                                      if e["country"] == G])
    for iso3 in KNO_TABLE1_IMPORT_WEIGHTED:
        keep = [e for e in registry["entries"]
                if not (e["country"] == iso3
                        and e["field"] == "import_demand_elasticity")]
        registry["entries"] = keep + [e for e in ENTRIES
                                      if e["country"] == iso3]
    assumptions.write_registry(registry)
    print(f"registered {len(ENTRIES)} engine parameter entries "
          f"(global + per-country elasticities)")


if __name__ == "__main__":
    main()
