# What this model can and cannot tell you

## What it CAN show

- **Direction** of employment effects of a policy demand shock, and the
  **transmission channels** through which it travels: who gains, who
  pays, and through which inter-industry links.
- **Rough magnitude** — the order of magnitude of gross job flows
  implied by the country's actual 2022 production structure (OECD ICIO
  2025) and employment intensities (OECD TiM 2025 / ILOSTAT).
- **Composition**: which sectors carry the gains and losses, and how
  much of an effect is direct, supply-chain (indirect) or — as an
  upper-bound illustration — induced through household spending.
- **Trade-offs**: protected-sector gains against downstream costs and
  real-income losses; gross stimulus against its financing drag.

## What it CANNOT show

- **Forecasts.** Results are comparative-static accounting at fixed
  2022 prices, technology and trade shares — not predictions of what
  will happen.
- **Supply constraints.** Demand shocks translate fully into output;
  there are no capacity limits, no skill shortages, no land or capital
  constraints.
- **Price adjustment.** No wage or exchange-rate responses, no monetary
  policy, no market clearing. The price-side tariff model passes costs
  through fully.
- **Dynamics.** No adjustment path, no investment response, no
  productivity change, no entry/exit of firms.
- **Net labour-market outcomes.** Job numbers are gross flows through
  fixed employment coefficients. They are not net employment changes
  after economy-wide displacement and labour-market adjustment.
- **Distribution within sectors.** No firm-size, gender, age or
  formality breakdowns: the underlying per-sector shares could not be
  derived from verified sources and were removed from the tool.
- **Marginal results are fragile.** When the parameter range straddles
  zero (e.g. a tariff's net effect), the honest statement is "net
  effect approximately zero; gross reallocation large" — and the sign
  of small net results can flip under the upper-bound induced (Type II)
  closure. The robust lesson is the reallocation, not the sign of a
  small residual.

## Sources and audit trail

Every coefficient is computed from OECD ICIO 2025 (year 2022), OECD TiM
2025 and ILOSTAT by the reproducible pipeline in `data-pipeline/`;
every behavioural parameter and every substituted data cell carries a
citation in `backend/app/data/assumptions.json`.
