# Economic Policy Simulator - Project Context

## Quick Start
```bash
# Run from C:\Users\bernd\vibecode\policy-simulator folder:
start.bat
```
This opens the backend (http://localhost:8000) and frontend (http://localhost:5173) in separate windows.

---

## Project Overview

An interactive, educational economic policy simulation tool for policymakers to visualize job creation effects of different policy choices.

### Key Features
- **Target Countries**: South Africa (ZAF), Tunisia (TUN), Viet Nam (VNM), Thailand (THA), Mozambique (MOZ)
- **Data Source**: World Bank WDI API (real-time indicators)
- **Policy Levers**: Import tariffs, subsidies, SME stimulus, productivity investment
- **Output**: Job creation projections disaggregated by gender, age (youth 15-24), job quality (formal/informal)
- **Time Horizons**: 1 year (short), 3 years (medium), 5 years (long)
- **Visualizations**:
  - Sankey flow diagrams (policy transmission)
  - Stacked bar charts (sectoral employment with direct/indirect breakdown)
  - Before/after unemployment indicators with visual comparison
  - Demographic pie charts (gender, age, job quality)
- **AI Chatbot**: Claude API integration for natural language policy queries
- **Methodology Tab**: Comprehensive disclaimer explaining data sources, model limitations, and appropriate use

### Tech Stack
- **Frontend**: React + Vite, TailwindCSS, Recharts, Lucide icons
- **Backend**: Python FastAPI, NumPy
- **Economic Model**: Leontief Input-Output analysis with employment multipliers
- **APIs**: World Bank WDI (real-time), Anthropic Claude (chatbot)

---

## Project Structure

```
policy-simulator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          # FastAPI endpoints
│   │   │   └── schemas.py         # Pydantic models
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── economic_model.py  # Core I-O simulation
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── wdi_service.py     # World Bank API client
│   │   │   └── chat_service.py    # Claude AI integration
│   │   ├── data/
│   │   │   ├── countries/         # NEW: verified country JSONs (ZAF, TUN)
│   │   │   ├── assumptions.json   # NEW: registry of substituted values
│   │   │   └── tiva_multipliers.py  # legacy hardcoded values (Phase 2: delete)
│   │   └── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env                       # ANTHROPIC_API_KEY (create this)
│   └── venv/                      # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ResultsPanel.jsx       # Main results display
│   │   │   ├── SankeyDiagram.jsx      # Policy flow visualization
│   │   │   ├── PolicyControls.jsx     # Sliders for policy inputs
│   │   │   ├── CountryDashboard.jsx   # WDI data display
│   │   │   ├── ChatPanel.jsx          # AI assistant interface
│   │   │   ├── Header.jsx             # Country selector
│   │   │   └── PresetScenarios.jsx    # Preset policy buttons
│   │   ├── hooks/
│   │   │   └── useSimulation.js       # Simulation state management
│   │   ├── services/
│   │   │   └── api.js                 # API client
│   │   └── App.jsx                    # Main app with tabs
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── node_modules/
├── data-pipeline/         # NEW (0.10.0): ICIO 2025 data pipeline (own venv, not deployed)
│   ├── run_pipeline.py            # CLI: --inspect | build countries
│   ├── make_comparison.py         # new-vs-old multiplier table
│   ├── config.py                  # countries, year, URLs, tolerances
│   ├── concordance_icio_to_14.csv # 50 ICIO industries -> 14 sectors
│   ├── sources.lock.json          # provenance manifest (sha256, dates)
│   ├── pipeline/                  # parse, extract, aggregate, employment,
│   │                              #   miyazawa, validate, build modules
│   ├── tests/                     # pytest validation suite (34 tests)
│   ├── reports/                   # validation + comparison reports
│   └── raw/                       # git-ignored source downloads + cache
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
├── SETUP.txt              # Manual setup instructions
└── project_context.md     # This file
```

---

## Key Files Reference

### Engine (`backend/app/models/engine.py`) — new in 0.11.0

Pure numpy/json Leontief engine over the verified country JSONs
(`backend/app/data/countries/{ISO3}.json`). No FastAPI imports; loadable
by file path (the pipeline test suite does exactly that). Contains NO
behavioural constants — an AST test asserts no numeric literal outside
{0, 1, 2}; every parameter comes from `backend/app/data/assumptions.json`
(GLOBAL-* entries plus per-country import demand elasticities from
Kee/Nicita/Olarreaga 2008, Table 1).

**Core:** `run_scenario(iso3, tariffs, sector_support, sme_stimulus,
include_type_ii, include_retaliation, include_financing_drag)` —
all rates as fractions; returns USD million / persons. dE = ê L dF with
direct/indirect/induced decomposition (Type II = Miyazawa, labelled
upper bound). Tariff channels computed separately: import substitution
(bounded by the data-derived domestic absorption share), downstream
cost-push (price-side Leontief, demand base includes exports),
real-income loss, optional stylised retaliation.

**Unit conversions** (percent <-> fraction, USD million <-> USD) live in
`routes.py`, never in the engine.

### API Routes (`backend/app/api/routes.py`)

**Endpoints (paths unchanged, /simulate contract NEW in 0.11.0):**
- `POST /api/simulate`: new request fields `tariff_changes` (0..50),
  `sector_support` (0..30, replaces subsidy_changes), `sme_stimulus`,
  `include_type_ii` / `include_retaliation` / `include_financing_drag`;
  `productivity_investment` and `time_horizon` REMOVED.
  Response: aggregate with parameter-range bounds, channel decomposition,
  per-sector effects, costs, citation-based data_source, assumptions ids.
- `GET /api/multipliers/{code}`, `GET /api/sectors[?country_code=]`
  (ICIO composition + per-country output shares), `GET /api/countries`
- `GET /api/assumptions[?country_code=]` (registry with citations),
  `GET /api/limitations` (docs/model-limitations.md) — new in 0.12.0
- WDI: `GET /api/country/{code}/profile`, `/api/indicators`,
  `/api/timeseries`, `/api/comparison/{indicator}`
- Chat endpoints exist but are dormant (UI hidden)
- `GET /api/presets`: 15 curated scenarios (3 per country) with
  walkthrough narrations, defined in `presets_data.py` and verified by
  the test suite

### App Component (`frontend/src/App.jsx`)

4 tabs since 0.12.0 (AI Assistant remains hidden; Sankey, demographics,
job-quality, wage panels removed in 0.11.0 — their data was not
derivable from verified sources):
1. **Guided Tour (default)**: curated scenarios from
   `backend/app/api/presets_data.py`, run immediately with step-by-step
   walkthroughs; every walkthrough claim is enforced by
   `data-pipeline/tests/test_presets.py` against the engine
2. **Free Exploration**: controls (+ 3 model toggles, micro-sectors
   greyed below 0.5% of output, per-lever assumptions popovers,
   composition tooltips) + results with channel decomposition
3. **Country Data**: WDI indicators dashboard
4. **Methodology**: truthful model + data description

Plus: first-visit modal, persistent banner with the "what the model can
and cannot tell you" panel (served from `docs/model-limitations.md` via
`GET /api/limitations`), "approximately zero" headline framing when the
parameter range straddles zero, model-version stamp on results.

