# Lever: exchange-rate depreciation (stylised)

A depreciation of rate d is a comparative-static price shock with two
sides:
- **import side**: all imported prices rise by d (an ImportPriceShock on
  every product), feeding the downstream input-cost and household
  real-income channels through the existing price model -- both losses;
- **export side**: export demand expands, ΔF_exports = epsilon_x x d x
  exports by sector, with epsilon_x the export supply elasticity.

The net sign is NOT forced: a country's structure decides it (an
import-dependent producer loses more through input costs; an
export-oriented one gains more through the export channel). The tests
assert only the channel signs (export gain >= 0, real-income loss <= 0,
input-cost loss <= 0) and the decomposition identity.

**Stylised** (stated in the UI label): a pure relative-price shock. No
monetary policy, no inflation pass-through dynamics, no balance-sheet or
debt-valuation effects, no J-curve timing. epsilon_x = 0.6, range
[0.3, 1.1].

Source note: the export elasticity is from Tokarick (2010) IMF WP/10/180
Table 2, which reports export **supply** elasticities (the paper has no
export-demand table). The lever models the export-volume response to the
relative-price change as a supply expansion; Viet Nam is absent from the
paper, so a single cited developing-economy value with a range is used
for all countries. See the assumptions registry and the data-
availability matrix.
