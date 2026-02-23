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
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
├── SETUP.txt              # Manual setup instructions
└── PROJECT_CONTEXT.md     # This file
```

---

## Key Files Reference

### Economic Model (`backend/app/models/economic_model.py`)

The core simulation engine using Leontief Input-Output analysis.

**Key Components:**
- `gdp_millions`: Country GDP - South Africa = $400B, Tunisia = $50B
- `sector_shares`: 14 sectors with approximate GDP proportions
- `tech_coefficients`: Inter-industry linkage matrix (stylized)
- `employment_coefficients`: Jobs per million USD output by sector
- `leontief_inverse`: (I - A)^(-1) matrix for multiplier effects

**Key Methods:**
- `simulate_policy(scenario)`: Main entry point, returns employment effects
- `_calculate_demand_shocks(scenario)`: Converts policy % to million USD
- `_apply_employment_multipliers()`: Calculates direct/indirect/induced jobs
- `calculate_employment_multipliers()`: Returns Type I and Type II multipliers

**Policy Transmission:**
```
Policy Input → Demand Shock (million USD) → Leontief Inverse → Output Change → Employment Coefficients → Jobs
```

### Results Panel (`frontend/src/components/ResultsPanel.jsx`)

Displays simulation results with multiple visualizations:
- Total jobs created/lost with confidence interval
- Job breakdown: direct, indirect, induced
- Stacked bar chart: direct (blue) + indirect (purple) jobs by sector
- Before/after unemployment indicators with visual bars
- Demographic pie charts (gender, age, job quality)

**Key Component:** `UnemploymentIndicator` - Shows current vs projected rates with color-coded improvement/worsening badges.

### API Routes (`backend/app/api/routes.py`)

**Endpoints:**
- `POST /api/simulate`: Run policy simulation
- `GET /api/country/{code}/profile`: Fetch WDI indicators
- `GET /api/multipliers/{code}`: Get employment multipliers
- `POST /api/chat`: Natural language policy interpretation
- `GET /api/presets`: Preset policy scenarios
- `GET /api/comparison/{indicator}`: Compare countries over time

**Helper Function:** `get_baseline_indicators()` - Fetches WDI data and calculates projected unemployment changes based on job effects.

### Schemas (`backend/app/api/schemas.py`)

**Key Models:**
- `PolicyScenarioRequest`: Input parameters (tariffs, subsidies, etc.)
- `SimulationResponse`: Full results including `baseline_indicators`
- `BaselineIndicator`: current_value, projected_value, change, unit
- `BaselineIndicators`: unemployment_total, youth, female, male
- `EmploymentEffectResponse`: Jobs by type with demographic shares

### App Component (`frontend/src/App.jsx`)

Main application with 4 tabs:
1. **Policy Simulation**: Controls + Results + Sankey diagram
2. **Country Data**: WDI indicators dashboard
3. **AI Assistant**: Claude-powered chat interface
4. **Methodology**: Comprehensive disclaimer and model documentation

---

## Data Sources

### Real Data (World Bank WDI API)
Fetched in real-time:
- Unemployment rates (total, youth, female, male)
- Labor force size
- GDP figures
- Employment by sector (agriculture, industry, services)
- Population data

### Employment Multipliers
| Country | Source | Quality | Reference Year |
|---------|--------|---------|----------------|
| South Africa | OECD TiVA/ICIO 2023 | Research-grade | 2020 |
| Viet Nam | OECD TiVA/ICIO 2023 | Research-grade | 2020 |
| Thailand | OECD TiVA/ICIO 2023 | Research-grade | 2020 |
| Tunisia | Stylized estimates | Illustrative | N/A |
| Mozambique | World Bank WDI 2024 + ILO | Illustrative | 2023-2024 |

ZAF multipliers: OECD ICIO + Stats SA Labour Force Survey. VNM: OECD ICIO + GSO Labour Force Survey. THA: OECD ICIO + NSO Labour Force Survey. MOZ: Stylized estimates based on WDI employment data (69.5% agriculture, 95% informality), ILO statistics, and regional patterns from comparable low-income Sub-Saharan African economies.

### Still Stylized/Approximated
- **Technical Coefficients Matrix**: Inter-industry linkages (not from national I-O tables)
- **Sector GDP Shares**: Approximate proportions
- **Policy Response Functions**: Non-linear effects are stylized, not econometrically estimated

---

## Economic Model Details

### Leontief Input-Output Framework

**Core Equation:**
```
X = (I - A)^(-1) × ΔD
```
Where:
- X = Total output change
- A = Technical coefficients matrix
- ΔD = Final demand change (from policy)
- (I - A)^(-1) = Leontief inverse

**Employment Calculation:**
```
Jobs = Σ (output_change × employment_coefficient × time_scale)
```

### Employment Multipliers

| Type | Description |
|------|-------------|
| Direct | Jobs in targeted sectors |
| Indirect | Jobs in supply chain (Type I = Direct + Indirect) |
| Induced | Jobs from consumer spending (Type II = Type I + Induced) |

### Policy Response Functions (Non-Linear)

**Tariffs:**
| Level | Effective Elasticity | Notes |
|-------|---------------------|-------|
| 0-10% | 0 → 0.35 (linear) | Optimal range |
| 10-20% | 0.35 → 0.15 (decay) | Diminishing returns |
| 20%+ | < 0.15, eventually negative | Retaliation, inefficiency |

Export-oriented sectors (automotive, textiles, manufacturing, chemicals) face additional penalty above 15%.

**Subsidies:**
| Level | Elasticity | Constraint |
|-------|------------|------------|
| 0-5% | 0.9 | Full effectiveness |
| 5-10% | 0.9 → 0.6 | Diminishing returns |
| 10-15% | 0.6 → 0.3 | Rent-seeking |
| 15%+ | 0.3 → 0.1 | Fiscal crowding-out if total >30% |

**SME Stimulus:**
| % of GDP | Fiscal Multiplier |
|----------|------------------|
| 0-1% | 1.5 |
| 1-2% | 1.35 |
| 2-3% | 1.15 |
| 3%+ | ~1.0 (absorption constraints) |

**Productivity Investment:**
- Short-term (1yr): 0.2 effectiveness, no quality bonus
- Medium-term (3yr): 0.6 effectiveness, +10% quality bonus
- Long-term (5yr): 1.0 effectiveness, +20% quality bonus

**Policy Synergies:**
- 2 policies: +10% effectiveness
- 3 policies: +15% effectiveness (optimal)
- 4 policies: +10% (implementation complexity)
- Complementary combos: additional +5% each
- Non-complementary combos: -10% penalty

### 14 Sectors
agriculture, mining, manufacturing, textiles, automotive, food_processing, chemicals, construction, utilities, trade, transport, finance, public_services, other_services

---

## Recent Changes (Session History)

### Session 1: Initial Build
- Created full-stack application structure
- Implemented Leontief I-O model
- Built React frontend with Recharts visualizations
- Integrated World Bank WDI API
- Added Claude chatbot integration

### Session 2: Fixes and Enhancements
1. **Fixed job creation numbers** - Model was returning percentages instead of USD millions
   - Added `gdp_millions` and `sector_shares` to economic model
   - SME stimulus now correctly calculated (e.g., 2% of $400B = $8B injection)

2. **Added sectoral employment graphs** - Stacked bar chart showing direct/indirect jobs

3. **Added before/after unemployment visualization** - Shows current vs projected rates with:
   - Color-coded improvement/worsening badges
   - Visual progress bars
   - Disaggregated by total, youth, female, male

4. **Fixed start.bat** - Script was stopping early; added error handling and absolute paths

5. **Added Methodology tab** - Comprehensive disclaimer explaining:
   - What data is real vs. stylized
   - Model methodology (Leontief I-O)
   - Known limitations (5 listed)
   - Appropriate vs inappropriate use cases
   - Recommendations for better estimates

6. **Updated footer** - Clear "Educational tool only" warning with link to Methodology

### Session 3: Project Relocation
- Moved project from `C:\Users\bernd\policy-simulator` to `C:\Users\bernd\vibecode\policy-simulator`
- Verified all scripts use relative paths (location-independent)
- Updated PROJECT_CONTEXT.md with new path
- Old folder partially deleted (venv has locked files - delete manually after closing any running servers)

### Session 4: Model Realism Improvements
1. **Non-linear policy effects** - Replaced linear elasticities with realistic response curves:
   - **Tariffs**: Optimal range 8-12%, diminishing returns above, negative effects above ~22%
   - **Subsidies**: Elasticity drops from 0.9 (at 5%) to 0.1 (at 20%+), fiscal crowding-out
   - **SME Stimulus**: Fiscal multiplier declines from 1.5 (1% GDP) to 1.0 (4%+ GDP)
   - **Productivity**: Time-dependent effects, job quality bonus in long term

2. **Policy synergy system** - Balanced mixes (2-3 policies) get 10-15% bonus:
   - Complementary: Subsidies + Productivity (+5%), SME + moderate tariffs (+5%)
   - Non-complementary: High tariffs without productivity (-10%)

3. **Trade retaliation** - Aggregate tariffs >50% trigger retaliation penalty (up to -30%)

4. **UI improvements**:
   - Time horizon selector moved outside policy tabs (always visible)
   - Updated Methodology tab with non-linear effects documentation

### Session 5: OECD TiVA Data Integration
1. **Employment multipliers upgraded**:
   - **South Africa**: Now uses OECD TiVA/ICIO 2023 data (reference year 2020) - research-grade
   - **Tunisia**: Stylized estimates (not in OECD ICIO) - clearly marked as illustrative

2. **New data module** (`backend/app/data/tiva_multipliers.py`):
   - Pre-calculated Type I and Type II multipliers by sector
   - Demographic shares from Stats SA Labour Force Survey (ZAF)
   - `is_tiva_available()` function for data source transparency

3. **Data source transparency**:
   - API response includes `data_source` field with quality indicator
   - Results panel shows green badge (OECD) or amber badge (stylized)
   - Methodology tab updated with data source details

### Session 6: Cost-Benefit Analysis
1. **Fiscal and economic cost calculations** added to economic model:
   - **Tariff revenue**: Accounts for import reduction via demand elasticity (-1.2)
   - **Deadweight loss**: Harberger triangle calculation for efficiency costs
   - **Subsidy/SME/Productivity costs**: Direct fiscal spending

2. **Key insight implemented**: Tariffs generate revenue but also create economic costs:
   - Import reduction reduces actual revenue vs. naive calculation
   - Deadweight loss represents consumer/producer surplus destruction
   - Even "profitable" tariffs have hidden economic costs

3. **New metrics**:
   - **Fiscal cost per job**: Government budget impact per job (can be negative = revenue)
   - **Economic cost per job**: Total welfare cost including DWL (always positive)

4. **Frontend updates**:
   - New "Cost-Benefit Analysis" section in results panel
   - Fiscal impact breakdown (tariff revenue, subsidies, SME, productivity)
   - Warning note about tariff revenue illusion

5. **Example outputs**:
   | Scenario | Jobs | Net Fiscal | $/Job (Fiscal) | $/Job (Economic) |
   |----------|------|------------|----------------|------------------|
   | 10% manufacturing tariff | 112K | +$1.5B | -$13K (revenue) | $1,077 |
   | Mixed policy | 1.27M | -$4.1B | $3,237 | $5,686 |

### Session 7: Web Deployment
1. **HTTP Basic Auth** added to `backend/app/main.py`:
   - Shared username/password protection via browser login popup
   - Credentials configured via environment variables (`AUTH_USERNAME`, `AUTH_PASSWORD`)
   - Auth is skipped when env vars are not set (local development unchanged)
   - Health check endpoint (`/health`) exempted for Render monitoring

2. **Frontend served from FastAPI**:
   - Built React app (`frontend/dist/`) served as static files from the backend
   - SPA catch-all route returns `index.html` for non-API paths
   - Path resolution supports both local dev and Docker container layouts

3. **Docker deployment**:
   - Multi-stage `Dockerfile`: Node builds frontend, Python serves everything
   - `.dockerignore` excludes dev files (venv, node_modules, .env)

4. **Render.com hosting**:
   - `render.yaml` blueprint for one-click deploy (free tier)
   - Environment variables: `AUTH_USERNAME`, `AUTH_PASSWORD`, `ANTHROPIC_API_KEY`
   - Auto-redeploys on every push to `main`

5. **Git/GitHub**:
   - Repository: `https://github.com/gidde-up/policy-simulator` (private)
   - `.gitignore` for Python/Node/env files

