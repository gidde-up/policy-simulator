# Validation report -- Viet Nam (VNM)

- ICIO edition: 2025 (rev. Jan 2026), reference year 2022
- Employment source: OECD TiM 2025 (EMPN); fallbacks: tim_parent_residual (see assumptions registry)
- Pipeline version: 1.0.0, built 2026-06-11

## Checks

- **PASS** `check_coefficient_sums`: max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = 0.00000 (tolerance 0.01)
- **PASS** `check_nonnegative`: all non-negative
- **PASS** `check_spectral_radius`: spectral radius(A_d) = 0.5775
- **PASS** `check_output_multipliers`: multipliers: agriculture=2.74, mining=2.08, manufacturing=1.94, textiles=2.13, automotive=1.85, food_processing=2.92, chemicals=2.25, construction=2.23, utilities=2.29, trade=2.14, transport=2.32, finance=2.25, public_services=1.85, other_services=2.28 | FLAGGED outside [1.1, 2.5]: agriculture=2.735, food_processing=2.921
- **PASS** `check_employment_total`: sector sum 54,958,900 vs ILOSTAT national 55,018,096 (2022): gap 0.11% (max 10%)
- **PASS** `check_type_ii_dominance`: min(L_II - L_I) = 8.27e-04

## Coverage

- TiM employment cells: {'tim_exact': 48, 'tim_parent_residual': 2}
- Type II propensity: 0.764
- Economy-wide labour share (observed sectors): 0.635
- Registry entries written: 5

## Type I / Type II employment multipliers (jobs per USD million of final demand)

| sector | e (direct) | Type I | Type II |
|---|---|---|---|
| agriculture | 99.59 | 210.19 | 268.35 |
| mining | 2.19 | 16.37 | 66.13 |
| manufacturing | 11.82 | 31.38 | 61.17 |
| textiles | 44.26 | 91.13 | 136.77 |
| automotive | 18.09 | 38.28 | 61.26 |
| food_processing | 13.15 | 140.71 | 194.75 |
| chemicals | 4.40 | 28.63 | 58.46 |
| construction | 40.77 | 69.51 | 109.99 |
| utilities | 5.11 | 25.71 | 62.10 |
| trade | 87.08 | 127.07 | 181.01 |
| transport | 40.08 | 73.74 | 115.80 |
| finance | 14.72 | 53.61 | 111.32 |
| public_services | 80.08 | 106.27 | 174.64 |
| other_services | 45.79 | 98.61 | 148.58 |
