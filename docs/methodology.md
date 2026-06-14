# How this simulator works

This is the methodology reference. It is written in two tiers: the plain
text is for everyone; each "Show the detail / equations" drop-down adds
the full formal version for readers who want it. Nothing here is
required reading to use the tool.

## 1. What this tool does

The simulator estimates how a policy choice ripples through an economy's
industries to change employment, using real input-output data for five
countries in 2022.

A worked example in words: a government spends on construction.
Construction firms buy steel, cement and transport from other
industries; those suppliers raise output and hire. The newly employed
spend their wages on food, housing and services, so those sectors hire
too. The tool adds up the jobs created at each round - the direct hire,
the supply-chain hire, and the wage-spending hire - and reports the
total, its split, and which sectors gain or lose.

Results are directional and illustrative: the size and direction of an
effect and the channels it travels through, not a forecast.

## 2. The data

The numbers come from official OECD and ILO statistics for 2022 - South
Africa, Tunisia, Viet Nam, Thailand and Senegal - not from assumptions.
Inter-industry structure and final demand are from the OECD; employment
and pay are from the OECD and the ILO.

::: detail Show the data detail
- **Inter-industry structure, final demand, imports, value added**:
  OECD Inter-Country Input-Output (ICIO) tables, 2025 edition
  (rev. Jan 2026), reference year 2022, regular version (80 economies +
  rest of world).
- **Aggregation**: the ~50 ICIO industries are mapped to 14 didactic
  sectors by a committed concordance (data-pipeline/concordance_icio_to_14.csv),
  one row per industry with a documented rationale.
- **Employment and labour compensation by industry**: OECD Trade in
  Employment (TiM) 2025 (EMPN, LABR).
- **Cross-checks and informality**: ILOSTAT (national employment totals,
  labour force, informal-employment shares by activity).
- **Provenance**: every source file's URL, SHA-256 hash, byte size and
  access date is recorded in data-pipeline/sources.lock.json; every
  substituted or derived cell is in backend/app/data/assumptions.json
  with a citation.
- **Employment concept note**: the model's baseline employment is the
  TiM national-accounts concept (consistent with the ICIO output
  accounts); the ILOSTAT labour-force-survey total differs and is stored
  only for cross-checking. Percentage-of-employment readings use the
  sector-sum (national-accounts) baseline.
:::

## 3. The engine

An input-output model traces two things a simple "jobs per dollar"
estimate misses: the supply chain that an industry pulls along
(indirect effects), and the spending of newly earned wages (induced
effects, shown as an optional upper bound). The model holds prices and
technology fixed at their 2022 values, so it is a short-run,
comparative-static picture.

::: detail Show the engine equations
The core is the open static Leontief model. Let A_d be the domestic
technical-coefficient matrix (input i per unit of output j from domestic
suppliers) and A_m the imported-input coefficients. The Leontief inverse
L = (I - A_d)^-1 maps a final-demand change to the total output needed
to meet it.

Employment effect of a final-demand change dF:
  dE = e-hat . L . dF
where e-hat is the diagonal matrix of employment coefficients
(jobs per USD million of output). The decomposition:
  direct   = e . dF
  indirect = e . (L - I) . dF
  induced  = e . (L_II - L) . dF   (Type II only)
Type II uses the Miyazawa household closure L_II, which recycles labour
income into consumption; the consumption propensity is capped at 1, so
induced effects are an upper bound and the sign of a small net result
can flip when it is switched on.

Price-side levers (tariffs, subsidies, depreciation) use the cost-push
Leontief identity: a unit-cost change dc raises producer prices by
  dp = L' . dc
which then changes demand through the own-price elasticity. Output is in
USD million (2022 current prices); all rates are fractions internally,
converted from percent at the API boundary.
:::

## 4. How each policy is modelled

Twelve levers, grouped so industrial and sectoral policy comes first and
trade last. Each is a demand or price change with parameters from the
data or cited literature; each reports its channels separately. The full
note for any lever (equations, parameter values, citations, and what it
deliberately leaves out) is in docs/levers/ and in the in-app
assumptions popover next to the lever.

Industrial and sectoral:
- **Production subsidy**: lowers a sector's price, raising demand for it
  and household real income.
- **Wage subsidy**: lowers a sector's price in proportion to its labour
  share; cheaper than a production subsidy, same machinery.
