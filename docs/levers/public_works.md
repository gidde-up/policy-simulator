# Lever: public works / EIIP

A public works programme with budget B (% of GDP) and a method choice:
- **labour-based** (employment-intensive, EIIP): labour cost share lambda
  from the ILO EIIP literature (0.35, range 0.20-0.50);
- **conventional** (equipment-based): lambda = the country's own
  construction-sector labour share (compensation / output, data-derived
  from the JSON), typically 0.08-0.16 -- much lower.

The budget splits into:
- a **wage component** lambda x B that creates direct jobs outside the
  output-employment route: direct jobs = (lambda x B) / (construction
  compensation per worker, internal data). With Type II on, this wage
  bill is recycled through the household closure as induced consumption.
- a **materials component** (1 - lambda) x B injected across the
  construction sector's input column (domestic A_d column, normalised),
  generating indirect/induced effects through the Leontief inverse.

Fiscal cost = B (financing drag default on). Because lambda is much
higher for the labour-based method, it creates far more direct jobs per
budget than the conventional method (tested).

**Results are JOB-YEARS, not permanent posts** (flagged in the UI): one
job-year is one person employed for one year; public works jobs are
typically temporary. The lever references real programmes (e.g. South
Africa's EPWP) only as context -- it does not model any specific
programme's design.