6. **Deployment instructions**: See `DEPLOYMENT.md`

### Session 8: New Countries + Results Enhancements
1. **Added Viet Nam (VNM)** — lower-middle-income, OECD ICIO coverage:
   - GDP: $450B, 14 sectors with VNM-specific shares (GSO national accounts)
   - TiVA employment multipliers (research-grade, OECD ICIO 2023)
   - Demographic shares from GSO Viet Nam Labour Force Survey
   - Country-specific I-O matrix (textiles/electronics/agriculture linkages)
   - 3 preset scenarios: Electronics Hub, Textile Export, Rural Development

2. **Added Thailand (THA)** — upper-middle-income, OECD ICIO coverage:
   - GDP: $515B, 14 sectors with THA-specific shares (NESDC national accounts)
   - TiVA employment multipliers (research-grade, OECD ICIO 2023)
   - Demographic shares from NSO Thailand Labour Force Survey
   - Country-specific I-O matrix (automotive supply chain, tourism linkages)
   - 3 preset scenarios: Automotive Hub, Tourism Recovery, Food Processing

3. **Jobs created % indicator**: Total jobs figure now shows percentage of labour force

4. **Fiscal impact % of public budget**: Net fiscal impact now shows percentage of annual government expenditure (fetched from WDI indicator `GC.XPN.TOTL.GD.ZS`)

