# Validation report -- South Africa (ZAF)

- ICIO edition: 2025 (rev. Jan 2026), reference year 2022
- Employment source: OECD TiM 2025 (EMPN); fallbacks: tim_parent_residual (see assumptions registry)
- Pipeline version: 1.0.0, built 2026-06-11

## Checks

- **PASS** `check_coefficient_sums`: max |colsum(A_d)+colsum(A_m)+va/x+tls/x - 1| = 0.00000 (tolerance 0.01)
- **PASS** `check_nonnegative`: all non-negative
- **PASS** `check_spectral_radius`: spectral radius(A_d) = 0.3778
- **PASS** `check_output_multipliers`: multipliers: agriculture=1.99, mining=1.82, manufacturing=1.90, textiles=1.76, automotive=1.79, food_processing=2.14, chemicals=1.74, construction=1.82, utilities=1.80, trade=1.64, transport=1.75, finance=1.12, public_services=1.95, other_services=1.35
- **PASS** `check_employment_total`: sector sum 15,732,200 vs ILOSTAT national 15,736,073 (2022): gap 0.02% (max 10%)
- **PASS** `check_type_ii_dominance`: min(L_II - L_I) = 1.24e-03

## Coverage

- TiM employment cells: {'tim_exact': 48, 'tim_parent_residual': 2}
- Type II propensity: 1.160 (capped at 1)
- Economy-wide labour share (observed sectors): 0.503
- Registry entries written: 5

## Type I / Type II employment multipliers (jobs per USD million of final demand)

| sector | e (direct) | Type I | Type II |
|---|---|---|---|
| agriculture | 29.46 | 50.07 | 64.74 |
| mining | 6.61 | 18.61 | 34.87 |
| manufacturing | 10.55 | 24.03 | 42.85 |
| textiles | 42.71 | 60.71 | 80.23 |
| automotive | 4.67 | 18.28 | 33.93 |
| food_processing | 11.32 | 35.72 | 53.54 |
| chemicals | 5.23 | 16.56 | 28.99 |
| construction | 54.07 | 68.70 | 88.27 |
| utilities | 5.08 | 16.63 | 32.37 |
| trade | 42.83 | 55.05 | 76.64 |
| transport | 26.21 | 40.72 | 56.61 |
| finance | 8.53 | 9.99 | 37.55 |
| public_services | 28.16 | 46.56 | 72.99 |
| other_services | 21.22 | 27.79 | 56.93 |
