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
- **Target Countries**: South Africa (ZAF) and Tunisia (TUN)
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
| Tunisia | Stylized estimates | Illustrative | N/A |

South Africa multipliers derived from OECD Inter-Country Input-Output tables with demographic shares from Stats SA Labour Force Survey.

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
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

---

## Resume Instructions

To continue development with Claude Code:

1. Open this folder in your terminal/IDE
2. Start a new Claude Code session
3. Say: "I'm continuing work on the economic policy simulator. Read PROJECT_CONTEXT.md for context."
4. Claude will read this file and understand the project state

### Potential Next Tasks
- ~~Integrate real OECD ICIO data~~ ✓ Done for ZAF employment multipliers
- **Full OECD ICIO integration**: Replace stylized technical coefficients with actual I-O matrices
- **Add cost analysis**: Fiscal cost per job, tariff revenue vs deadweight loss
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

---

## Model Limitations (Important!)

1. **Static model**: No dynamic adjustments or general equilibrium effects
2. **Simplified non-linearity**: Response curves are stylized, not econometrically estimated
3. **No price effects**: Doesn't model wage/price/exchange rate changes
4. **Simplified sectors**: 14 aggregated vs thousands in reality
5. **Stylized retaliation**: Trade retaliation is a simple penalty, not modeled dynamically
6. **Mixed data quality**: ZAF has OECD data, TUN uses stylized estimates
7. **Technical coefficients still stylized**: I-O linkages not from national tables

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
│   │   ├── data/                  # NEW: TiVA multiplier data
│   │   │   ├── __init__.py
│   │   │   └── tiva_multipliers.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── economic_model.py  # Core I-O simulation + non-linear effects
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── wdi_service.py     # World Bank API client
│   │   │   └── chat_service.py    # Claude AI integration
│   │   └── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env                       # ANTHROPIC_API_KEY
│   └── venv/
├── frontend/
│   └── ... (unchanged)
├── start.bat
├── start.sh
├── SETUP.txt
└── PROJECT_CONTEXT.md
```

---

*Last updated: January 2026*