5. **Files modified** (10 backend + 3 frontend):
   - `tiva_multipliers.py`: VIETNAM_TIVA, THAILAND_TIVA data dictionaries
   - `economic_model.py`: GDP, sector shares, `_load_vietnam_io()`, `_load_thailand_io()`
   - `routes.py`: Validation, 6 presets, gov expenditure in baseline indicators
   - `wdi_service.py`: VNM/THA supported countries, `gov_expenditure` WDI indicator
   - `chat_service.py`: VNM/THA economic context in AI prompt
   - `schemas.py`: Country code description, `gov_expenditure_usd` field
   - `main.py`: Docstring
   - `Header.jsx`: 4 country buttons
   - `App.jsx`: Country label lookup
   - `PresetScenarios.jsx`: VNM/THA fallback presets
   - `ResultsPanel.jsx`: % of labour force, % of public expenditure

### Session 9: Mozambique Integration
1. **Added Mozambique (MOZ)** — low-income economy with high agriculture dependence:
   - **Economic context**: 69.5% employment in agriculture, 95% informality, emerging LNG sector
   - **Data sources**: World Bank WDI 2024, ILO labor force statistics
   - **Employment multipliers**: Stylized estimates based on regional patterns:
     - Very high labor intensity in agriculture (168 jobs/$1M)
     - Extremely low in extractives/mining (8 jobs/$1M) - capital-intensive LNG/coal
     - High informality across all sectors (74-92% in most sectors)
     - Strong agricultural linkages in food processing (72 jobs/$1M)

