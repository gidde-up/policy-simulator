"""The acceptance constraint (CLAUDE.md ground rule 4): under default
parameters a unilateral tariff increase must NOT produce a net positive
aggregate employment effect (Flaaen & Pierce 2019; Amiti, Redding &
Weinstein 2019).

Test tolerances (not model parameters, hence defined here, not in the
assumptions registry):
  - net employment <= +0.05% of baseline sector-sum employment with
    retaliation off (allows tiny positive noise, per the overhaul spec);
  - strictly negative with retaliation on;
  - protected-sector gains at least 60% offset by losses elsewhere.
"""
import pytest

from tests.conftest import BUILT_COUNTRIES

TARIFF = 0.10
SECTOR = "manufacturing"
NET_CEILING_SHARE = 0.0005   # +0.05% of baseline employment
MIN_OFFSET = 0.60


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def test_tariff_not_net_positive(engine, iso3, capsys):
    r = engine.run_scenario(iso3, tariffs={SECTOR: TARIFF})
    net = r["aggregate"]["total_jobs"]
    baseline = r["baseline"]["sector_sum_employment_persons"]
    share = net / baseline
    print(f"\n[{iso3}] 10% {SECTOR} tariff: net {net:,.0f} jobs "
          f"({share:+.3%} of baseline)")
    assert share <= NET_CEILING_SHARE, (
        f"{iso3}: net {net:,.0f} (+{share:.3%}) exceeds the acceptance "
        f"ceiling; recalibrate ONLY cited parameters within their "
        f"literature ranges (see assumptions registry)")


def test_tariff_negative_with_retaliation(engine, iso3):
    r = engine.run_scenario(iso3, tariffs={SECTOR: TARIFF},
                            include_retaliation=True)
    assert r["aggregate"]["total_jobs"] < 0, (
        f"{iso3}: must be net negative with retaliation on")


def test_protected_gains_offset(engine, iso3):
    r = engine.run_scenario(iso3, tariffs={SECTOR: TARIFF})
    gains = sum(s["total_jobs"] for s in r["sector_effects"]
                if s["total_jobs"] > 0)
    losses = -sum(s["total_jobs"] for s in r["sector_effects"]
                  if s["total_jobs"] < 0)
    assert gains > 0, f"{iso3}: expected some protected-sector gain"
    assert losses >= MIN_OFFSET * gains, (
        f"{iso3}: losses {losses:,.0f} offset only "
        f"{losses / gains:.0%} of gains {gains:,.0f} (need >= 60%)")
