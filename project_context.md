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
- **Technical Coefficients Matrix**: Inter-industry linkages not from national I-O tables; seeded (`np.random.seed(42)`) for reproducibility
- **Sector GDP Shares**: Approximate proportions
- **Policy Response Functions**: Non-linear effects are stylized, not econometrically estimated
- **Confidence intervals**: OECD countries ±10–15%; stylized countries ±25–30% (data-quality-aware since v0.8.0)

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
| 0-1% | 1.0 |
| 1-2% | 0.90 |
| 2-3% | 0.82 |
| 3%+ | ~0.75 (absorption constraints) |
Source: IMF/World Bank empirical estimates for developing countries (v0.8.0)

**Productivity Investment:**
- Short-term (1yr): −0.15 multiplier (displacement effect dominates); no quality bonus
- Medium-term (3yr): +0.45 multiplier (competitiveness gains begin); +10% quality bonus
- Long-term (5yr): +1.0 multiplier (expanded markets dominate); +20% quality bonus
Source: Acemoglu & Restrepo (2018); direction corrected in v0.8.0

**Import Elasticities (sector-specific):**
agriculture −0.5, mining −0.6, manufacturing −1.5, textiles −2.0, automotive −1.8,
food_processing −0.8, chemicals −1.3, construction −0.7, utilities −0.4,
trade −1.0, transport −0.8, finance −0.5, public_services −0.3, other_services −0.6
Source: Kee, Nicita & Olarreaga (2008); replaces universal −1.2 constant in v0.8.0

**Policy Synergies:**
- 2 policies: +5% effectiveness (base bonus 1.05)
- 3 policies: +8% effectiveness (base bonus 1.08)
- 4 policies: implementation complexity penalty applies
- Complementary combos (subsidy + productivity, SME + moderate tariffs): additional +5%
- Non-complementary combos: −10% penalty
- Negative interaction: avg tariff >8% AND avg subsidy >8% triggers rent-seeking penalty (v0.8.0)

### 14 Sectors
agriculture, mining, manufacturing, textiles, automotive, food_processing, chemicals, construction, utilities, trade, transport, finance, public_services, other_services

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

## Resume Instructions

Open the project in Claude Code. CLAUDE.md at the project root is loaded automatically and contains workflow instructions. See CHANGELOG.md for version history and planned work.

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

*Last updated: March 2026 (v0.8.0)*
