# Data-availability matrix -- policy-lever / job-quality extension (Session E)

Derived from the country JSONs, the assumptions registry and sources.lock.json. Per-country unavailability means the dependent output is hidden for that country -- never imputed.

## Per-country items

| item | ZAF | TUN | VNM | THA | SEN |
|---|---|---|---|---|---|
| 1. Informal employment by activity | OK (2022, ILOSTAT broad aggregate groups) | OK (2019, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) |
| 5a. National informality rate (context) | OK (2022) | OK (2019) | OK (2022) | OK (2022) | OK (2022) |
| 5b. Working-poverty rate (context) | OK (2022) | OK (2022) | OK (2022) | OK (2022) | OK (2022) |
| 3b. Conventional construction labour share | DERIVED | DERIVED | DERIVED | DERIVED | DERIVED |
| 2. Tokarick export demand elasticity | PENDING (manual download: IMF WP/10/180) | PENDING (manual download: IMF WP/10/180) | PENDING (manual download: IMF WP/10/180) | PENDING (manual download: IMF WP/10/180) | PENDING (manual download: IMF WP/10/180) |

## Global / non-per-country items

- 3a. EIIP labour-based labour-cost share: **GLOBAL** (GLOBAL-eiip-labour-cost-share-central/low/high; ILO EIIP, 0.35 / 0.20 / 0.50)
- 4. Investment-incentive redundancy share: **PENDING (manual download: James 2013; IMF-OECD-UN-WB 2015)**
- 6. Wage cross-check (internal TiM vs ILOSTAT earnings): **DONE (report)** (ILOSTAT earnings-by-activity not on the bulk API; model uses internal TiM figures -- see reports/wage_crosscheck.md)

## Notes

- Informality indicator: ILOSTAT EMP_NIFL_SEX_ECO_NB_A over EMP_TEMP_SEX_ECO_NB_A. ZAF has only broad-aggregate-group detail (AGR/MAN/CON/MEL/MKT/PUB); the other four have ISIC Rev.4 sections. Manufacturing-family sectors inherit section C (1-digit data cannot split manufacturing); every inherited cell is registered (scope=informality, method=share_inheritance).
- TUN informality year is 2019 (latest available); others 2022.
- Items 2 and 4 require manual PDF downloads (IMF/World Bank are bot-blocked). They feed Session F levers (depreciation; investment tax incentive) and are not needed by the Session E engine foundation. register_extension_params.py registers them automatically once the PDFs are in raw/ and the extraction scripts have read them.

