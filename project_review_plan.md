# PROJECT REVIEW — Economic Policy Simulator
**Reviewing as:** Multi-perspective analyst (Coder + Economist + Educator)
**Source:** Full codebase exploration at `c:\Users\bernd\vibecode\policy-simulator`
**Date:** 2026-03-05
**Depth:** Standard (with web research on best practices)

---

## BEST PRACTICES CONTEXT (from research)

1. **Transparency over precision** — Educational simulators must clearly bound what is modeled vs. excluded. Users must understand they are running thought experiments, not forecasts.
2. **Defensible parameterization** — Assumptions should be explicitly sourced (OECD, ILO, WDI), not embedded silently. Stylized values need labeling.
3. **Prediction-Experience-Reflection cycle** — Didactic tools work best when learners predict outcomes first, then compare. The tool currently skips the "predict" phase.
4. **Explicit exclusion criteria** — State clearly what is NOT modeled (distributional effects within countries, political economy constraints, environmental impacts, macro feedback loops).
5. **Multi-format feedback** — Results should be readable as both narrative and numbers; current tool is numbers-heavy, narrative-light.

---

## PERSPECTIVE 1: CODER / PROGRAMMER

### Strengths
- Clean FastAPI + React architecture with good separation of concerns
- Pydantic validation on all I/O; async endpoints throughout
- OECD TiVA multipliers for 3 countries are research-grade data
- Deployed to production (Render.com) with auth middleware

### Weaknesses & Gaps

**[Red] Technical coefficients matrix is randomly generated**
- File: `backend/app/models/economic_model.py`, method `_load_*_io()`
- `np.random.uniform(0.01, 0.05, (n, n))` — random on every instantiation
- This means indirect employment effects (the largest share of output) are not reproducible and have no empirical basis
- Fix: Seed with a fixed value (`np.random.seed(42)`) as minimum; ideally replace with OECD ICIO coefficients

**[Red] Confidence intervals are arbitrary constants**
- File: `economic_model.py` ~line 506-521
- `±15%` for most sectors, `±20%` for agriculture — not statistically derived
- A tool built on OECD data for ZAF should show narrower intervals than one using stylized data for MOZ
- Fix: Tie interval width to data quality flag (`data_source.quality_score`); OECD-backed = ±10%, stylized = ±25-30%

**[Yellow] Import elasticity hardcoded as universal constant**
- `import_elasticity = -1.2` applied to all sectors in `_calculate_policy_costs()`
- Reality: agriculture ~-0.5, manufacturing ~-1.5, textiles ~-2.0
- Fix: Add sector-specific elasticity dictionary in `tiva_multipliers.py`

**[Yellow] Induced multiplier flat across all sectors**
- `self.induced_multiplier = 1.4` (constant, `economic_model.py`)
- Finance workers earning $28,000/yr have far higher induced consumption than agriculture workers at $3,500/yr
- Fix: Weight induced multiplier by sector productivity (already calculated in job quality metrics)

**[Yellow] No input validation on policy extremes at API level**
- Pydantic schemas accept any float for tariff/subsidy values
- A tariff of 150% would produce numerical artifacts in the non-linear curve
- Fix: Add `ge=0, le=100` validators in `schemas.py`; add `le=30` for subsidies

**[Yellow] WDI service silently drops missing indicators**
- `wdi_service.py` skips missing fields without flagging to user
- If World Bank API changes or country data is incomplete, results degrade silently
- Fix: Return partial-data warnings in `CountryProfileResponse`

**[Green] No automated tests**
- No test suite exists (no `tests/` directory)
- Fix: Add at minimum 3 unit tests: (1) simulate_policy returns plausible jobs, (2) non-linear tariff curves behave correctly at boundaries, (3) cost-benefit calculation is consistent

**[Green] Frontend build not validated at startup**
- `main.py` serves `frontend/dist/` without checking it exists; users get API docs instead of UI
- Fix: Check at startup and log a clear warning if `dist/` is missing

---

## PERSPECTIVE 2: ECONOMIST

### Strengths
- Leontief I-O framework is theoretically sound for short/medium-run employment analysis
- Non-linear policy effects (tariff Laffer curve, subsidy diminishing returns) reflect real economic theory
- Type I vs Type II multiplier distinction is correct and educationally valuable
- Job quality metrics (formality, poverty risk, productivity) add distributional dimension often absent from aggregate employment models
- Deadweight loss calculation uses correct Harberger triangle formula

### Weaknesses & Gaps

