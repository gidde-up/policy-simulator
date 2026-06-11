# Changelog — Economic Policy Simulator

All notable changes to this project are documented here.
Versioning follows [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.
The project is in pre-release (0.x.y); version 1.0.0 will mark the first production-ready release.

---

## [0.10.0] — 2026-06-11  ← current
**Session 15 — Phase 1 data pipeline (Session A of the post-audit overhaul): real OECD ICIO data for ZAF and TUN**

### Data pipeline (new top-level directory `data-pipeline/`)
- New reproducible pipeline computing country model files from real datasets: OECD ICIO 2025 edition (rev. Jan 2026, regular "SML" version, 80 economies + ROW, year 2022), OECD Trade in Employment (TiM) 2025 (`EMPN` employment, `LABR` compensation of employees), ILOSTAT (national employment cross-check, labour force)
- Structure discovery from the ICIO file itself (81 economies, 50 industries, FD categories HFCE/NPISH/GGFC/GFCF/INVNT/DPABR); nothing about the layout hardcoded; unknown labels stop the run
- Committed concordance `data-pipeline/concordance_icio_to_14.csv`: 50 ICIO industries to the 14 didactic sectors, one row per code with rationale (judgement calls documented: C19 coke/petroleum and C22 rubber/plastics grouped with chemicals; C301/C302T309 other transport equipment NOT in automotive; real estate in other_services)
- Per-country extraction at native detail with balance gates (column identity, OUT row/column consistency, derived VA vs VA row, exports residual >= 0, spectral radius < 1); aggregation to 14 sectors; `A_d`, `A_m`, `L_typeI = (I-A_d)^-1`
- Employment matching cascade: TiM exact (48/50 industries for both countries) -> child-sum -> parent-residual (C24 split over C24A/C24B by output shares) -> ILOSTAT section residual; every non-exact cell registered
- Type II (induced) via Miyazawa household endogenisation from TiM labour compensation; consumption propensity capped at 1 where exceeded (registered)
- Output: `backend/app/data/countries/ZAF.json` and `TUN.json` (versioned schema with full source metadata and access dates); `backend/app/data/assumptions.json` registry (10 entries); validation reports and a new-vs-old multiplier comparison table in `data-pipeline/reports/`
- Provenance lockfile `data-pipeline/sources.lock.json` (URL, SHA-256, bytes, access date, acquisition method per source file); OECD endpoints are Cloudflare-protected, so the ICIO zip and TiM CSVs were acquired via documented manual browser download
- pytest suite (34 tests): coefficient sums, non-negativity, spectral radius, output multiplier ranges, employment vs ILOSTAT national totals, 3-sector hand-check of the Leontief identity, registry integrity, comparison-table freshness
- Findings for the record: old hardcoded "research-grade" multipliers exceed the ICIO-derived values by roughly 2-4x in most sectors (e.g. ZAF agriculture direct: 127.3 typed in code vs 29.5 computed)

### Project governance
- CLAUDE.md replaced with the post-audit ground rules (no invented numbers, no false provenance, stop on missing data, push only after pytest passes)
- .gitignore: added `data-pipeline/raw/`, `data-pipeline/.venv/`, `*.zip`

### Unchanged this session (by design — Session A stops here)
- Engine (`economic_model.py`, `tiva_multipliers.py`), API and frontend untouched; the app still runs on the old multipliers until the Phase 2 engine rebuild
- Mozambique removal and Senegal addition deferred to Session B
- ZAF.json / TUN.json now go to independent verification before Session B (VNM, THA, SEN + engine rebuild)

---

## [0.9.0] — 2026-03-16
**Session 14 — Learner/Didactic fixes**

### Frontend
- **Time horizon year labels**: buttons now read "Short (1 yr)", "Medium (3 yrs)", "Long (5 yrs)" for clarity
- **ChatPanel prompt chips**: four clickable example prompts added above the input field to guide users who don't know what to ask
- **Auto-triggered AI interpretation**: after each simulation run, ResultsPanel automatically fetches a plain-language explanation from the `/api/explain` endpoint and displays it in a blue panel above the numeric results; interpretation clears on reset and reloads on each new run; fails silently if API is unavailable

---

## [0.8.0] — 2026-03-05
**Sessions 12-13 — Model integrity, economic rigor, and UI transparency**
Commit: `23f09b3`

### Backend — Model integrity
- **Reproducibility fix**: seeded technical coefficients matrix with `np.random.seed(42)`; indirect employment effects are now reproducible across instantiations
- **Data-quality-aware confidence intervals**: OECD-backed countries (ZAF, VNM, THA) use ±10%/±15% uncertainty; stylized countries (TUN, MOZ) use ±25%/±30%
- **Sector-specific import elasticities**: replaced universal −1.2 constant with 14-sector dictionary based on Kee, Nicita & Olarreaga (2008); range −0.3 (public services) to −2.0 (textiles)
- **API-level input validation**: Pydantic `@field_validator` for tariff changes (−50% to 100%) and subsidy changes (0% to 30%)
- **WDI partial-data warnings**: missing indicators returned in `data_warnings` list of `CountryProfileResponse`
- **Removed dead code**: eliminated unused flat `induced_multiplier = 1.4` constant

### Backend — Economic rigor
- **Downstream tariff cost penalty**: tariffs now impose negative demand shocks on downstream sectors using the tariffed input; weighted by inter-industry linkage (threshold 0.07) and 40% pass-through; corrects prior model which captured only upstream Leontief effects
- **Productivity model direction corrected**: short-term multiplier changed from +0.20 to −0.15 (displacement dominates); medium-term +0.45 (competitiveness gains); long-term +1.0 (expanded markets); grounded in Acemoglu & Restrepo (2018)
- **SME fiscal multipliers lowered**: peak reduced from 1.5 to 1.0; range now 0.75–1.0, consistent with IMF/World Bank developing-country empirical estimates
- **Synergy multiplier tightened**: base bonuses reduced (1.05/1.08 vs prior 1.10/1.15); negative interaction term added when avg tariff or avg subsidy exceeds 8% (rent-seeking penalty)

### Frontend
- **Model boundaries warning banner**: dismissible amber banner before results listing four partial-equilibrium limitations (no wage pressure, no crowding-out, no exchange-rate effects, no price-level changes)
- **Data quality badge**: green (OECD TiVA) or amber (stylized estimates) in results header
- **Gross/net disclaimer**: footnote below total jobs figure clarifying results are gross effects, not net of economy-wide displacement

---

## [0.7.1] — 2026-02-23
**Session 11 — UI clarifications and full technical documentation**
Commits: `98663c8`, `24d03c6`

- **Productivity slider label clarified**: unit changed from `%` to `% of sector GDP`; description updated to specify targeted sectors (manufacturing, automotive, chemicals, food processing)
- **Full technical model documentation**: collapsible panel added to Methodology tab with 12 sections — Leontief framework equations, sector list, multiplier types, GDP/sector-share tables for all 5 countries, policy transmission formulas, synergy logic, time-horizon scaling, demographic disaggregation, job quality calculations, cost-benefit formulas (including Harberger triangle), technical coefficients assumptions, and confidence interval methodology

---

## [0.7.0] — 2026-02-23
**Sessions 9-10 — Mozambique and job quality metrics**
Commit: `4286408`

### Mozambique (MOZ)
- **Country added**: low-income economy with 69.5% agricultural employment and 95% informality
- **Employment multipliers**: stylized estimates from World Bank WDI 2024 and ILO statistics; very high labor intensity in agriculture (168 jobs/$1M), very low in extractives (8 jobs/$1M — capital-intensive LNG/coal)
- **Three preset scenarios**: Agricultural Focus, Commodity Extraction, Industrialization Drive; designed to illustrate the structural transformation dilemma (natural gas revenues generate minimal jobs)
- **WDI service**: MOZ added to supported countries with data profile
- **Frontend**: MOZ country selector, flag emoji support added to CSS font stack

### Job quality metrics
- **Problem identified**: aggregate job counts conceal quality differences; Mozambique agriculture creates more jobs than industry but at 88% informality and ~85% working poverty risk vs 26% informality and ~30% poverty risk for manufacturing
- **New `JobQualityMetrics` schema**: formalization rate, working poverty risk, avg productivity (USD/worker), high/low productivity job counts, sector composition breakdown
- **Backend**: `_calculate_job_quality_metrics()` method using sector-specific poverty rates (85% agriculture → 10% finance) and productivity estimates ($3.5K agriculture → $28K finance)
- **Frontend**: new "Job Quality Analysis" section in ResultsPanel with three color-coded metric cards and horizontal sector composition bar chart

---

## [0.6.0] — 2026-02-07
**Session 8 — Viet Nam and Thailand**
Commit: `d2f0335` (bundled with initial commit)

- **Viet Nam (VNM)**: GDP $450B; OECD TiVA/ICIO 2023 multipliers (research-grade); country-specific I-O matrix reflecting textiles/electronics/agriculture linkages; demographic shares from GSO Labour Force Survey; three preset scenarios (Electronics Hub, Textile Export, Rural Development)
- **Thailand (THA)**: GDP $515B; OECD TiVA/ICIO 2023 multipliers (research-grade); country-specific I-O matrix reflecting automotive supply chain and tourism; demographic shares from NSO Labour Force Survey; three preset scenarios (Automotive Hub, Tourism Recovery, Food Processing)
- **Labour force % indicator**: total jobs figure now shows as share of labour force
- **Fiscal impact % of public budget**: net fiscal impact shown as % of annual government expenditure (from WDI indicator `GC.XPN.TOTL.GD.ZS`)

---

## [0.5.0] — 2026-02-07
**Session 7 — Web deployment**
Commit: `d2f0335` (bundled with initial commit)

- **HTTP Basic Auth**: username/password protection via `AUTH_USERNAME` / `AUTH_PASSWORD` environment variables; skipped in local dev; `/health` endpoint exempted for Render monitoring
- **Frontend served from FastAPI**: built React app (`frontend/dist/`) served as static files; SPA catch-all route returns `index.html` for non-API paths
- **Docker**: multi-stage Dockerfile (Node builds frontend, Python serves everything); `.dockerignore` excludes dev artefacts
- **Render.com**: `render.yaml` blueprint; auto-redeploys on push to `main`; `DEPLOYMENT.md` with step-by-step instructions
- **GitHub**: repository created at `github.com/gidde-up/policy-simulator`

---

## [0.4.0] — 2026-02-07
**Session 6 — Cost-benefit analysis**
Commit: `d2f0335` (bundled with initial commit)

- **Fiscal cost calculations**: tariff revenue (gross and net after import reduction via demand elasticity), deadweight loss (Harberger triangle), subsidy/SME/productivity direct spending
- **Key insight modeled**: tariffs generate revenue but also impose economic costs; import reduction reduces realised revenue below naive calculation; deadweight loss represents destroyed consumer/producer surplus
- **Cost-per-job metrics**: fiscal cost per job (can be negative for tariff revenue scenarios) and economic cost per job (always positive, includes DWL)
- **Frontend**: new "Cost-Benefit Analysis" section in ResultsPanel with fiscal impact breakdown and tariff revenue illusion warning note

---

## [0.3.0] — 2026-02-07
**Session 5 — OECD TiVA data integration**
Commit: `d2f0335` (bundled with initial commit)

- **South Africa multipliers upgraded**: replaced stylized estimates with OECD TiVA/ICIO 2023 data (reference year 2020); pre-calculated Type I and Type II multipliers by sector
- **New data module** (`backend/app/data/tiva_multipliers.py`): OECD multipliers, demographic shares from Stats SA Labour Force Survey, `is_tiva_available()` for runtime data-source checks
- **Data source transparency**: API response includes `data_source` field with quality indicator; ResultsPanel shows green badge (OECD) or amber badge (stylized)
- **Tunisia**: confirmed as stylized estimates (not in OECD ICIO); clearly marked as illustrative

---

## [0.2.0] — late Jan 2026
**Session 4 — Model realism: non-linear policy effects**

- **Tariff response curve**: optimal range 8-12%; diminishing returns above; negative effects above ~22%; export-oriented sectors (automotive, textiles, manufacturing, chemicals) face additional penalty above 15%; trade retaliation penalty (up to −30%) when aggregate tariffs exceed 50%
- **Subsidy response curve**: elasticity declines from 0.9 (at 5% GDP) to 0.1 (at 20%+ GDP); fiscal crowding-out above 30% combined subsidy
- **SME stimulus fiscal multiplier**: declines from 1.5 (at 1% GDP) to ~1.0 (at 4%+ GDP) to reflect absorption constraints
- **Productivity time-dependency**: effectiveness scaled by time horizon (0.2 short-term → 1.0 long-term); job quality bonus in medium/long term
- **Policy synergy system**: balanced 2-policy mixes +10%; 3-policy +15%; 4-policy complexity penalty −10%; specific complementary/non-complementary interaction terms
- **UI**: time horizon selector moved outside policy tabs (always visible); Methodology tab updated with non-linear effects documentation

---

## [0.1.1] — late Jan 2026
**Session 2 — Core fixes and first visualisations**

- **Job creation numbers fixed**: model was returning percentages instead of USD millions; added `gdp_millions` and `sector_shares`; SME stimulus now correctly calculated (e.g. 2% of $400B = $8B injection)
- **Sectoral employment chart**: stacked bar chart showing direct and indirect jobs per sector
- **Before/after unemployment visualisation**: current vs projected rates with color-coded improvement/worsening badges, progress bars, disaggregated by total/youth/female/male
- **Methodology tab**: comprehensive disclaimer covering data sources, model methodology, five known limitations, appropriate vs inappropriate use cases
- **start.bat**: fixed early-exit bug; added error handling and absolute paths
- **Footer**: added "Educational tool only" warning with link to Methodology

---

## [0.1.0] — late Jan 2026
**Session 1 — Initial build**

- Full-stack application structure: FastAPI backend + React/Vite frontend
- Leontief Input-Output employment simulation model (14 sectors; direct, indirect, induced effects)
- World Bank WDI API client for real-time baseline indicators
- Four policy levers: import tariffs, subsidies, SME stimulus, productivity investment
- Sankey diagram for policy transmission visualisation
- Claude API chatbot integration for natural-language policy queries
- Initial countries: South Africa (ZAF) and Tunisia (TUN)
- Preset policy scenarios
- Demographic disaggregation: gender, age (youth 15-24), formal/informal

---

## Versioning summary

| Version | Date | Sessions | Description |
|---------|------|----------|-------------|
| 0.9.0 | 2026-03-16 | 14 | Learner/didactic fixes (time horizon labels, prompt chips, auto AI interpretation) |
| 0.8.0 | 2026-03-05 | 12-13 | Model integrity + economic rigor + UI transparency |
| 0.7.1 | 2026-02-23 | 11 | UI clarifications + full technical documentation |
| 0.7.0 | 2026-02-23 | 9-10 | Mozambique + job quality metrics |
| 0.6.0 | 2026-02-07 | 8 | Viet Nam and Thailand |
| 0.5.0 | 2026-02-07 | 7 | Web deployment (Render.com + Docker + auth) |
| 0.4.0 | 2026-02-07 | 6 | Cost-benefit analysis |
| 0.3.0 | 2026-02-07 | 5 | OECD TiVA data integration (ZAF) |
| 0.2.0 | late Jan 2026 | 4 | Non-linear policy effects + synergy model |
| 0.1.1 | late Jan 2026 | 2-3 | Core fixes, visualisations, methodology tab |
| 0.1.0 | late Jan 2026 | 1 | Initial build |

Version 1.0.0 target: completion of learner/didactic improvements (guided mode, auto-triggered AI interpretation, scenario comparison) and a unit test suite.

### Planned for 0.10.0 (Learner/Didactic — remaining Reviewer 3 items)
- Guided mode with structured exercises per country (3-4 per country, framed as questions)
- Scenario save + compare feature (side-by-side results)
- Policy lever real-world anchoring (current tariff rate context on sliders)

### Planned for 0.10.0 (Code quality)
- Unit test suite (3-5 core tests)
- Sensitivity chart (single-slider range sweep)
- PDF/export results
- LocalStorage scenario persistence
- Sankey tooltip with actual job numbers
