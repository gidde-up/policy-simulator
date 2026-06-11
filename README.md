# Economic Policy Simulator

A **didactic** simulator of the employment effects of economic policy
choices, built for ITCILO training use. Learners (many of them policy
makers) explore the **direction, transmission channels and rough
magnitude** of policy effects in five economies: **South Africa,
Tunisia, Viet Nam, Thailand and Senegal**.

It is **not** a forecasting or decision-support tool, and it says so on
every screen.

## What it does

- **Guided Tour** (default view): 15 curated scenarios with step-by-step
  walkthroughs of what each result teaches. Every factual claim in the
  walkthroughs is enforced by automated tests against the model output.
- **Free Exploration**: three policy levers —
  - **Tariffs**, decomposed into four separately displayed channels:
    protected-sector gain (import substitution), downstream input-cost
    push, real-income loss, and an optional stylised retaliation toggle;
  - **Government sector support**, with a financing-drag toggle
    (tax-financed) so gross and net effects can be compared;
  - **SME / demand stimulus**, spread through household consumption and
    scaled by a cited first-round fiscal multiplier.
- Results show net employment with a **parameter range** (never a single
  point), direct/indirect/(induced) decomposition, per-sector effects,
  output and value-added changes, and fiscal flows. Induced (Type II)
  effects are an explicit toggle labelled as an upper bound. When the
  range straddles zero, the headline says so: *net effect approximately
  zero; the robust result is the gross reallocation*.
- **Country Data**: live World Bank WDI dashboard (the one genuinely
  real-time data source; everything in the model itself is static,
  versioned and reproducible).

## Where the numbers come from

The model core is a demand-driven Leontief input-output model computed
by a reproducible pipeline (`data-pipeline/`) from:

| Source | Edition | Used for |
|---|---|---|
| OECD Inter-Country Input-Output (ICIO) tables | 2025 edition (rev. Jan 2026), year 2022, regular version (80 economies + ROW) | inter-industry structure, final demand, imports, value added, Leontief inverses (Type I and Miyazawa Type II) |
| OECD Trade in Employment (TiM) | 2025 edition | employment and labour compensation by industry |
| ILOSTAT | bulk API | national employment cross-checks, labour force, per-cell fallbacks |
| World Bank WDI | live API | dashboard indicators only (not used inside the model) |

The 50 ICIO industries are aggregated to 14 didactic sectors by a
committed concordance (`data-pipeline/concordance_icio_to_14.csv`, one
row per industry with a rationale). Per-country model files live in
`backend/app/data/countries/*.json` with full source metadata, hashes
and access dates (`data-pipeline/sources.lock.json`).

**Ground rules** (enforced by tests):

- No invented numbers: every coefficient is computed from a named
  dataset by reproducible code, or carries a full citation in the
  assumptions registry (`backend/app/data/assumptions.json`). An AST
  test asserts the engine contains no numeric literal outside {0, 1, 2}.
- Behavioural parameters are cited and ranged: import demand
  elasticities per country (Kee, Nicita & Olarreaga 2008, Table 1),
  own-price demand elasticity (USDA-ERS TB-1929), retaliation share
  (Fajgelbaum et al. 2020), fiscal multiplier (IMF Batini et al. 2014).
- Acceptance constraint: under default parameters a unilateral tariff
  increase is never net employment-positive, in any country (automated
  per-country test, consistent with Flaaen & Pierce 2019 and Amiti,
  Redding & Weinstein 2019).
- The full audit trail of every substituted data cell and calibration
  decision is in the assumptions registry, surfaced in the UI as
  per-lever popovers.

The project history is candid: versions before 0.10.0 used hardcoded
multipliers falsely labelled as OECD data. They were deleted; the
comparison record is preserved in
`data-pipeline/reports/comparison_multipliers.md`.

## What the model cannot tell you

Comparative-static accounting at fixed 2022 prices and technology: no
supply constraints, no price/wage/exchange-rate responses, no dynamics,
no net labour-market outcomes, no within-sector distribution. The full
statement is in [`docs/model-limitations.md`](docs/model-limitations.md),
served in-app via the "what the model can and cannot tell you" panel.
Per-lever methodological notes: [`docs/levers/`](docs/levers/).

## Tech stack

- **Backend**: Python, FastAPI; the engine
  (`backend/app/models/engine.py`) is pure numpy over the static country
  JSONs — all data is loaded once at startup, runtime is matrix-vector
  products.
- **Frontend**: React 18, Vite, TailwindCSS, Recharts.
- **Data pipeline**: Python (pandas/numpy), own venv, not deployed.
- **AI assistant**: dormant. The backend chat endpoints exist but the UI
  is hidden; no LLM call is made during simulations.

## Quick start (local)

```bash
# backend (terminal 1)
cd backend
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# frontend (terminal 2)
cd frontend
npm install
npm run dev                       # open http://localhost:5173
```

No API keys are needed. `ANTHROPIC_API_KEY` in `backend/.env` is only
relevant to the dormant chat endpoints.

## Reproducing the data

See [`data-pipeline/README.md`](data-pipeline/README.md) for exact
commands, source URLs and the manual-download fallback (OECD endpoints
sit behind a bot challenge). Re-running the pipeline regenerates the
country JSONs; the validation suite gates every output.

## Tests and CI

```bash
cd data-pipeline
.venv\Scripts\python -m pytest    # validation + engine + preset suite
```

GitHub Actions (`.github/workflows/tests.yml`) runs the full pytest
suite, a backend API-contract smoke (including the tariff acceptance
constraint) and the frontend build on every push and pull request.
House rule: push to `main` (which auto-deploys) only after the suite is
green locally.

## Deployment

Render.com, auto-deploy from `main` (see `render.yaml`, `Dockerfile`,
[`DEPLOYMENT.md`](DEPLOYMENT.md)). Note for classroom use: on the Render
free tier the instance spins down when idle and a cold start takes about
a minute — use a paid instance or an external keep-alive ping before
sessions. `/health` is exempt from authentication.

## License

MIT License

## Acknowledgments

- OECD (ICIO tables, Trade in Employment database)
- ILO (ILOSTAT)
- World Bank (WDI API)
