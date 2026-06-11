# Validation report -- Senegal (SEN)

- ICIO edition: 2025 (rev. Jan 2026), reference year 2022
- Employment source: OECD TiM 2025 (EMPN); fallbacks: tim_parent_residual (see assumptions registry)
- Pipeline version: 1.0.0, built 2026-06-11

## Checks

- **PASS** `check_coefficient_sums`: max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = 0.00233 (tolerance 0.01)
- **PASS** `check_nonnegative`: all non-negative
- **PASS** `check_spectral_radius`: spectral radius(A_d) = 0.2483
- **PASS** `check_output_multipliers`: multipliers: agriculture=1.19, mining=1.32, manufacturing=1.57, textiles=1.40, automotive=1.41, food_processing=1.59, chemicals=1.40, construction=1.72, utilities=1.27, trade=1.16, transport=1.36, finance=1.38, public_services=1.21, other_services=1.31
- **PASS** `check_employment_total`: sector sum 4,976,300 vs ILOSTAT national 4,544,908 (2022): gap 9.49% (max 10%)
- **PASS** `check_type_ii_dominance`: min(L_II - L_I) = 1.00e-06

## Coverage

- TiM employment cells: {'tim_exact': 48, 'tim_parent_residual': 2}
- Type II propensity: 1.965 (capped at 1)
- Economy-wide labour share (observed sectors): 0.278
- Registry entries written: 6

## Type I / Type II employment multipliers (jobs per USD million of final demand)

| sector | e (direct) | Type I | Type II |
|---|---|---|---|
| agriculture | 181.47 | 208.50 | 213.64 |
| mining | 27.41 | 51.29 | 82.23 |
| manufacturing | 62.50 | 104.46 | 133.50 |
| textiles | 205.97 | 253.18 | 282.53 |
| automotive | 52.06 | 93.54 | 186.47 |
| food_processing | 37.49 | 125.99 | 140.53 |
| chemicals | 35.75 | 62.25 | 81.73 |
| construction | 114.51 | 175.82 | 212.73 |
| utilities | 20.27 | 43.63 | 69.47 |
| trade | 267.93 | 286.63 | 303.81 |
| transport | 144.27 | 188.17 | 228.84 |
| finance | 30.34 | 64.79 | 140.49 |
| public_services | 47.53 | 70.47 | 174.00 |
| other_services | 119.72 | 153.67 | 220.68 |