---

## Data Sources

### Status after the v0.10.0 audit (resolved in 0.11.0)
A code audit (June 2026) found that the multipliers hardcoded in
`tiva_multipliers.py` and the np.random I-O coefficients in
`economic_model.py` were NOT derived from the datasets they were
labelled with. Both files were DELETED in v0.11.0; the engine now runs
exclusively on the pipeline-verified country JSONs. The permanent record
of the old-vs-new comparison is
`data-pipeline/reports/comparison_multipliers.md`.

### Verified country data files (new, pipeline-derived)
`backend/app/data/countries/{ISO3}.json` — computed by `data-pipeline/`
from real datasets; full method and source manifest in
`data-pipeline/README.md` and `data-pipeline/sources.lock.json`:
- **OECD ICIO 2025 edition** (rev. Jan 2026), regular SML version,
  year 2022: A_d, A_m, Leontief inverses (Type I and Miyazawa Type II),
  output, VA, final demand, import shares
- **OECD Trade in Employment (TiM) 2025**: employment (EMPN) and
  compensation of employees (LABR) by industry
- **ILOSTAT**: national employment cross-check, labour force
- Substituted/capped cells registered in
  `backend/app/data/assumptions.json`

Built and validated: **ZAF, TUN, VNM, THA, SEN** (ZAF/TUN independently
verified after Session A; VNM/THA/SEN built in Session B). The engine
(`backend/app/models/engine.py`) reads ONLY these files since 0.11.0.

### Real data (World Bank WDI API), used by the dashboard
- Unemployment rates (total, youth, female, male), labour force, GDP,
  employment by broad sector, population

