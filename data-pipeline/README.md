# Data pipeline — OECD ICIO 2025 country files

Produces one static JSON per country in `backend/app/data/countries/`
from real, named datasets. The simulation engine (Phase 2) consumes only
these JSONs; no runtime computation against external data.

## Sources

| Source | Edition / vintage | Access | Used for |
|---|---|---|---|
| OECD Inter-Country Input-Output (ICIO) tables, regular "SML" version (80 economies + ROW), year 2022 | 2025 edition (rev. Jan 2026) | `https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2025/2016-2022_SML.zip` (link discovered from the [OECD ICIO dataset page](https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html)) | Z, M, x, VA, TLS, final demand; A_d, A_m, Leontief inverses |
| OECD Trade in Employment (TiM), dataflow `OECD.STI.PIE,DSD_TIM_2025@DF_TIM_2025,1.0` | 2025 edition | SDMX REST, `format=csvfilewithlabels`; measures `EMPN` (persons) and `LABR` (USD) | employment by industry; compensation of employees (Type II) |
| ILOSTAT | bulk API (`rplumber.ilo.org`) | indicators `EMP_TEMP_SEX_ECO_NB_A`, `EAP_TEAP_SEX_AGE_NB_A` | national employment cross-check; labour force; per-cell fallback |

Exact URLs, SHA-256 hashes, byte sizes, access dates and acquisition
method of every file are recorded in `sources.lock.json`.

**Bot protection caveat:** all OECD endpoints (including the SDMX API)
sit behind a Cloudflare challenge that blocks scripted clients
(verified 2026-06-11). The downloader tries a scripted fetch first and
otherwise instructs you to download in a normal browser and drop the
file into `data-pipeline/raw/` under the expected name; the pipeline
detects it, hashes it and records `method: manual`. ILOSTAT is scriptable.

Expected manual files in `raw/`:

- `2016-2022_SML.zip` (the ICIO bundle, ~160 MB)
- `TIM_EMPN_2022.csv` — from
  `https://sdmx.oecd.org/public/rest/data/OECD.STI.PIE,DSD_TIM_2025@DF_TIM_2025,1.0/EMPN.ZAF+TUN+VNM+THA+SEN....A?startPeriod=2022&endPeriod=2022&format=csvfilewithlabels`
- `TIM_LABR_2022.csv` — same with `LABR.` instead of `EMPN.`

## Commands

```powershell
cd data-pipeline
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

.venv\Scripts\python run_pipeline.py --inspect   # structure discovery
.venv\Scripts\python run_pipeline.py ZAF TUN VNM THA SEN   # build country JSONs
.venv\Scripts\python register_engine_params.py   # engine parameters -> registry
.venv\Scripts\python make_verifier_output.py     # ZAF tariff scenario deliverable
.venv\Scripts\python -m pytest                   # validation + engine suite
```

Runtime: the first build parses the 2022 CSV inside the zip (~2 min);
per-country blocks are cached in `raw/cache/*.npz`, so re-runs take
seconds. Building a country writes:

- `backend/app/data/countries/{ISO3}.json` (only if ALL validation gates
  pass; staged + atomic move, no partial output)
- `backend/app/data/assumptions.json` (registry of every substituted or
  capped value)
- `reports/validation_report_{ISO3}.md`

## Method

1. **Extraction** (native 50-industry detail, per country c): domestic
   intermediates `Z_dd`; imported intermediates `M` (foreign rows into
   c's columns, summed over partners by supplying industry); gross
   output `x`; `VA`/`TLS` rows; final demand by category (HFCE, NPISH,
   GGFC, GFCF, INVNT, DPABR); exports as residual
   `x − Z_dd·1 − F_dom·1`. Balance gates: column identity
   `ΣZ + TLS + VA = OUT` (0.1%, with an absolute floor of 1e-6 of total
   output for source rounding), OUT row = OUT column, derived VA vs VA
   row (1%), exports ≥ 0, spectral radius < 1.
2. **Final demand mapping**: households = HFCE + NPISH; DPABR (direct
   purchases abroad by residents) goes to imported household demand
   (domestic supply into DPABR is asserted ≈ 0); inventories kept so
   `x = Z·1 + F·1` balances.
3. **Aggregation** to the 14 didactic sectors via
   `concordance_icio_to_14.csv` (every ICIO code exactly once,
   judgement calls documented in the `rationale` column); coefficients
   recomputed on aggregates: `A_d = Z diag(x)^-1`, `A_m = M diag(x)^-1`,
   `L_typeI = (I − A_d)^-1`.
4. **Employment** (TiM `EMPN`, persons): matching cascade per industry —
   exact code → child-sum (finer TiM codes partitioning the target) →
   parent-residual (e.g. TiM `C24` minus filled siblings allocated over
   `C24A`/`C24B` by output shares) → ILOSTAT section residual. Everything
   past "exact" is registered in `assumptions.json`.
   `e_i = E_i / x_i` in jobs per USD million of gross output (current
   2022 USD, the ICIO valuation; no price-year conversion).
5. **Type II (Miyazawa)**: labour-income row from TiM `LABR` (same
   cascade; remaining gaps filled with the economy-wide labour share
   computed from observed sectors); consumption column = domestic household
   demand normalised by total compensation, capped at propensity 1 if
   exceeded (registered). `L_typeII` = industry block of the inverse of
   the augmented matrix.

## Validation and engine tests (pytest)

Data checks per country:
1. `colsum(A_d) + colsum(A_m) + VA/x + TLS/x ≈ 1` (±1%)
2. all coefficients ≥ 0 (negative inventory cells permitted, flagged)
3. spectral radius of `A_d` < 1
4. Type I output multipliers: hard bounds (1.0, 3.5), flagged outside
   [1.1, 2.5]
5. Σ sectoral employment within 10% of ILOSTAT national employment
   plus schema, identity, Type II dominance and registry-integrity tests.

Engine tests (the engine at `backend/app/models/engine.py` is pure
numpy/json and is loaded here by file path): 3-sector hand-checked toy
example; linearity; decomposition and channel sums; per-country lever
smoke tests; the tariff acceptance gate (10% manufacturing tariff must
not be net employment-positive, strictly negative with retaliation,
gains ≥ 60% offset); an AST test asserting engine.py contains no
numeric literal outside {0, 1, 2} (all parameters live in
`backend/app/data/assumptions.json` with citations).

The Session A new-vs-old multiplier comparison is preserved at
`reports/comparison_multipliers.md` (the old hardcoded values were
deleted with `tiva_multipliers.py` in Session B; the report is the
permanent record).

## Adding a country

1. Add the ISO3 code to `COUNTRIES` in `config.py` (must be in the ICIO
   80; check with `--inspect`).
2. Extend the TiM browser-download URLs with the new code (or re-export
   `EMPN`/`LABR` CSVs including it) and refresh `raw/TIM_*.csv`.
3. `python run_pipeline.py XXX` — the gates will stop on any coverage
   problem; resolve via the documented fallbacks only.

## Session A status (2026-06-11)

Built and verified: **ZAF, TUN**. Remaining (Session B): VNM, THA, SEN.
The backend engine still runs on the old hardcoded multipliers; it
switches to these JSONs in Phase 2.
