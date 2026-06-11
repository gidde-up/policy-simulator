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

## Acceptance constraint
Under default parameters a 10% manufacturing tariff must not be net
employment-positive in any country (automated test;
Flaaen & Pierce 2019; Amiti, Redding & Weinstein 2019).
