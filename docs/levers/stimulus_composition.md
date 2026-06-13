# Lever: stimulus composition

The SME / demand stimulus (% of GDP) can be injected three ways; the
choice changes both the demand vector and the leakage treatment:

- **household transfer** (default, the v1 behaviour): spread across the
  household consumption vector and scaled by the cited first-round
  fiscal multiplier (Batini et al. 2014). The multiplier captures that
  transfers are partly saved or spent on imports before any domestic
  demand arises.
- **government consumption**: spread across the government final-demand
  vector. Direct government purchases enter domestic demand at full
  value; the leakage is the import share of the government vector
  (imported_final_demand / total) rather than a behavioural multiplier.
- **public investment**: same treatment using the GFCF vector.

Why the multiplier applies only to the transfer: a transfer is income
that households may save or spend abroad (first-round leakage, hence the
< 1 multiplier); a government purchase is spending that occurs by
definition, so its only leakage is the imported content of what is
bought, which the data-derived import share already captures. Applying
the Batini multiplier to direct purchases would double-count the
leakage.

Fiscal cost = the stimulus amount; the stimulus does not carry the
financing-drag toggle (it is modelled as deficit/one-off, distinct from
the tax-financed sector-support and public-investment levers).
