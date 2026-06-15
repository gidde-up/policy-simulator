# Lever: import tariff

A tariff of rate t on sector s is modelled as four separately reported
final-demand channels (engine: `backend/app/models/engine.py`).

## (i) Import substitution (protected-sector gain)
Import demand for s falls by |ε_s|·t (capped at 100% of the import
flow). The share of that reduction met by domestic suppliers equals the
sector's **domestic absorption share** (x_s − exports_s)/((x_s −
exports_s) + imports_s), computed from the country data — not assumed.
ε_s is the country's import-weighted average import demand elasticity
from Kee, Nicita and Olarreaga (2008), Table 1 (see assumptions
registry; Senegal's value is calibrated, with the reason recorded).

## (ii) Downstream cost
The imported-input price rise propagates through the domestic cost
structure (price-side Leontief model): dp′ = dp_m′ A_m (I − A_d)^−1
with dp_m = t·1_s. Final demand for domestic output — including
exports — falls by |η|·dp_j·F_j, with η the compensated own-price
demand elasticity (USDA-ERS TB-1929; registry).

## (iii) Real-income loss
The consumer price index rises by the cost-push dp (weighted by
domestic household consumption) plus the direct price rise on imported
final goods of s. The implied loss of purchasing power reduces
household demand across all sectors in proportion to the household
consumption vector. η is documented as compensated, so the overlap with
this channel biases the net effect downward — the conservative
direction for the acceptance constraint.

## (iv) Retaliation (toggle, default off, stylised)
Export demand falls by t̄ × 0.5 in the country's top-3 export sectors
(t̄ = import-weighted average tariff). Anchored on the 2018-19 US-China
episode (Fajgelbaum et al. 2020); labelled illustrative.

## Costs
Tariff revenue = t × remaining imports (post-substitution), valued
pre-tariff.

## No forced sign (v1.2 correction)
Earlier versions forced the tariff result to be net employment-negative
and calibrated Senegal's import-demand elasticity downward to achieve
it. That was outcome-forcing and has been removed: every country now
uses its cited import-weighted elasticity from KNO (2008), and the sign
is whatever the data and parameters produce. Tests check the channel
accounting and the caveats, never a required sign. With strong domestic
substitution and weak downstream linkages (Senegal), a manufacturing
tariff can come out modestly net-positive in this static model.

## Caveat (shown in the UI and methodology)
Tariff results are static simulated effects, not a policy
recommendation. The model can show gross gains in protected sectors and
losses through import costs, downstream users, consumption and trade
channels. It does not fully model retaliation, long-run productivity,
consumer welfare, firm dynamics, distributional price effects, or
macroeconomic adjustment.
