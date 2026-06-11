# Validation report -- Tunisia (TUN)

- ICIO edition: 2025 (rev. Jan 2026), reference year 2022
- Employment source: OECD TiM 2025 (EMPN); fallbacks: tim_parent_residual (see assumptions registry)
- Pipeline version: 1.0.0, built 2026-06-11

## Checks

- **PASS** `check_coefficient_sums`: max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = 0.00002 (tolerance 0.01)
- **PASS** `check_nonnegative`: all non-negative | inventories min=-0.0 (negative cells permitted)
- **PASS** `check_spectral_radius`: spectral radius(A_d) = 0.2630
- **PASS** `check_output_multipliers`: multipliers: agriculture=1.45, mining=1.19, manufacturing=1.25, textiles=1.27, automotive=1.22, food_processing=1.76, chemicals=1.22, construction=1.38, utilities=1.27, trade=1.30, transport=1.33, finance=1.38, public_services=1.23, other_services=1.34
- **PASS** `check_employment_total`: sector sum 3,578,800 vs ILOSTAT national 3,444,619 (2022): gap 3.90% (max 10%)
- **PASS** `check_type_ii_dominance`: min(L_II - L_I) = 7.55e-04

## Coverage

- TiM employment cells: {'tim_exact': 48, 'tim_parent_residual': 2}
- Type II propensity: 1.134 (capped at 1)
- Economy-wide labour share (observed sectors): 0.435
- Registry entries written: 6

## Type I / Type II employment multipliers (jobs per USD million of final demand)

| sector | e (direct) | Type I | Type II |
|---|---|---|---|
| agriculture | 55.18 | 77.68 | 89.61 |
| mining | 6.36 | 10.85 | 25.15 |
| manufacturing | 29.73 | 39.10 | 61.43 |
| textiles | 63.55 | 78.06 | 102.37 |
| automotive | 28.48 | 37.41 | 55.94 |
| food_processing | 16.04 | 54.36 | 72.24 |
| chemicals | 22.30 | 30.28 | 46.65 |
| construction | 126.20 | 142.58 | 161.83 |
| utilities | 15.57 | 21.49 | 38.02 |
| trade | 71.46 | 82.91 | 98.82 |
| transport | 36.72 | 49.51 | 78.96 |
| finance | 12.89 | 23.79 | 58.43 |
| public_services | 66.84 | 76.03 | 128.68 |
| other_services | 37.27 | 51.21 | 77.23 |
