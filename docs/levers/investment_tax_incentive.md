# Lever: investment tax incentive

The user sets the fiscal cost X (% of GDP forgone in revenue) and the
incentive intensity s (the share of investment cost the incentive
covers). Then:

- gross incentivised investment = X / s
- additional investment = (1 - r) x X / s
- windfall = r x X / s

where r is the registered redundancy share (the fraction of incentivised
investment that would have happened anyway). Only the **additional**
investment creates demand (allocated by the GFCF composition or a target
sector); the **windfall** is displayed explicitly because it is the
didactic point: a large share of incentive spending typically rewards
investment that would have occurred regardless.

Fiscal cost X carries the financing drag (default on). Consequences,
all tested:
- at r = 1 the lever is pure drag (no additional investment) -> net
  negative;
- net employment is monotonically decreasing in r;
- windfall + additional = gross (identity).

r = 0.75, range [0.50, 0.90], from investor-motivation surveys in
James (2013) and IMF-OECD-UN-World Bank (2015) Table 1 (covered target
countries: Tunisia 0.58, Viet Nam 0.85, Thailand 0.81). See the
assumptions registry.
