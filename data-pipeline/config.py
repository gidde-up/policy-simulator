"""Central configuration for the ICIO data pipeline.

Single source of constants. No numeric model parameters live here --
only structural settings, paths, source locations and tolerances.
"""
from pathlib import Path

PIPELINE_VERSION = "1.0.0"

# --- Countries -------------------------------------------------------------
# Coded for all five target countries; Session A runs only ZAF and TUN.
COUNTRIES = ["ZAF", "TUN", "VNM", "THA", "SEN"]

COUNTRY_NAMES = {
    "ZAF": "South Africa",
    "TUN": "Tunisia",
    "VNM": "Viet Nam",
    "THA": "Thailand",
    "SEN": "Senegal",
}

# --- Reference data --------------------------------------------------------
REFERENCE_YEAR = 2022
ICIO_EDITION = "2025 (rev. Jan 2026)"

# OECD ICIO dataset page (for documentation; actual file URL in sources.lock.json):
ICIO_DATASET_PAGE = (
    "https://www.oecd.org/en/data/datasets/"
    "inter-country-input-output-tables.html"
)

# OECD SDMX REST API (keyless)
SDMX_BASE = "https://sdmx.oecd.org/public/rest"
# Trade in Employment 2025 edition dataflow (verified reachable 2026-06-10)
TIM_DATAFLOW = "OECD.STI.PIE,DSD_TIM_2025@DF_TIM_2025,1.0"
# TiM key order: MEASURE.REF_AREA.ACTIVITY.COUNTERPART_AREA.UNIT_MEASURE.FREQ
TIM_MEASURE_EMPLOYMENT = "EMPN"   # employment, persons (UNIT_MULT=3 -> thousands)
TIM_MEASURE_COMPENSATION = "LABR"  # compensation of employees, USD million

# ILOSTAT bulk API (keyless; verified reachable 2026-06-10)
ILOSTAT_BASE = "https://rplumber.ilo.org/data/indicator/"
# Employment by sex and economic activity (ISIC Rev.4, 1-digit), annual
ILOSTAT_EMP_BY_ACTIVITY = "EMP_TEMP_SEX_ECO_NB_A"
# Labour force by sex and age, annual
ILOSTAT_LABOUR_FORCE = "EAP_TEAP_SEX_AGE_NB_A"

# --- The 14 didactic sectors (canonical order, matches existing UI) --------
SECTORS_14 = [
    "agriculture",
    "mining",
    "manufacturing",
    "textiles",
    "automotive",
    "food_processing",
    "chemicals",
    "construction",
    "utilities",
    "trade",
    "transport",
    "finance",
    "public_services",
    "other_services",
]

# --- Paths ------------------------------------------------------------------
PIPELINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_DIR.parent
RAW_DIR = PIPELINE_DIR / "raw"
CACHE_DIR = RAW_DIR / "cache"
STAGING_DIR = RAW_DIR / "staging"
REPORTS_DIR = PIPELINE_DIR / "reports"
CONCORDANCE_CSV = PIPELINE_DIR / "concordance_icio_to_14.csv"
SOURCES_LOCK = PIPELINE_DIR / "sources.lock.json"

OUTPUT_DIR = REPO_ROOT / "backend" / "app" / "data" / "countries"
ASSUMPTIONS_JSON = REPO_ROOT / "backend" / "app" / "data" / "assumptions.json"
OLD_MULTIPLIERS_PY = REPO_ROOT / "backend" / "app" / "data" / "tiva_multipliers.py"

# --- Tolerances (validation gates) ------------------------------------------
TOL_COLUMN_IDENTITY = 0.001    # ZxA column balance vs OUT, fraction
TOL_ROW_IDENTITY = 0.001       # row balance vs x, fraction
TOL_VA_DERIVED = 0.01          # derived VA vs VA+TLS rows, fraction
TOL_COEFF_SUM = 0.01           # A_d + A_m + VA-coeff column sums vs 1, fraction
MULTIPLIER_SOFT_RANGE = (1.1, 2.5)   # spec range; outside -> flagged
MULTIPLIER_HARD_RANGE = (1.0, 3.5)   # outside -> hard failure
EMPLOYMENT_GAP_MAX = 0.10      # sector-sum vs ILOSTAT national total