### Legacy values still driving the engine (to be deleted in Phase 2)
- `tiva_multipliers.py` hardcoded multipliers and demographic shares
- np.random technical-coefficient matrices in `economic_model.py`
- Stylized policy response functions and synergy multipliers

---

## Economic Model Details (v0.11.0 engine)

### Core
Demand-driven Leontief model on the verified 14-sector country data:
dE = ê L dF; direct = ê dF, indirect = ê (L_I − I) dF, induced =
ê (L_II − L_I) dF (Type II toggle, Miyazawa closure, consumption
propensity capped at 1, labelled an upper bound). dx = L dF;
dVA = (VA/x) ∘ dx. Comparative-static: no time scaling.

### Policy levers
- **Tariff** on sector s at rate t — four channels, decomposed in the
  response: (i) import substitution = |ε_s|·t·imports_s·absorption_s
  (imports and the domestic absorption share are data-derived per
  country); (ii) downstream cost: dp' = dp_m' A_m (I−A_d)^-1, demand
  falls by |η|·dp_j·F_j with F including exports; (iii) real-income loss
  through the household price index; (iv) optional stylised retaliation
  on the top-3 export sectors.
- **Sector support** (replaces "subsidy"): dF_s += rate·x_s; financing
  drag toggle (default on) subtracts the amount from household
  consumption.
- **SME/demand stimulus**: household-consumption-weighted injection ×
  first-round fiscal multiplier.
- Productivity lever REMOVED (0.11.0); time-horizon scaling REMOVED.

### Behavioural parameters (assumptions.json, all cited)
- Import demand elasticities: per-country import-weighted averages from
  Kee/Nicita/Olarreaga (2008) Table 1 (ZAF −1.16, TUN −1.06, THA −1.08);
  VNM −1.08 (not in KNO sample; global median); SEN −0.5 (calibrated to
  the bottom of the cited range; KNO's own −1.05 violates the acceptance
  constraint — reason recorded in the registry entry). Range for
  uncertainty display: [−0.5, −1.67].
- Own-price demand elasticity −0.5 [−0.25, −0.75] (USDA-ERS TB-1929),
  treated as compensated.
- Retaliation share 0.5, top-3 sectors (Fajgelbaum et al. 2020), toggle.
- Fiscal multiplier 0.5 [0.1, 1.0] (IMF Batini et al. 2014 buckets).

### Acceptance constraint (tested per country)
10% manufacturing tariff at defaults: net employment ≤ +0.05% of
baseline (actual: ZAF −0.011%, TUN −0.485%, VNM −0.732%, THA −0.226%,
SEN −0.019%); strictly negative with retaliation; protected-sector
gains ≥ 60% offset.

### 14 Sectors
agriculture, mining, manufacturing, textiles, automotive, food_processing, chemicals, construction, utilities, trade, transport, finance, public_services, other_services
(ICIO composition of each sector is in the country JSON metadata and the /api/sectors response)

---


## Recent Changes
See [CHANGELOG.md](CHANGELOG.md) for full version history.

---

---

## Environment Setup

### Requirements
- Python 3.10+ (tested with 3.14)
- Node.js 18+ (tested with 24.13)
- Anthropic API key (for AI chatbot, optional)

### API Key Setup
Create `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```
Get key from: https://console.anthropic.com/

### Manual Start (if start.bat fails)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## URLs

### Local Development
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

### Production (Render.com)
- Live site: https://policy-simulator-XXXX.onrender.com (check Render dashboard for actual URL)
- Protected by HTTP Basic Auth (credentials in Render environment variables)

---

## Deployment Workflow

To update the live website after making changes:
```bash
cd C:\Users\bernd\vibecode\policy-simulator
git add -A
git commit -m "Description of changes"
git push
```
Render auto-redeploys in 3-5 minutes. See `DEPLOYMENT.md` for full details.

---

## Data Pipeline (new in 0.10.0)

`data-pipeline/` (own venv, not deployed) computes the verified country
JSONs. Key commands (from `data-pipeline/`):
```powershell
.venv\Scripts\python run_pipeline.py --inspect   # ICIO structure discovery
.venv\Scripts\python run_pipeline.py ZAF TUN     # build country JSONs
.venv\Scripts\python -m pytest                   # 34-test validation suite
```
Raw OECD downloads live in `data-pipeline/raw/` (git-ignored). OECD
endpoints are behind a Cloudflare bot challenge: the ICIO zip and the two
TiM CSV exports must be downloaded in a normal browser into `raw/` (exact
URLs and filenames in `data-pipeline/README.md`). ILOSTAT downloads are
scripted. Pushing to main requires `pytest` green (CLAUDE.md rule 6).