**[Red] No general equilibrium feedback — severe limitation not clearly communicated**
- Leontief I-O is a fixed-price, demand-driven model. It cannot capture:
  - Wage pressure from labor market tightening
  - Crowding out of private investment by fiscal stimulus
  - Exchange rate effects of tariffs (critical for export-dependent countries like VNM, THA)
  - Price level changes from tariff protection
- The tool currently treats all employment gains as additive with no resource constraints
- Fix: Add a prominent "Model Boundaries" warning in ResultsPanel before results; make it dismissible but not skippable on first use

**[Red] Tariff employment effects are theoretically incomplete**
- Tariffs raise output in protected sector but also raise input costs for downstream sectors
- The model captures upstream linkages (Leontief) but the tariff cost shock to downstream users is missing
- Example: A 20% textile tariff raises textile output but also raises input costs for apparel manufacturers — net employment effect is ambiguous
- Fix: Add downstream cost penalty term to tariff demand shock calculation; this would significantly change tariff results

**[Red] Productivity investment modeled as demand stimulus, not supply-side shift**
- Currently: productivity investment → demand increase → more jobs (Keynesian)
- Correct: productivity investment → labor productivity increase → potentially fewer jobs per unit of output but more competitive output, higher wages, new sectors
- The model gives productivity a positive employment effect at all time horizons, which contradicts standard economic theory (automation risk, displacement)
- Fix: For short-term, productivity investment should have near-zero or slightly negative employment impact; positive effects should emerge only at medium/long term via competitiveness gains

**[Yellow] SME stimulus fiscal multiplier values are high**
- Multipliers of 1.5 for SME stimulus (0-1% GDP) exceed most empirical estimates for developing countries
- IMF/World Bank literature: fiscal multipliers in developing countries typically 0.5-1.0 (lower due to import leakage, financing constraints)
- Fix: Reduce multipliers to 0.8-1.2 range; add country-specific calibration (Vietnam and Thailand have higher multipliers than South Africa due to import content)

**[Yellow] Policy synergy multiplier is theoretically underdeveloped**
- The synergy bonus (+5-15%) for combining policies has no empirical basis
- In practice, policy interactions can be negative (tariffs + subsidies = rent-seeking, not synergy)
- Fix: Replace flat synergy bonus with specific interaction terms: tariff × subsidy should have negative interaction beyond threshold; subsidy × productivity should be positive

**[Yellow] No distinction between employment creation and employment redistribution**
- The model reports new jobs, but many "new" jobs in protected sectors may simply be redistributed from more productive unprotected sectors
- This is the core Stolper-Samuelson result: protection creates jobs in import-competing sectors by destroying jobs elsewhere
- Fix: Add a footnote/disclaimer that employment effects shown are gross, not net of economy-wide displacement

**[Yellow] Country parameterization asymmetric in quality**
- ZAF, VNM, THA: OECD TiVA data (research-grade)
- TUN, MOZ: Stylized estimates (lower confidence)
- This difference is acknowledged in documentation but not visually signaled in results
- Fix: Add data quality badge in ResultsPanel header; color-code confidence intervals by data quality

**[Green] Working poverty risk thresholds not specified**
- "Working poverty risk" is calculated but the income threshold is not displayed ($1.90/day? $3.20/day? $6.85/day?)
- Fix: Display the poverty line used and its source (World Bank international poverty lines)

**[Green] No labor market context (labor supply elasticity)**
- The model assumes jobs created = jobs filled, with no consideration of whether the labor supply exists
- In Vietnam and Thailand (near full employment), additional jobs may require wage increases or migration
- Fix: Add labor market tightness indicator to CountryDashboard

---

## PERSPECTIVE 3: USER / LEARNER (Didactic Quality)

### Strengths
- Clean, tabbed UI that separates input, output, and explanation
- AI assistant (ChatPanel) lowers barrier for non-technical users
- Preset scenarios provide guided starting points
- Methodology tab with technical documentation shows transparency

### Weaknesses & Gaps

**[Red] No guided learning path — tool is a dashboard, not a lesson**
- Users face all sliders simultaneously with no scaffold for what to explore first
- No question posed to the learner ("What do you predict will happen if...?")
- No comparison of user prediction vs. model result
- Fix: Add an optional "Guided Mode" with 3-4 structured exercises per country, each framed as a question with a learning objective. Could be a simple step-by-step sidebar.

