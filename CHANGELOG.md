# Changelog — Economic Policy Simulator

All notable changes to this project are documented here.
Versioning follows [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.
The project is in pre-release (0.x.y); version 1.0.0 will mark the first production-ready release.

---

## [1.2.2] — 2026-06-15  ← current
**Public works / EIIP reframed as a distinct class of intervention.** PATCH: didactic framing only - no engine math or parameter change. Addresses the risk that the lever's low modelled cost-per-job and large headline job count overstate its standing relative to permanent-job levers (apples to oranges).

### Backend
- `run_scenario` adds `employment_programme_note` for public-works and direct-public-employment scenarios: a substantial caveat that these create temporary job-years (not permanent posts) at low/stipend pay and outside standard employment relations; that their cost-per-job and headline count are not comparable with permanent-job levers; that the constant-returns assumption ignores the project-pipeline, institutional and fiscal limits on marginal expansion where a programme already operates at scale (for example South Africa's EPWP); and that the job-quality figures use host-sector averages and so overstate actual programme job quality.
- New labour-based public-works presets for all five countries (previously only South Africa), so the comparison is available everywhere; the South Africa narrative now flags EPWP saturation, and Senegal's flags greenfield headroom.

### Frontend
- The employment-programme caveat is shown as a prominent amber callout at the top of the result.
- Guided mode renders EIIP / public-works (and direct public hiring) as a visibly separated, secondary "Employment programmes - a different class" group, below the permanent-job levers, with its own caveat.

### Tests
- Regression lock regenerated (response gains the note for programme scenarios; 4 new presets). Preset count 24 -> 28.

---

## [1.2.1] — 2026-06-15
**Live labour-market context, Data-tab layout, methodology redesign.** PATCH: data-source and presentation improvements; no model or contract change.

### Backend
- National **informality** and **working-poverty** context indicators are now fetched live from the ILOSTAT SDMX API (latest available year) instead of the static JSON snapshot: `EMP_NIFL_SEX_RT` (total) and `SDG_0111_SEX_AGE_RT` (total, age 15+). New FastAPI-free module `live_indicators.py` with a 24h in-memory cache, an 8s timeout, a short negative-cache on failure, and a clean fallback to the verified snapshot (labelled). `/api/context/{iso3}` overlays the live values, labels the source and period, and sets `data_mode`. These remain context-only and are never used in the simulation; the sectoral informality used by the job-quality module stays in the verified JSONs (model input, hash-locked). Latest at release: ZAF 2025-Q2, VNM 2024-Q4, THA 2024, SEN 2025-Q1; TUN still 2019 (no newer survey).

### Frontend
- Data tab: the labour-market context and data-caveats panel now sits below the headline indicators and employment-by-sector but **above** the cross-country comparison chart. Source/period and live-vs-snapshot mode are shown.
- Methodology tab redesigned: a hero header, a clickable table of contents, and per-section cards (numbered) for the plain-language tier; tier-2 "expert detail" disclosures restyled as clear, collapsed, keyboard-operable panels. Replaces the previous single flat wall of text.

### Tests
- `test_live_indicators.py`: SDMX-CSV parsing (latest period, SEX/AGE filters), fallback on fetch failure, and cache reuse within the TTL (no network in tests). Suite: 400 -> 405.

---

## [1.2.0] — 2026-06-15
**Integrated Prompt v5 — financing transparency, methodology, and result interpretation.** MINOR bump: new financing-mode control and job-quality output dimension, a comprehensive two-tier methodology with its own API and UI, and a corrected trade-elasticity parameter. The v1.0.0 simulate contract is preserved except for the deliberate financing change (documented below); the engine regression lock was regenerated at the new numbers after the Workstream C verification stop.

### Backend
- **Financing modes (Workstream C).** The boolean `include_financing_drag` is replaced by an explicit `financing_mode`: `deficit` (no offset), `tax_financed` (offset = MPC x fiscal cost, **the new default**), `full_crowding_out` (offset = fiscal cost, the old 100% behaviour kept as a labelled upper bound). The marginal propensity to consume is a registered parameter (`GLOBAL-marginal-propensity-to-consume`, central 0.8, range 0.6–0.9; literature_based, Haavelmo 1945 framing; global, as no country-specific value was available). Financing applies symmetrically to every positive-cost fiscal lever, including the stimulus, which loses its separate 0.5 first-round fiscal multiplier (now deprecated in the registry, audit trail preserved) and is no longer costless to finance. Tariffs and depreciation are not financing-eligible; tariff revenue stays a memo item. `run_scenario` returns a structured `financing` object plus gross/net aggregate keys. The legacy boolean is a deprecated alias.
- **Senegal tariff elasticity (Workstream D).** Corrected from the outcome-calibrated −0.5 to the cited central −1.05 (Kee, Nicita & Olarreaga 2008). The sign-forcing tariff acceptance tests are removed and replaced with channel/accounting/transparency tests plus a guard that fails if any test requires a predetermined tariff sign. Consequence: a 10% Senegal manufacturing tariff is now modestly net positive, a property of the data, not an endorsement. This deliberately retires the former net-non-positive acceptance constraint.
- **Job quality gained/lost split (Workstream G).** `engine.job_quality` now returns separate gained and lost profiles (weighted compensation ratio and informality, missing-informality sectors excluded rather than zeroed, "not applicable" on empty groups) alongside the net composition.
- **Methodology API (Workstream B).** `GET /api/methodology` serves the two-tier `docs/methodology.md`.
- **Country caveats (Workstream F.3).** `GET /api/context/{iso3}` now returns a data-derived `caveats` block (data years, employment-validation gap with a warning when large, MPC status, Type II cap) from a FastAPI-free helper.
- **Presets (Workstream I.1).** Every preset carries a lever group, financing mode, a "what this illustrates" line, a "do not conclude" line, and caveat tags. Two preset signs changed as correct consequences of the financing fix (Tunisia demand stimulus now negative; Thailand direct public hiring now positive); narratives updated, and stale references to the deprecated 0.5 multiplier removed.

### Frontend
- Financing-mode selector in the scenario controls; result page shows mode, gross effect, financing offset, net effect, fiscal cost, MPC and caveat (Workstream C.4).
- App title renamed to "Employment Policy Learning Simulator"; forecast/recommendation wording removed; a persistent not-a-forecast notice and corrected exchange-rate wording on the results page (Workstream E).
- Central channel-label map (`channelLabels.js`); no raw snake_case in user-facing output; "financing drag" renders as "financing offset" (Workstream F.1).
- Assumption popovers on every active lever, now showing whether the lever is fiscal and whether the financing mode applies (Workstream F.2).
- Country "Data and model caveats" panel; informality wording corrected to note its use in the job-quality view (Workstream F.3).
- Job-quality panel split into sectors gaining, sectors losing, and net composition (Workstream G).
- Guided mode shows lever settings for every lever (including the newer ones), the financing mode, and the caveat tags.

### Tests
- New: financing modes (`test_financing.py`), channel labels (`test_channel_labels.py`), UI language guard (`test_ui_language.py`), country caveats (`test_country_caveats.py`), job-quality gained/lost (`test_job_quality.py`), tariff transparency + no-sign-forcing guard (`test_engine_tariff_acceptance.py`). Engine regression lock regenerated at the v1.2 numbers and re-enabled. Suite: 222 → 300+.

---

## [1.1.0] — 2026-06-14
**Sessions 19–22 (E–H) — policy-lever expansion and job quality.** Independently verified (regression lock reproduced at 5e-15; every mandated lever identity and acceptance test confirmed; the three judgement calls — Tokarick export-supply provenance, redundancy share, wage cross-check — accepted as honestly handled). MINOR bump: new levers, a new job-quality metric, new UI sections; backward-compatible API (the v1.0.0 simulate contract is a strict subset, regression-locked).

Post-verification follow-ups folded into this release: the percent→fraction conversion is now a single shared helper (`backend/app/api/lever_params.py`) used by both `/api/simulate` and the preset tests, so they cannot drift; the static-accounting caveat was extended to the `tha_production_subsidy_auto` and `vnm_investment_incentive` presets; the informality indicator direction was confirmed (informal employment as a share of sector employment — agriculture highest, finance/public lower).

### Session H — UI, taxonomy, presets, job-quality panel (2026-06-14)
**Frontend**
- Lever taxonomy regrouped into four collapsible groups: (1) industrial & sectoral policy, (2) public investment & employment programmes, (3) macro-fiscal, (4) trade & exchange rate (last, collapsed by default) - directly answering the "tariff-heavy" critique
- New lever controls: production/wage subsidies (per-sector), public investment, investment tax incentive, public works (method choice), direct public hiring, stimulus composition, depreciation; assumptions popovers extended to every new lever
- Results: job-quality panel (wage-bill change, average compensation ratio vs economy, informality composition with caveats), investment-incentive windfall breakdown, job-years framing
- Guided mode reordered to lead with industrial/public-programme scenarios; "What is not in this tool and why" panel with greyed pseudo-levers (interest rates, ALMPs, minimum wages, targeted transfers); country labour-market context (informality, working poverty) in the Data tab
**Backend**
- 9 new test-enforced guided presets (24 total) incl. ZAF public works (EPWP context), VNM investment incentive (windfall lesson), production-vs-wage-subsidy contrast, stimulus-composition comparison, TUN depreciation; static-accounting caveat added to the two flagship presets
- New endpoints: /api/not-in-tool, /api/context/{iso3}, /api/sectors output shares, /api/assumptions

### Session G — job-quality module (2026-06-14)
- engine.job_quality(): wage-bill change (v.L.dF identity), |dE|-weighted average compensation per worker vs economy mean, informality composition of the change (per-country gate; hidden where no data, never imputed); national working poverty stays context-only. docs/job-quality.md. Pure post-processing -- run_scenario and its regression lock untouched.

### Session F — new policy levers (2026-06-13)
- Eight levers via the composable-shock pipeline: public investment, stimulus composition (household/government/investment), production subsidy, wage subsidy, investment tax incentive (windfall/redundancy), public works/EIIP (job-years; labour-based vs conventional), direct public employment, stylised depreciation
- run_scenario gains an optional `extensions` arg; v1 calls byte-identical (35-case regression lock green). API request/response extended. 13 acceptance-style tests x 5 countries. docs/levers/*.md for all 8 + docs/not-in-this-tool.md
- Registered (cited): EIIP labour share (ILO), conventional construction labour share (data-derived per country), export supply elasticity (Tokarick 2010 - note: the paper has export SUPPLY, not demand; documented), investment-incentive redundancy (James 2013; IMF-OECD-UN-WB 2015)

### Session E — data gates and engine generalisation (2026-06-13)
**Engine (E.2)**
- Refactored `backend/app/models/engine.py` to composable typed shocks (`DemandShock`, `ImportPriceShock`, `DomesticCostShock`, `DirectEmployment`, `FiscalCost`) feeding a single evaluator; generalised price/demand primitives (`_cost_push_prices`, `_downstream_dF`, `_real_income_dF`, `_hh_spread`) now shared by every price-side lever so Session F levers reuse one path
- `DirectEmployment` recycles programme wage bills through the Miyazawa closure when Type II is on (e · L_II · h_c · W); raises rather than silently zeroing when no closure exists
- All v1 levers re-expressed as shock compilers; numbers unchanged — a 35-case regression lock (15 presets + 5-country tariff battery × retaliation/Type II) asserts `run_scenario` reproduces the committed v1.0.0 engine at rel=1e-6 (`tests/test_engine_regression_lock.py`, fixture generated pre-refactor from commit 5273bf4)

**Data (E.1)**
- ILOSTAT informal-employment shares by sector appended as an optional `informality` block to the five country JSONs (append-only, byte-identity-gated so verified numbers cannot move); ZAF via ILOSTAT broad aggregate groups, the others ISIC Rev.4 sections; manufacturing-family sectors inherit section C; national informality + working-poverty context indicators included (context only, never in simulation arithmetic)
- EIIP labour-based labour-cost share registered GLOBAL (0.35, range 0.20–0.50; ILO EIIP Green Works); conventional construction labour share registered per country, data-derived from each JSON (construction compensation/output)
- Registry: scopes `informality`/`labour_content`, methods `data_derived`/`share_inheritance`; country-rebuild preservation extended so extension entries survive
- Wage cross-check report: ILOSTAT earnings-by-activity is not served by the rplumber bulk API (HTTP 400); model uses internal TiM compensation (IO-consistent), documented
- Data-availability matrix committed (`reports/data_availability_extension.md`)
- **Pending manual downloads** (IMF/World Bank bot-blocked): Tokarick (2010) export demand elasticities and the investment-incentive redundancy share (James 2013; IMF-OECD-UN-WB 2015) — both feed Session F levers, not the Session E foundation; `register_extension_params.py` registers them once the PDFs are in `raw/`
- Tests: 142 → 222 (regression lock, shock-equivalence, DirectEmployment toy, informality)

---

## [1.0.0] — 2026-06-11
**Session 18 — Session D of the post-audit overhaul: Phase 4 hygiene and deployment. First production-ready release.**

The MAJOR bump marks completion of the four-phase overhaul: verified data pipeline (A), engine rebuild with cited parameters and acceptance gates (B), didactic UI rebuild (C), CI and documentation hygiene (D). Both external verifications passed.

### Continuous integration
- GitHub Action (`.github/workflows/tests.yml`): on every push/PR — the full pytest suite (142 tests: data validation, engine math, tariff acceptance gates, preset walkthrough verification, no-literal AST check), a backend API-contract smoke that re-asserts the acceptance constraint through the HTTP layer, and the frontend build
- CLAUDE.md rule 6 extended: local pytest gate before push stays; a red Action on main must be fixed immediately

### Documentation
- README.md rewritten from scratch: removed every stale claim (live OECD integration, research-grade multipliers, confidence intervals, AI assistant, demographic disaggregation, Sankey); now documents the real pipeline, data editions, ground rules, the audit history (with pointer to the preserved old-vs-new comparison), and what the model cannot do
- DEPLOYMENT.md: free-tier cold-start guidance for classroom delivery (paid instance recommended, or /health keep-alive ping — /health is auth-exempt); CI section; removed the stale chatbot API-key prerequisite
- FastAPI self-description (OpenAPI) rewritten to match the real model

### Performance
- All five country files and engine parameters are loaded eagerly at startup (data problems surface at boot; per-request work is matrix-vector products only)
- Frontend bundle split into react/recharts/app chunks so app changes do not invalidate the vendor cache

### Hygiene
- Stray `test_request.json` (old API contract) and `nul` artifact removed from the repo root

---

## [0.12.0] — 2026-06-11
**Session 17 — Session C of the post-audit overhaul: Phase 3 didactic UI rebuild**

External verification of Session B passed (full numerical reproduction of all five acceptance results and the ZAF channel decomposition); its two carry-over items are implemented here.

### Backend
- Curated scenarios moved to `backend/app/api/presets_data.py` (plain data) with per-scenario walkthrough narrations; `tests/test_presets.py` runs every scenario on the engine and asserts the sign/structure claims its walkthrough makes — five draft narratives were corrected to the model's true stories in the process (notably: tax-financed support to VNM manufacturing and THA automotive is net employment-NEGATIVE because those sectors employ fewer people per dollar than the household basket the financing drag falls on; TUN tariff-plus-support on textiles nets out to approximately zero)
- New endpoints: `GET /api/assumptions[?country_code=]` (the registry with citations, for the lever popovers), `GET /api/limitations` (serves docs/model-limitations.md), `GET /api/sectors?country_code=` now returns each sector's output share
- Simulation response carries `data_source.model_version`; the Type II note now states that the sign of small net results can flip under the upper-bound closure (verifier carry-over 1)
- SEN elasticity registry entry: basis text strengthened per the verifier — the low value is independently defensible (thin domestic manufacturing capacity), not only an acceptance-gate calibration
- New documentation: `docs/levers/{tariff,sector_support,sme_stimulus}.md` methodological notes, `docs/model-limitations.md`; Dockerfile ships `docs/` so the API can serve it

### Frontend (Phase 3 rebuild)
- **Guided Tour is the default tab**: pick a curated scenario, the model runs immediately, and a step-by-step walkthrough narrates what the result teaches; "Open in Free Exploration" hands the levers over for modification
- Free Exploration: the full controls/results view, now behind its own clearly labelled tab
- First-visit modal (learning tool framing, localStorage-gated); permanently accessible "what the model can and cannot tell you" panel rendered from docs/model-limitations.md, linked from the banner and the Methodology tab
- Per-lever assumptions popovers rendering the registry entries (values, basis, citations) for the active country
- Micro-sectors greyed out in lever selection below 0.5% of the country's output (verifier carry-over 2; e.g. Senegal automotive at 0.01%)
- Sector tooltips show each didactic sector's ICIO industry composition
- ResultsPanel: when the parameter range straddles zero or the net effect is under 0.05% of baseline, the headline becomes "Net effect: approximately zero" with the gross reallocation (+gains/−losses) as the robust message; gross reallocation shown alongside all results; every results view stamped "Model vX – OECD ICIO 2025 ed. (year 2022)"
- PolicySlider: numeric input beside each slider, visible keyboard focus states, disabled state for micro-sectors
- Accessibility pass: focus-visible rings on interactive elements, low-contrast grey text raised

---

## [0.11.0] — 2026-06-11
**Session 16 — Session B of the post-audit overhaul: Phase 1 completed (VNM, THA, SEN) and Phase 2 engine rebuild**

External verification of the Session A deliverables passed (independent recomputation of all ZAF/TUN derived objects; four non-blocking follow-ups, all implemented below).

### Data pipeline
- VNM.json, THA.json, SEN.json built from OECD ICIO 2025 / TiM 2025 / ILOSTAT; all validation gates pass (employment gap vs ILOSTAT: VNM 0.11%, THA 0.04%, SEN 9.49% — the SEN gap reflects the TiM national-accounts vs ILOSTAT LFS concept difference, documented in metadata)
- Verifier follow-ups: per-sector ICIO-code composition added to JSON metadata (UI tooltips); employment-denominator and GDP concept notes added; product-side `imports_by_product` and data-derived `domestic_absorption` shares added; export-residual clips now registered in assumptions.json (finding: ZAF construction exports are genuinely ~0 in the source — the only clipped cell was sector T, households as employers)
- Aggregate-level balance gate got the same absolute rounding floor as the native gates (SEN automotive: output USD 3.8m, gap USD −8,400 = source rounding)
- ZAF/TUN regenerated for the metadata additions; all numeric arrays verified byte-identical

### Backend — engine rebuild (Phase 2)
- DELETED `backend/app/data/tiva_multipliers.py` and `backend/app/models/economic_model.py` (fabricated multipliers, np.random I-O matrices, invented wage/job-quality/demographic/synergy functions). The new-vs-old record stays in `data-pipeline/reports/comparison_multipliers.md`
- New `backend/app/models/engine.py`: pure numpy/json Leontief engine over the verified country JSONs; dE = ê L dF with direct/indirect/induced decomposition; Type II (Miyazawa) as a labelled upper-bound toggle; comparative-static (time-horizon scaling removed)
- Tariff lever with four separately reported channels: import substitution (bounded by data-derived domestic absorption), downstream cost-push (price-side Leontief, demand base includes exports), real-income loss, stylised retaliation toggle (top-3 export sectors)
- "Subsidy" lever replaced by government sector support with a financing-drag toggle (tax-financed, default on); SME stimulus spread by household consumption with a cited first-round fiscal multiplier; productivity lever dropped (decision recorded)
- Every behavioural parameter lives in assumptions.json with full citations: per-country import demand elasticities (Kee/Nicita/Olarreaga 2008, Table 1 import-weighted averages: ZAF −1.16, TUN −1.06, THA −1.08; VNM −1.08 = study median, not in sample; SEN −0.5 calibrated to the bottom of the cited range because KNO's −1.05 leaves a 10% manufacturing tariff net employment-positive — reason recorded in the registry); own-price elasticity −0.5 (USDA-ERS TB-1929); retaliation 0.5/top-3 (Fajgelbaum et al. 2020); fiscal multiplier 0.5 [0.1, 1.0] (IMF Batini et al. 2014 — the overhaul doc's 0.6–1.0 was not supported by the source and was not used)
- An AST test enforces that engine.py contains no numeric literal outside {0, 1, 2}; unit conversions live in the API layer
- Acceptance constraint enforced per country (10% manufacturing tariff: ZAF −0.011%, TUN −0.485%, VNM −0.732%, THA −0.226%, SEN −0.019% of baseline employment; strictly negative with retaliation; gains ≥ 60% offset)
- New API contract: aggregate effects with parameter-range bounds (never a single point), channel decomposition, % of sector-sum baseline employment (verifier item), citation-based data_source (the "research-grade" quality flag is gone); removed: wage effects, job-quality metrics, demographic shares, synergy, Sankey transmission paths, cosmetic confidence intervals
- Mozambique removed / Senegal added: wdi_service, schemas, presets (15 presets rebuilt as lever-settings-only), chat prompts purged of country-fact claims (chat remains dormant)
- Test suite now 140 tests (pipeline validation + engine: 3-sector hand-check, linearity, decomposition/channel sums, per-country lever smoke, acceptance gates, no-literal AST test, registry integrity)

### Frontend (minimal surgery; full UI rebuild is Session C)
- Country selector and dashboard: MOZ out, SEN in
- ResultsPanel rebuilt for the new contract: net effect with parameter range, % of baseline employment, channel decomposition bars, direct/indirect/induced, sector bar chart, fiscal flows, citation footer; removed: demographic pies, job-quality panel, wage effect, Sankey, data-quality badge, confidence intervals
- PolicyControls: productivity slider removed, Subsidies renamed Sector Support, three model toggles added (Type II, retaliation, financing drag); time-horizon buttons removed (comparative-static engine)
- Auto-fired `/api/explain` after each simulation removed; AI Assistant tab hidden (backend chat endpoints stay dormant)
- PolicySlider dead-knob fix: decorative thumb now `pointer-events-none`
- Persistent banner: "Learning tool illustrating transmission channels of policy choices - not a forecast"; Methodology tab rewritten truthfully
- Stale MOZAMBIQUE_*.md analysis documents deleted

---

## [0.10.0] — 2026-06-11
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
