# Validation report -- Thailand (THA)

- ICIO edition: 2025 (rev. Jan 2026), reference year 2022
- Employment source: OECD TiM 2025 (EMPN); fallbacks: tim_parent_residual (see assumptions registry)
- Pipeline version: 1.0.0, built 2026-06-11

## Checks

- **PASS** `check_coefficient_sums`: max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = 0.00000 (tolerance 0.01)
- **PASS** `check_nonnegative`: all non-negative
- **PASS** `check_spectral_radius`: spectral radius(A_d) = 0.3970
- **PASS** `check_output_multipliers`: multipliers: agriculture=1.53, mining=1.38, manufacturing=1.68, textiles=2.27, automotive=1.64, food_processing=1.91, chemicals=1.41, construction=1.85, utilities=1.52, trade=1.26, transport=1.69, finance=1.19, public_services=1.31, other_services=1.58
- **PASS** `check_employment_total`: sector sum 39,204,000 vs ILOSTAT national 39,221,052 (2022): gap 0.04% (max 10%)
- **PASS** `check_type_ii_dominance`: min(L_II - L_I) = 1.39e-03

## Coverage

- TiM employment cells: {'tim_exact': 48, 'tim_parent_residual': 2}
- Type II propensity: 1.365 (capped at 1)
- Economy-wide labour share (observed sectors): 0.347
- Registry entries written: 6

## Type I / Type II employment multipliers (jobs per USD million of final demand)

| sector | e (direct) | Type I | Type II |
|---|---|---|---|
| agriculture | 181.00 | 217.06 | 239.99 |
| mining | 2.33 | 8.19 | 24.63 |
| manufacturing | 12.75 | 27.71 | 40.49 |
| textiles | 16.67 | 49.68 | 65.20 |
| automotive | 10.49 | 24.31 | 36.82 |
| food_processing | 17.93 | 93.53 | 115.94 |
| chemicals | 7.63 | 15.46 | 28.25 |
| construction | 55.28 | 79.57 | 95.94 |
| utilities | 3.31 | 9.31 | 20.54 |
| trade | 56.95 | 64.23 | 88.62 |
| transport | 26.32 | 42.69 | 61.27 |
| finance | 11.78 | 15.79 | 39.49 |
| public_services | 49.05 | 57.87 | 109.17 |
| other_services | 48.79 | 72.54 | 94.81 |