2. **Three policy scenarios** designed to test structural transformation:
   - **Agricultural Focus**: Support existing agriculture/commodity sectors (cashews, sugar, cotton)
     - Expected impact: Moderate (high labor intensity but limited linkages)
   - **Commodity Extraction**: Develop natural gas, coal, and mineral extraction
     - Expected impact: LOWEST (mining only 8 jobs/$1M, capital-intensive)
   - **Industrialization Drive**: Push manufacturing, textiles, higher value-added production
     - Expected impact: HIGHEST (targets labor-intensive sectors: textiles 124 jobs/$1M, construction 84 jobs/$1M, food processing 72 jobs/$1M, manufacturing 55 jobs/$1M)

3. **Model validation criteria**: If working correctly, simulations should show:
   - Total jobs created: Industrialization > Agriculture > Extraction
   - Reflects real development challenge: natural gas boom creates minimal jobs despite high revenues

4. **Frontend fixes**:
   - Added emoji font support for proper flag rendering (🇲🇿)
   - Updated CSS with "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji" font stack

5. **Files modified** (5 backend + 4 frontend):
   - **Backend**:
     - `tiva_multipliers.py`: Added MOZAMBIQUE_STYLIZED multipliers with sector-specific data
     - `wdi_service.py`: Added MOZ to SUPPORTED_COUNTRIES
     - `routes.py`: Added 3 Mozambique preset scenarios to PRESET_SCENARIOS list + fixed country validation to accept MOZ
     - `economic_model.py`: Added MOZ GDP ($22.75B) and sector shares (30% agriculture, 20% trade, reflecting WDI structure)
   - **Frontend**:
     - `Header.jsx`: Added Mozambique to country selector with flag emoji
     - `PresetScenarios.jsx`: Added MOZ fallback presets (agriculture, extractives, industrialization)
     - `CountryDashboard.jsx`: Added MOZ to comparison charts
     - `index.html` + `index.css`: Added emoji font support for cross-browser flag rendering

