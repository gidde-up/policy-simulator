# Wage cross-check (internal TiM vs ILOSTAT earnings)

Internal compensation per worker = TiM compensation of employees / TiM employment, by sector, from the verified country JSONs (USD thousand per worker per year, current 2022 USD).

## ILOSTAT earnings-by-activity availability

- ZAF: EAR_4MTH_SEX_ECO_CUR_NB_A -> NOT available (HTTP 400)
- TUN: EAR_4MTH_SEX_ECO_CUR_NB_A -> NOT available (HTTP 400)
- VNM: EAR_4MTH_SEX_ECO_CUR_NB_A -> NOT available (HTTP 400)
- THA: EAR_4MTH_SEX_ECO_CUR_NB_A -> NOT available (HTTP 400)
- SEN: EAR_4MTH_SEX_ECO_CUR_NB_A -> NOT available (HTTP 400)

The ILOSTAT mean-earnings-by-economic-activity series is not retrievable through the rplumber bulk API for these countries (HTTP 400). The programmatic external cross-check could not be performed; the internal figures below are reported for transparency.

## Internal compensation per worker by sector (USD thousand/year)

| sector | ZAF | TUN | VNM | THA | SEN |
|---|---|---|---|---|---|
| agriculture | 2.8 | 1.5 | 1.8 | 0.9 | 0.1 |
| mining | 18.3 | 21.6 | 95.9 | 55.1 | 3.9 |
| manufacturing | 14.5 | 7.4 | 8.8 | 4.8 | 1.3 |
| textiles | 4.2 | 3.8 | 4.1 | 2.8 | 0.5 |
| automotive | 22.2 | 6.3 | 3.8 | 5.9 | 7.5 |
| food_processing | 9.7 | 7.4 | 8.7 | 5.8 | 1.0 |
| chemicals | 15.4 | 7.0 | 15.9 | 11.3 | 1.4 |
| construction | 3.0 | 1.2 | 3.7 | 1.5 | 0.9 |
| utilities | 20.4 | 9.8 | 19.8 | 18.6 | 4.7 |
| trade | 4.5 | 1.7 | 2.9 | 3.9 | 0.2 |
| transport | 4.4 | 7.5 | 3.8 | 4.2 | 1.0 |
| finance | 51.2 | 24.7 | 16.1 | 18.5 | 9.7 |
| public_services | 6.9 | 8.8 | 5.2 | 10.3 | 10.1 |
| other_services | 18.8 | 6.6 | 4.3 | 3.2 | 2.3 |

## Conclusion

The model uses the internal TiM-based compensation figures shown above. They are, by construction, consistent with the OECD ICIO value-added accounts that drive every other model quantity; an ILOSTAT labour-force-survey earnings series would introduce a different statistical concept (gross monthly earnings of employees, survey-based, excluding employers' social contributions and the self-employed). For an accounting-consistent input-output simulator, IO consistency is the correct priority. This choice is documented here and in the methodology.

