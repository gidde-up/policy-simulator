# Changelog — Economic Policy Simulator

All notable changes to this project are documented here.
Versioning follows [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.
The project is in pre-release (0.x.y); version 1.0.0 will mark the first production-ready release.

---

## [0.3.0] — 2026-03-05
**Sessions 12-13 — Model integrity, economic rigor, and UI transparency**
Commit: `23f09b3`

### Backend — Model integrity (Coder review)
- **Reproducibility fix**: seeded random technical coefficients matrix with `np.random.seed(42)` — indirect employment effects are now reproducible across instantiations
- **Data-quality-aware confidence intervals**: OECD-backed countries (ZAF, VNM, THA) use ±10%/±15% uncertainty; stylized countries (TUN, MOZ) use ±25%/±30%
- **Sector-specific import elasticities**: replaced universal `−1.2` constant with 14-sector dictionary based on Kee, Nicita & Olarreaga (2008); range −0.3 (public services) to −2.0 (textiles)
- **Removed dead code**: eliminated unused flat `induced_multiplier = 1.4` constant (sector-specific TiVA values were already in use)
- **API-level input validation**: added Pydantic `@field_validator` for tariff changes (−50% to 100%) and subsidy changes (0% to 30%)
- **WDI partial-data warnings**: missing indicators now collected in `data_warnings` list and returned in `CountryProfileResponse`

### Backend — Economic rigor (Economist review)
- **Downstream tariff cost penalty**: tariffs now impose a negative demand shock on downstream sectors that use the tariffed input, weighted by inter-industry linkage coefficient (threshold: 0.07) and 40% pass-through rate; corrects the prior model which only captured upstream Leontief effects
- **Productivity model direction corrected**: short-term multiplier changed from +0.20 to −0.15 (displacement effect dominates); medium-term +0.45 (competitiveness gains begin); long-term +1.0 (expanded markets); grounded in Acemoglu & Restrepo (2018)
- **SME fiscal multipliers lowered**: peak multiplier reduced from 1.5 to 1.0; range now 0.75–1.0, consistent with IMF/World Bank empirical estimates for developing countries
- **Synergy multiplier tightened**: base synergy bonuses reduced (1.05/1.08 vs prior 1.10/1.15); added negative interaction term when avg tariff or avg subsidy exceeds 8% (rent-seeking penalty)

### Frontend — UI transparency
- **Model boundaries warning banner**: dismissible amber banner displayed before results on every simulation run; lists four key partial-equilibrium limitations (no wage pressure, no crowding-out, no exchange-rate effects, no price-level changes)
- **Data quality badge**: green (OECD TiVA) or amber (stylized estimates) badge displayed in results header
- **Gross/net disclaimer**: footnote added below total jobs figure clarifying results are gross employment effects, not net of economy-wide displacement

---

## [0.2.0] — 2026-02-23
**Sessions 9-11 — Mozambique expansion and job quality metrics**
Commits: `4286408`, `0e54df7`, `98663c8`, `24d03c6`

### New features
- **Mozambique (MOZ) country support**: full data profile, stylized employment multipliers, and five preset policy scenarios
- **Job quality metrics**: added `JobQualityMetrics` response schema with formality rate, working poverty risk, productivity category, and sector composition of new jobs
- **Full technical model documentation**: Methodology tab expanded with complete I-O model documentation, data sources, and limitation disclosures
- **Productivity slider clarification**: label updated to reduce ambiguity about what the parameter represents

### Bug fixes
- Fixed missing `Any` import in `economic_model.py`

---

## [0.1.0] — 2026-02-07
**Sessions 1-8 — Initial working version**
Commit: `d2f0335`

### Core features
- **Leontief Input-Output employment model**: sector-level employment simulation with direct, indirect, and induced effects; Type I and Type II multipliers
- **Four countries**: South Africa (ZAF), Tunisia (TUN), Viet Nam (VNM), Thailand (THA) with OECD TiVA multipliers for ZAF/VNM/THA
- **Policy levers**: tariff changes (by sector), subsidy changes (by sector), SME stimulus (% GDP), productivity investment; short/medium/long time horizons
- **Non-linear policy effects**: tariff Laffer curve, subsidy diminishing returns
- **Policy cost calculator**: tariff revenue (gross/net), subsidy spending, SME/productivity costs, deadweight loss (Harberger triangle), net fiscal impact, cost-per-job
- **WDI integration**: live World Bank data for baseline employment, unemployment, GDP, labor force, and sectoral employment indicators
- **AI chat assistant**: natural-language policy query interface via Claude API
- **Preset scenarios**: 4-5 curated policy scenarios per country with documented rationale
- **Sankey diagram**: visual transmission-path diagram from policy to employment effects
- **Frontend**: React + TailwindCSS + Recharts SPA with tabbed layout (Controls / Results / Country Dashboard / Chat / Methodology)
- **Backend**: FastAPI + Pydantic with async endpoints and auth middleware
- **Deployment**: Docker container on Render.com with auto-deploy from GitHub main branch

---

## Versioning notes

| Version | Status | Description |
|---------|--------|-------------|
| 0.3.x | Current | Model integrity + economic rigor fixes |
| 0.2.x | Archived | Mozambique + job quality |
| 0.1.x | Archived | Initial working version |

Version 1.0.0 target: completion of Reviewer 3 (Learner/Didactic) fixes and a unit test suite.

### Planned for 0.4.0 (Learner/Didactic fixes)
- Guided mode with structured exercises per country
- Auto-triggered 3-sentence AI interpretation after each simulation run
- Time horizon labels with year counts (Short = 1 yr, Medium = 3 yr, Long = 5 yr)
- ChatPanel example prompt chips
- Scenario save + compare feature

### Planned for 0.5.0 (Code quality)
- Unit test suite (3-5 core tests)
- Sensitivity chart (single-slider range sweep)
- PDF/export results
- LocalStorage scenario persistence
- Sankey tooltip with actual job numbers