**[Red] Results are number-heavy with weak narrative interpretation**
- ResultsPanel shows 8+ sections of data simultaneously
- A user with no economics background cannot determine if "+47,000 jobs" is good, bad, or typical
- The AI explanation endpoint exists (`/api/explain`) but is not surfaced automatically after each simulation
- Fix: Auto-trigger a brief (3-sentence) AI interpretation after each simulation run, displayed above the numbers. Keep the full detail below.

**[Yellow] Policy levers lack real-world anchoring**
- "15% tariff on manufacturing" is abstract without context: What does the current tariff rate look like? What do comparator countries charge?
- Fix: Add current policy baseline indicators to each slider (e.g., "Current manufacturing tariff: ~7% [WTO bound rate]")

**[Yellow] Time horizon selector is unclear**
- Short/Medium/Long labels without year counts are ambiguous
- Fix: Label as "Short (1 year)", "Medium (3 years)", "Long (5 years)" — this is already defined in the model

**[Yellow] No scenario comparison capability**
- Users cannot compare two simulations side-by-side
- Standard feature in policy simulation tools (IMF GIMF, World Bank MFMOD)
- Fix: Add "Save scenario" + "Compare" feature that shows two result columns side-by-side

**[Yellow] ChatPanel requires knowing what to ask**
- The AI assistant is powerful but blank-canvas — users don't know what questions to ask
- Fix: Add 3-4 example prompt chips (e.g., "Suggest the best policy to reduce youth unemployment in South Africa")

**[Yellow] No sensitivity analysis or "what if" exploration**
- Users cannot see how results change across a parameter range without manually adjusting sliders
- Fix: Add a simple sensitivity chart for one slider at a time (e.g., show jobs created for tariff from 0% to 30%)

**[Green] Sankey diagram is visually compelling but hard to read**
- Flow values are divided by 100 for display (noted in code comment)
- Labels are small and overlap at typical screen sizes
- Fix: Show actual job numbers in Sankey tooltips; improve label placement

**[Green] No printable/exportable results**
- For classroom or assignment use, users need to share or submit results
- Fix: Add PDF export or "Copy results summary" button

**[Green] No save/load for custom scenarios**
- Users building a scenario lose it on page refresh
- Fix: LocalStorage persistence for current scenario parameters

---

## PRIORITIZED IMPROVEMENT ROADMAP

### Priority 1 — Critical Fixes (model integrity) — est. 0.5 day
1. **Seed random technical coefficients matrix** (`np.random.seed(42)`) — 30 min
2. **Add API-level input validation** for policy parameter ranges — 30 min
3. **Surface model boundary warnings** in ResultsPanel before results display — 1 hr
4. **Fix productivity investment model** to show near-zero short-term employment effect and competitive gains long-term — 2-3 hrs

### Priority 2 — Economic Rigor — est. 1-2 days
5. **Sector-specific import elasticities** in `tiva_multipliers.py` — 1 hr
6. **Weight induced multiplier** by sector productivity — 1 hr
7. **Lower SME fiscal multipliers** to 0.8-1.2 range — 30 min
8. **Add downstream cost penalty to tariff model** (critical for economic accuracy) — 3-4 hrs
9. **Data quality badges** in ResultsPanel (OECD vs. stylized) — 1 hr
10. **Specify poverty line threshold** in job quality display — 30 min

### Priority 3 — Didactic Quality — est. 2-3 days
11. **Auto-trigger AI interpretation** (3 sentences) after each simulation — 2 hrs
12. **Label time horizon** with year counts — 15 min
13. **Add current policy baseline** to slider labels — 2 hrs (requires data)
14. **Add example prompt chips** in ChatPanel — 30 min
15. **Scenario save + compare** feature — 4-6 hrs

### Priority 4 — Code Quality — est. 1 day
16. **Add unit test suite** (3-5 core tests) — 2 hrs
17. **WDI partial-data warnings** — 1 hr
18. **Startup check** for frontend dist build — 30 min
19. **Sankey tooltip** with actual job numbers — 1 hr
20. **Export/print results** button — 2-3 hrs

---

## VERDICT: REVISE

The simulator is a well-engineered first version with genuine educational value. The core I-O framework is sound, the UI is professional, and the OECD data integration is a real strength. However, three issues require fixes before the tool can be used confidently in a professional training context:

1. The **random technical coefficients** make indirect employment results non-reproducible
2. The **productivity model** is theoretically inverted (shows jobs created short-term, when economics predicts the opposite)
3. **No guided learning structure** means most users will explore randomly without forming or testing economic intuitions

Addressing Priority 1 issues (half a day of work) would substantially raise the tool's credibility. Priorities 2-4 represent a roadmap for the next 2-3 development sessions.