6. **Key fixes applied**:
   - **Country validation**: Added "MOZ" to hardcoded validation lists in `/api/simulate` and `/api/multipliers/{code}` endpoints
   - **GDP and sector shares**: Added Mozambique-specific economic structure to economic model (30% agriculture, 5% mining/LNG, 7% manufacturing, 20% trade)
   - **Employment multipliers**: All 14 sectors with Mozambique-specific labor intensity and demographic shares (high informality, female/youth participation)

7. **Documentation**:
   - Created `MOZAMBIQUE_UPDATE.md` with setup instructions
   - Created `MOZAMBIQUE_SCENARIOS.md` with detailed expected employment impacts and policy implications
   - Created `MOZAMBIQUE_ANALYSIS.md` documenting why agriculture creates more jobs than industrialization (sector size dominance issue)

### Session 10: Job Quality Metrics Integration
1. **Problem identified**: Agriculture scenarios create MORE jobs than industrialization for Mozambique, but agricultural jobs have:
   - 88% informality (vs 26% for manufacturing)
   - ~85% working poverty risk (vs ~30% for manufacturing)
   - $3,500/worker productivity (vs $12,000+ for manufacturing)

2. **Job quality metrics added** to distinguish quantity vs quality of jobs:
   - **Formalization rate**: % of jobs that are formal (formal/informal breakdown)
   - **Working poverty risk**: % of jobs below poverty line based on sector poverty rates
   - **Productivity**: Average output per worker (USD/year) by sector
   - **Sector composition**: Jobs by agriculture, manufacturing, services

3. **Backend changes**:
   - **schemas.py**: New `JobQualityMetrics` schema with 13 fields tracking formalization, poverty, and productivity
   - **economic_model.py**: New `_calculate_job_quality_metrics()` method with:
     - Sector-specific working poverty rates (85% agriculture, 70% trade, 30% manufacturing, 10% finance)
     - Sector-specific productivity estimates ($3.5K agriculture to $28K finance)
     - Formal/informal job disaggregation
     - High/medium/low productivity categorization
   - **chat_service.py**: Updated system prompt to include Mozambique context

4. **Frontend changes**:
   - **ResultsPanel.jsx**: New "Job Quality Analysis" section with:
     - Three metric cards (Formalization, Working Poverty Risk, Productivity)
     - Color-coded by quality level (green/amber/red)
     - Sector composition horizontal bar chart
     - Interpretation note explaining trade-offs
   - Displayed prominently after main employment impact, before job breakdown

5. **Data sources for job quality estimates**:
   - **Working poverty**: ILO Statistics, World Bank Poverty & Equity Database
   - **Productivity**: Typical sector GDP per worker in developing economies
   - **Informality**: From existing TIVA multipliers (informal_share)