---

## Resume Instructions

Open the project in Claude Code. CLAUDE.md at the project root is loaded automatically and contains workflow instructions. See CHANGELOG.md for version history and planned work.

The post-audit overhaul is COMPLETE (v1.0.0): verified data pipeline
(Session A), engine rebuild with cited parameters and acceptance gates
(Session B), didactic UI rebuild (Session C), CI + documentation
hygiene (Session D). Both external verifications passed. CI:
`.github/workflows/tests.yml` (pytest suite, API-contract smoke,
frontend build). The project is in maintenance mode; for changes,
follow the ground rules in CLAUDE.md (no invented numbers, registry
citations, push only after pytest green).

---


## Troubleshooting

### start.bat stops immediately
- Check Python/Node are in PATH: `python --version`, `node --version`
- Run commands manually per SETUP.txt

### Backend errors
- Delete `backend/venv` and let start.bat recreate it
- Check `backend/.env` exists with API key (for chatbot)
- Check `backend/requirements.txt` has compatible versions

### Frontend errors
- Delete `frontend/node_modules` and `frontend/package-lock.json`
- Run `npm install` again

### Low job numbers
- Verify `gdp_millions` in economic_model.py is correct (ZAF: 400000, TUN: 50000)
- Check `_calculate_demand_shocks()` uses GDP multiplication
- Ensure policy inputs are reasonable (e.g., 2% SME stimulus, not 0.02%)

### AI Assistant not working
- Check `backend/.env` has valid `ANTHROPIC_API_KEY`
- Verify API key has credits at console.anthropic.com

### Render deployment issues
- Check build logs in Render dashboard
- Verify environment variables are set (`AUTH_USERNAME`, `AUTH_PASSWORD`)
- Free tier spins down after 15 min inactivity — first load has ~30s cold start

---

## Model Limitations (Important!)

1. **Partial equilibrium only**: No general equilibrium feedback — no wage pressure, no crowding-out of private investment, no exchange-rate effects, no price-level changes (displayed as warning banner in UI since v0.8.0)
2. **Gross employment effects**: Results are gross, not net of economy-wide displacement (Stolper-Samuelson redistribution not modeled; disclaimer shown in UI)
3. **Simplified non-linearity**: Response curves are stylized, not econometrically estimated
4. **Simplified sectors**: 14 aggregated vs thousands in reality
5. **Stylized retaliation**: Trade retaliation is a simple penalty, not modeled dynamically
6. **Technical coefficients still stylized**: I-O linkages seeded with `np.random.seed(42)` for reproducibility (v0.8.0) but not from national I-O tables
7. **Mixed data quality** (signalled by badge in UI):
   - **Research-grade** (±10–15% confidence): ZAF, VNM, THA — OECD TiVA/ICIO 2023
   - **Illustrative** (±25–30% confidence): TUN, MOZ — stylized estimates from WDI/ILO

**This tool is for educational purposes only. Results are illustrative, not forecasts.**

---

## Project Structure (Updated)

```
policy-simulator/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py          # FastAPI endpoints
│   │   │   └── schemas.py         # Pydantic models (incl. DataSourceInfo)
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── tiva_multipliers.py # OECD TiVA employment multipliers
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── economic_model.py  # Core I-O simulation + non-linear effects
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── wdi_service.py     # World Bank API client
│   │   │   └── chat_service.py    # Claude AI integration
│   │   └── main.py                # FastAPI app + Basic Auth + static file serving
│   ├── requirements.txt
│   ├── .env                       # ANTHROPIC_API_KEY (local only, gitignored)
│   └── venv/
├── frontend/
│   └── ... (unchanged)
├── .gitignore
├── .dockerignore
├── Dockerfile                     # Multi-stage build for deployment
├── render.yaml                    # Render.com deployment config
├── CLAUDE.md                      # Claude Code workflow instructions (auto-loaded)
├── CHANGELOG.md                   # Version history (v0.1.0 → current)
├── DEPLOYMENT.md                  # Step-by-step deployment instructions
├── project_review_plan.md         # Multi-perspective review (sessions 12-13)
├── start.bat
├── start.sh
├── SETUP.txt
└── project_context.md             # This file — technical reference
```

---

*Last updated: March 2026 (v0.9.0)*
