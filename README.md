# Economic Policy Simulator for Job Creation

An interactive, educational tool for policymakers to explore the employment effects of economic policy choices. Currently supports **South Africa** and **Tunisia**.

## Features

- **Policy Simulation**: Model tariff, subsidy, SME stimulus, and industrial policy effects on employment
- **Input-Output Analysis**: Uses Leontief multipliers to calculate direct, indirect, and induced job effects
- **Real Data Integration**: Fetches live data from World Bank WDI API
- **Demographic Disaggregation**: Results broken down by gender, age (youth vs adult), and job quality (formal vs informal)
- **Interactive Visualizations**: Sankey flow diagrams showing policy transmission mechanisms
- **AI Assistant**: Natural language interface powered by Claude for policy interpretation
- **Preset Scenarios**: Quick-start with pre-configured policy packages

## Screenshots

The tool provides three main views:
1. **Policy Simulation** - Adjust policy levers via sliders and see projected employment effects
2. **Country Data** - View real economic indicators from World Bank WDI
3. **AI Assistant** - Ask policy questions in natural language

## Tech Stack

- **Frontend**: React 18, Vite, TailwindCSS, Recharts
- **Backend**: Python 3.11+, FastAPI, NumPy/Pandas
- **Data Sources**: World Bank WDI API, OECD ICIO Tables
- **AI**: Anthropic Claude API (optional)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd policy-simulator
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Set up the frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

4. **(Optional) Configure AI Assistant:**
   Create a `.env` file in the backend folder:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

### Running the Application

1. **Start the backend (terminal 1):**
   ```bash
   cd backend
   venv\Scripts\activate  # or source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start the frontend (terminal 2):**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5173`

## Project Structure

```
policy-simulator/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes and schemas
│   │   ├── models/        # Economic model (I-O analysis)
│   │   ├── services/      # WDI API, Chat services
│   │   └── main.py        # Application entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client
│   │   └── App.jsx        # Main application
│   └── package.json
│
└── README.md
```

## Economic Model

### Input-Output Analysis

The model uses **Leontief Input-Output analysis** to calculate employment multipliers:

1. **Direct Effects**: Jobs created directly in the targeted sector
2. **Indirect Effects**: Jobs created in upstream supply chain sectors
3. **Induced Effects**: Jobs created from household spending of new wages

### Policy Transmission

```
Policy Change → Sector Demand Shock → Output Multiplier → Employment Effect
     ↓                                       ↓
  Tariff/Subsidy                    Leontief Inverse Matrix
  SME Stimulus                      Employment Coefficients
  Industrial Policy                 Demographic Shares
```

### Employment Multipliers

The model calculates two types of multipliers:
- **Type I**: Direct + Indirect effects
- **Type II**: Direct + Indirect + Induced effects

### Key Assumptions

| Parameter | Description | Source |
|-----------|-------------|--------|
| Employment coefficients | Jobs per $1M output by sector | ILO, OECD TiM |
| Inter-industry flows | Technical coefficients matrix | OECD ICIO |
| Induced multiplier | 1.4x for developing countries | Literature |
| Tariff elasticity | 0.3 (10% tariff → 3% demand) | Trade studies |

## Data Sources

### World Bank WDI API
- Base URL: `https://api.worldbank.org/v2/`
- Indicators: Employment, unemployment, labor force, GDP, sectoral composition
- Updates: Quarterly

### OECD ICIO Tables
- Inter-Country Input-Output tables
- 45 industries (ISIC Rev.4)
- Both South Africa and Tunisia included

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulate` | POST | Run policy simulation |
| `/api/multipliers/{country}` | GET | Get employment multipliers |
| `/api/country/{code}/profile` | GET | Get country economic profile |
| `/api/chat` | POST | Natural language policy query |
| `/api/presets` | GET | Get preset scenarios |

## Limitations & Caveats

This is a **didactic tool** designed for educational purposes:

1. **Simplified Model**: Uses stylized I-O coefficients, not full econometric estimation
2. **Static Analysis**: Does not model dynamic adjustment processes
3. **Partial Equilibrium**: Does not account for general equilibrium effects
4. **No Behavioral Response**: Assumes fixed technical coefficients
5. **Uncertainty**: Results include ±15-20% confidence intervals

**Results should be interpreted as illustrative, not precise forecasts.**

## Contributing

Contributions welcome! Areas for improvement:
- Add more countries
- Integrate actual OECD ICIO data files
- Add more policy levers (exchange rate, interest rate)
- Improve demographic employment shares with micro-data
- Add scenario comparison features

## License

MIT License

## Acknowledgments

- World Bank for the WDI API
- OECD for Input-Output methodology and tables
- ILO for employment data standards
