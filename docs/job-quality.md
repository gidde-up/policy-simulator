# Job-quality module

The job-quality outputs describe the **composition** of the jobs a
scenario moves -- their wage and informality mix -- not their intrinsic
quality and not a forecast. Every figure rests on one assumption, stated
in each caveat: **jobs created or lost in a sector are assumed to share
that sector's existing characteristics** (average compensation,
informality rate). The module is a pure post-processing of the scenario
result; it does not change any employment number.

## Wage dimension (all countries; internal data)

- **Wage-bill change** dW = compensation coefficients . output change
  = v' L dF, where v is the sector compensation/output ratio (TiM
  labour compensation over ICIO output). This is the change in the
  total wage bill implied by the output change, and equals the
  value-added/compensation identity exactly (tested).
- **Average compensation ratio**: the |employment-change|-weighted
  average compensation per worker of the sectors that move, divided by
  the economy-wide average compensation per worker. A ratio of 0.8
  means "the jobs moved pay, on average, 0.8x the economy mean". Bounded
  by the sector min/max by construction (tested).
- The per-sector wage profile (which sectors, at which compensation
  level, gain or lose) is available from the sector effects.

All wage figures use the internal TiM-based compensation, for
consistency with the input-output accounts (see
data-pipeline/reports/wage_crosscheck.md).

## Informality dimension (per-country gate)

The |employment-change|-weighted average informal-employment share of
the sectors that move: "an estimated X% of the jobs moved fall in
activities where employment is predominantly informal". Uses the
ILOSTAT informality block written in Session E (EMP_NIFL_SEX_ECO_NB_A
over total employment; ZAF via broad aggregate groups, others ISIC
Rev.4 sections; manufacturing-family sectors inherit section C). The
data year is shown. A country with no informality block shows no
informality figure -- hidden, never imputed (tested gate).

## Working poverty (context only)

The national working-poverty rate (ILOSTAT SDG 1.1.1) appears only in
the country context panel, sourced and dated. It is **never** attached
to scenario results: no sector-level working-poverty data exists, so a
scenario-specific working-poverty number would be invented.

## What this is not

Not a prediction that specific created jobs are informal, low-paid or
precarious; not a measure of job quality changing within a sector; not a
distributional analysis across households. It is the sector mix of the
employment change, read through each sector's current averages.
