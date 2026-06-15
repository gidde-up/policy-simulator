# Workstream C - Financing-drag correction: verification STOP

Date: 2026-06-14. Baseline: v1.1.0 (Sessions A-H verified).
Status: implemented in the working tree, full test suite green.
**No version bump, no commit of C, no push** - held for your verification
(Integrated Prompt v5, step 4 and final acceptance #20).

This report is the C.6 deliverable. The final v1.2.0 report
(`verification_after_financing_methodology_fix.md`) is produced only
after you sign off on C and Workstream I runs.

---

## 1. What changed

The boolean `include_financing_drag` (an implicit MPC = 1, i.e. full
crowding-out, applied as the v1.1.0 default) is replaced by an explicit
`financing_mode`:

| mode | withdrawal per unit fiscal cost | role |
|------|--------------------------------|------|
| `deficit` | 0 | gross demand experiment |
| `tax_financed` | MPC (0.8) | **new default** |
| `full_crowding_out` | 1.0 | upper-bound sensitivity (old behaviour) |

- MPC is a registered behavioural parameter
  `GLOBAL-marginal-propensity-to-consume` (central 0.8, low 0.6, high 0.9;
  stylised developing-economy, Haavelmo 1945 framing, `literature_based`).
  Not a country econometric estimate - labelled as such.
- Financing is applied symmetrically to every positive-cost fiscal lever,
  including the SME/household stimulus, which previously carried a 0.5
  first-round fiscal multiplier and **no** financing offset. That 0.5
  multiplier is removed; the transfer now lands on the household basket
  with its import leakage, and the saving side is handled by the
  financing MPC. Stimulus is no longer costless to finance.
- Tariffs and depreciation are NOT financing-eligible (no fiscal spend).
  Tariff revenue stays a memo item; it is not auto-recycled.
- The old boolean is a deprecated alias: `True -> full_crowding_out`,
  `False -> deficit`, with `deprecated_input_used: true` in the output.
- `run_scenario` returns a structured `financing` object and the
  aggregate gains `gross_jobs_before_financing`,
  `net_jobs_after_financing`, `financing_offset_jobs`.

## 2. Financing battery (1% of GDP, net jobs by mode)

Reproducible: `python make_financing_report.py`; full decomposition in
`reports/financing_battery.json`. Strict ordering
`deficit > tax_financed > full_crowding_out` holds for every country and
lever (asserted in `test_financing.py`).

Public investment:

| country | deficit | tax_financed | full_crowding_out |
|---------|--------:|-------------:|------------------:|
| ZAF | 196,670 | 99,838 | 75,631 |
| TUN | 50,412 | 30,107 | 25,030 |
| VNM | 285,787 | -78,784 | -169,927 |
| THA | 262,811 | -11,769 | -80,414 |
| SEN | 44,650 | 9,476 | 682 |

Stimulus, household transfer (was costless to finance; now is not):

| country | deficit | tax_financed | full_crowding_out |
|---------|--------:|-------------:|------------------:|
| ZAF | 107,888 | 11,057 | -13,151 |
| TUN | 16,312 | -3,994 | -9,070 |
| VNM | 380,875 | 16,304 | -74,839 |
| THA | 279,139 | 4,560 | -64,085 |
| SEN | 36,818 | 1,645 | -7,149 |

Stimulus, government consumption (Haavelmo: tax-financed sits between
deficit and full crowding-out, modest, not forced):

| country | deficit | tax_financed | full_crowding_out |
|---------|--------:|-------------:|------------------:|
| ZAF | 170,713 | 73,881 | 49,673 |
| TUN | 31,647 | 11,342 | 6,266 |
| VNM | 416,065 | 51,494 | -39,648 |
| THA | 261,123 | -13,456 | -82,101 |
| SEN | 18,935 | -16,239 | -25,032 |

## 3. Senegal elasticity (Workstream D)

| | value | source |
|--|------|--------|
| old (v1.1.0) | -0.5 | bottom of cited range; the registry note admitted it was lowered so a 10% mfg tariff would not be employment-positive |
| new | **-1.05** | KNO (2008) Table 1, import-weighted Senegal central; used as-is, not calibrated to any outcome |

Consequence: a 10% Senegal manufacturing tariff is now modestly net
**positive** (~5,509 jobs) - a true property of the data with strong
domestic substitution, explicitly **not** a tariff endorsement. The
sign-forcing acceptance tests are removed and replaced with accounting
and transparency tests, plus a guard (`test_no_tariff_sign_forcing_in_tests`)
that fails if any test requires a predetermined tariff sign.

## 4. Changed preset signs (under the new tax_financed default)

Two presets genuinely flip sign; both are correct consequences of C.
Their `expected.net_sign` and walkthroughs were updated to match the
corrected model:

| preset | old default (full_CO) | new default (tax_financed) | change |
|--------|----------------------:|---------------------------:|--------|
| `tun_demand_stimulus` | +25,381 (positive) | -7,987 (**negative**) | stimulus now financing-eligible; TUN high import leakage |
| `tha_direct_public_employment` | -10,038 (~zero) | +58,607 (**positive**) | at MPC 0.8 the labour-intensive programme nets positive |

Two further presets had walkthrough text asserting the now-removed 0.5
fiscal multiplier (a false-provenance issue); corrected to describe the
import-leakage + symmetric-financing mechanism:
`zaf_demand_stimulus`, `zaf_stimulus_government`. Signs unchanged.

Note: the broader preset rework (caveat tags, "financing offset"
relabel, financing-mode field, "What this illustrates / Do not conclude"
lines) is Workstream I, deferred to after this verification.

## 5. Tests

- Full suite: **326 passed, 35 skipped**. The 35 skips are the v1.0.0
  regression lock, superseded by the v1.2 financing model + Senegal
  correction; fixture preserved for audit, to be regenerated in
  Workstream I after sign-off.
- `test_financing.py`: **46 passed** - deficit (no withdrawal),
  tax_financed (= cost x MPC), linearity (tax = full x MPC),
  full_crowding_out reproduces the v1.1.0 baseline numbers, symmetry
  (equal cost -> equal withdrawal regardless of lever), stimulus
  symmetry (transfer vs government purchase), strict ordering, Haavelmo
  bound, deprecated boolean alias, route-helper financing_mode
  propagation.

## 6. Files (working tree, uncommitted)

Engine/API: `backend/app/models/engine.py`, `backend/app/api/schemas.py`,
`backend/app/api/routes.py`, `backend/app/api/lever_params.py`,
`backend/app/api/presets_data.py`.
Registry: `backend/app/data/assumptions.json` (MPC entries; SEN
elasticity -1.05), `data-pipeline/register_engine_params.py`,
`data-pipeline/register_extension_params.py`, `sources.lock.json`.
Tests: `tests/test_financing.py` (new),
`tests/test_engine_tariff_acceptance.py` (rewritten, Workstream D),
`tests/test_engine_core.py`, `tests/test_shock_equivalence.py`,
`tests/test_engine_regression_lock.py` (skip note).
Reports/scripts: `make_baseline_report.py`,
`reports/baseline_before_financing_methodology_fix.json`,
`make_financing_report.py`, `reports/financing_battery.json`, this file.
Docs: `docs/levers/tariff.md`.

## 7. Remaining (after your sign-off)

C.4 frontend (financing-mode selector; gross / offset / net display) is
not yet built - the backend contract is ready. Workstreams E (UI
language, title rename - Header still reads "Job Creation Analysis
Tool"), F (channel-label map, popovers, country caveats), G (job-quality
gained/lost split), and I (preset rework, regression-lock regeneration,
docs cleanup, CHANGELOG + version bump to 1.2.0, final verification
report) follow.