- **Investment tax incentive**: only the non-windfall share of
  incentivised investment adds demand; the windfall (investment that
  would have happened anyway) is shown explicitly.
- **Sector support**: government spending that raises demand for a
  chosen sector.

Public investment and employment programmes:
- **Public investment**: spending allocated by the capital-goods mix or
  to a target sector.
- **Public works / EIIP**: a labour-based or conventional programme;
  the wage component creates direct job-years, the materials component
  flows through the construction supply chain.
- **Direct public hiring**: government employs people in public services;
  wages plus a small operating component.

Macro-fiscal:
- **SME / demand stimulus**: spending placed on household consumption,
  government consumption, or investment (a composition choice).

Trade and exchange rate:
- **Tariff**: raises import prices - helping the protected sector but
  raising input costs downstream and consumer prices - with an optional
  retaliation toggle.
- **Exchange-rate depreciation (stylised)**: raises all import prices
  and expands exports; the net sign depends on the country's structure.

::: detail Show the lever equations and parameters
The per-lever notes in docs/levers/*.md are the canonical formal source
(one file per lever): channel equations, the registry parameter values
and their citations, and the explicit exclusions. The key cited
parameters, all in backend/app/data/assumptions.json:
- import demand elasticities per country (Kee, Nicita & Olarreaga 2008);
- own-price (compensated) demand elasticity -0.5 [-0.25, -0.75]
  (USDA-ERS TB-1929);
- retaliation share 0.5 on the top export sectors (Fajgelbaum et al.
  2020);
- EIIP labour-based labour share 0.35 [0.20, 0.50] (ILO EIIP), with the
  conventional construction labour share derived per country;
- export supply elasticity 0.6 [0.3, 1.1] (Tokarick 2010, Table 2 -
  export SUPPLY; the paper has no export-demand table, so the
  depreciation lever is labelled stylised);
- investment-incentive redundancy 0.75 [0.50, 0.90] (James 2013;
  IMF-OECD-UN-WB 2015).
The engine contains no behavioural constant: an automated test asserts
no numeric literal outside {0, 1, 2} appears in engine.py.
:::

## 5. Financing: who pays for the spending

Spending has to be paid for, and how it is paid for changes the jobs
result. The tool lets you choose:
- **Deficit-financed**: ignore how it is paid for - the pure
  "what does adding this spending do?" experiment.
- **Tax-financed** (the default): the spending is paid by taxes that
  reduce household spending. Because households would have saved part of
  any taxed income, the demand withdrawn is less than the spending
  added, so net employment is usually a modest positive - the standard
  balanced-budget result.
- **Full crowding-out**: the strongest assumption, every dollar of
  spending displaces a dollar of household demand. Shown as an upper
  bound on the financing drag, not the default.

The same financing choice applies to every spending lever and to the
stimulus, so no lever gets a privileged treatment.

::: detail Show the financing detail
A spending or transfer lever places its first-round demand on its
sector vector (with that vector's import share as leakage). The chosen
financing mode then withdraws demand from the household consumption
vector:
- deficit: withdrawal = 0;
- tax-financed: withdrawal = MPC . (fiscal cost), where MPC is the
  marginal propensity to consume (a tax falls partly on saving, so only
  the consumed share is withdrawn);
- full crowding-out: withdrawal = 1.0 . (fiscal cost).
This makes tax-financed spending Haavelmo-consistent: a balanced-budget
injection (spend X, tax X) leaves a net positive demand of (1 - MPC).X
plus any difference in job intensity between the spending and the
displaced consumption. The MPC parameter and its citation are in the
assumptions registry. (Parameter value finalised with the financing
verification; see CHANGELOG.)
:::

## 6. What the tool cannot do

- It is not a forecast.
- Prices and wages do not adjust; there are no supply or capacity limits.
- It is short-run and static (one before/after comparison, no time path).
- Small net results are fragile: read the reallocation, not the sign.
- Job-quality figures describe the mix of the jobs moved, not their
  intrinsic quality.

::: detail Show the formal limitations
The full statement is in docs/model-limitations.md (fixed coefficients,
linearity, no factor constraints, comparative-static, the
marginal-results sign-flip caveat, the composition assumption behind
job quality) and the deliberate exclusions - interest-rate policy,
active labour market policies, minimum wages, distribution-targeted
transfers - with reasons, in docs/not-in-this-tool.md. Both are served
in-app (the "model scope" and "not in this tool" panels).
:::
