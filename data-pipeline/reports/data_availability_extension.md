# Data-availability matrix -- policy-lever / job-quality extension (Session E)

Derived from the country JSONs, the assumptions registry and sources.lock.json. Per-country unavailability means the dependent output is hidden for that country -- never imputed.

## Per-country items

| item | ZAF | TUN | VNM | THA | SEN |
|---|---|---|---|---|---|
| 1. Informal employment by activity | OK (2022, ILOSTAT broad aggregate groups) | OK (2019, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) | OK (2022, ISIC Rev.4 sections) |
| 5a. National informality rate (context) | OK (2022) | OK (2019) | OK (2022) | OK (2022) | OK (2022) |
| 5b. Working-poverty rate (context) | OK (2022) | OK (2022) | OK (2022) | OK (2022) | OK (2022) |
| 3b. Conventional construction labour share | DERIVED | DERIVED | DERIVED | DERIVED | DERIVED |

## Global / non-per-country items

- 2. Export elasticity (depreciation lever): **GLOBAL** -- Tokarick (2010) WP/10/180 has NO export-demand table; it reports export SUPPLY (Table 2), import demand (Table 1) and trade-balance (Table 4) elasticities. Registered GLOBAL as export SUPPLY (0.6, [0.3, 1.1]); Viet Nam is absent from the paper and the published sparse-cell tables do not support reliable per-country extraction. Import-demand Table 1 cross-checks the registered KNO values qualitatively.
- 3a. EIIP labour-based labour-cost share: **GLOBAL** (GLOBAL-eiip-labour-cost-share-central/low/high; ILO EIIP, 0.35 / 0.20 / 0.50)
- 4. Investment-incentive redundancy share: **GLOBAL** (0.75, [0.50, 0.90]; James 2013 + IMF-OECD-UN-WB 2015 Table 1; covered targets TUN 0.58, VNM 0.85, THA 0.81)
- 6. Wage cross-check (internal TiM vs ILOSTAT earnings): **DONE (report)** (ILOSTAT earnings-by-activity not on the bulk API; model uses internal TiM figures -- see reports/wage_crosscheck.md)

## Notes

- Informality indicator: ILOSTAT EMP_NIFL_SEX_ECO_NB_A over EMP_TEMP_SEX_ECO_NB_A. ZAF has only broad-aggregate-group detail (AGR/MAN/CON/MEL/MKT/PUB); the other four have ISIC Rev.4 sections. Manufacturing-family sectors inherit section C (1-digit data cannot split manufacturing); every inherited cell is registered (scope=informality, method=share_inheritance).
- TUN informality year is 2019 (latest available); others 2022.
- All source PDFs (ILO EIIP x2, Tokarick WP/10/180, James 2013, IMF-OECD-UN-WB 2015) were acquired by manual browser download (IMF/World Bank bot-blocked) and recorded in sources.lock.json with sha256 + method=manual.
- Concept note (item 2): the extension prompt expected per-country export DEMAND elasticities from Tokarick; the paper does not contain them. The honest reading -- export SUPPLY elasticities, correctly labelled -- is registered GLOBAL and the depreciation lever is flagged stylised.