6. **Files modified** (3 backend + 1 frontend):
   - Backend: `schemas.py`, `economic_model.py`, `chat_service.py`
   - Frontend: `ResultsPanel.jsx`

7. **Documentation**:
   - Created `JOB_QUALITY_METRICS.md` with detailed methodology and interpretation guide

8. **Impact on analysis**: Now scenarios can be compared on:
   - **Quantity**: Total jobs created (agriculture wins for Mozambique)
   - **Quality**: Formalization, productivity, poverty risk (manufacturing wins)
   - Supports structural transformation narrative: fewer but better jobs

### Session 11: UI Clarifications & Technical Documentation

1. **Industrial Policy slider label clarified**:
   - Unit changed from `%` to `% of sector GDP`
   - Description updated: "Share of manufacturing sector GDP invested in industrial upgrading...Targets manufacturing, automotive, chemicals, and food processing."
   - File: `frontend/src/components/PolicyControls.jsx`

2. **Full Technical Model Documentation added** (Methodology tab):
   - Collapsible panel at bottom of Methodology tab ("Full Technical Model Documentation")
   - Hidden by default; shown on click — does not clutter main interface
   - 12 sections covering all model components:
     1. Core Leontief framework and equations (L = (I−A)⁻¹, Δemployment = e·L·Δd)
     2. 14 sectors list
     3. Employment multiplier types and data sources per country
     4. Country GDP and sector shares table (all 5 countries)
     5. Policy transmission equations for all four levers
     6. Policy synergy multiplier logic
     7. Time horizon scaling table (direct/indirect/induced by horizon)
     8. Demographic disaggregation methodology
     9. Job quality metrics calculations (formalization, poverty risk, productivity)
     10. Cost-benefit analysis formulas (incl. Harberger triangle for DWL)
     11. Technical coefficients matrix assumptions and country-specific linkages
     12. Uncertainty and confidence interval methodology
   - Includes timestamp; to be updated with each model change
   - File: `frontend/src/App.jsx`

3. **Files modified** (2 frontend):
   - `frontend/src/components/PolicyControls.jsx`
   - `frontend/src/App.jsx`

4. **Deployed**: Commit `98663c8` pushed to `gidde-up/policy-simulator` → auto-deployed via Render

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

## Resume Instructions

To continue development with Claude Code:

1. Open this folder in your terminal/IDE
2. Start a new Claude Code session
3. Say: "I'm continuing work on the economic policy simulator. Read PROJECT_CONTEXT.md for context."
4. Claude will read this file and understand the project state

### Potential Next Tasks
- ~~Integrate real OECD ICIO data~~ ✓ Done for ZAF employment multipliers
- ~~Add cost analysis~~ ✓ Done (fiscal cost per job, tariff revenue vs deadweight loss)
- ~~Deploy to web with access protection~~ ✓ Done (Render.com + HTTP Basic Auth)
- **Full OECD ICIO integration**: Replace stylized technical coefficients with actual I-O matrices
- Add more countries (requires OECD ICIO coverage or regional estimates)
- Add scenario comparison (side-by-side results)
- Export results to PDF/Excel
- Implement CGE model for more accurate dynamic results

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

1. **Static model**: No dynamic adjustments or general equilibrium effects
2. **Simplified non-linearity**: Response curves are stylized, not econometrically estimated
3. **No price effects**: Doesn't model wage/price/exchange rate changes
4. **Simplified sectors**: 14 aggregated vs thousands in reality
5. **Stylized retaliation**: Trade retaliation is a simple penalty, not modeled dynamically
6. **Mixed data quality**:
   - **Research-grade**: ZAF, VNM, THA use OECD TiVA/ICIO 2023 data
   - **Illustrative**: TUN, MOZ use stylized estimates based on regional patterns and WDI/ILO data
7. **Technical coefficients still stylized**: I-O linkages not from national tables (except country-specific adjustments for VNM, THA)

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
├── DEPLOYMENT.md                  # Step-by-step deployment instructions
├── start.bat
├── start.sh
├── SETUP.txt
└── PROJECT_CONTEXT.md
```

---

*Last updated: February 2026*
