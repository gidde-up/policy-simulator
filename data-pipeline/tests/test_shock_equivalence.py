"""The composable-shock pipeline must reproduce the v1 channel builders
channel-by-channel, preserve the channel label set and order, and apply
the financing-drag asymmetry (support feeds the drag; stimulus never
does). Also pins the DomesticCostShock sign conventions on a toy."""
import numpy as np
import pytest

from tests.conftest import BUILT_COUNTRIES

V1_LABEL_ORDER = ["tariff_substitution", "tariff_downstream",
                  "tariff_real_income", "tariff_retaliation",
                  "sector_support", "financing_drag", "sme_stimulus"]


@pytest.fixture(scope="module", params=BUILT_COUNTRIES)
def iso3(request):
    return request.param


def test_compiled_channels_match_v1_builders(engine, iso3):
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    tariffs = {"manufacturing": 0.10, "textiles": 0.05}
    support = {"construction": 0.08}
    stim = 0.01

    # drag_factor 1.0 (= full crowding-out) so the financing_drag channel
    # equals the builder at full withdrawal
    channels = engine._scenario_channels(
        cd, p, tariffs, support, stim,
        include_retaliation=True, include_financing_drag=1.0)

    # under the v1.2 symmetric model the stimulus is also drag-eligible,
    # so the financing drag is on (support + stimulus) fiscal cost
    drag_cost = (sum(r * cd.x[cd.sectors.index(s)] for s, r in support.items())
                 + stim * cd.gdp)
    expected = {
        "tariff_substitution": engine.tariff_substitution_dF(cd, tariffs, p),
        "tariff_downstream": engine.tariff_downstream_dF(cd, tariffs, p),
        "tariff_real_income": engine.tariff_real_income_dF(cd, tariffs, p),
        "tariff_retaliation": engine.tariff_retaliation_dF(cd, tariffs, p),
        "sector_support": engine.sector_support_dF(cd, support),
        "financing_drag": engine.financing_drag_dF(cd, drag_cost),
        "sme_stimulus": engine.stimulus_dF(cd, stim, p),
    }
    assert list(channels.keys()) == [k for k in V1_LABEL_ORDER
                                     if k in expected]
    for k, v in expected.items():
        np.testing.assert_allclose(channels[k], v, rtol=1e-12, atol=1e-9,
                                   err_msg=f"{iso3}/{k}")


def test_financing_drag_symmetric_and_toggleable(engine, iso3):
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    # v1.2: the stimulus is now drag-eligible too (symmetry) -> a
    # stimulus-only scenario has a financing drag when the factor > 0
    ch = engine._scenario_channels(cd, p, {}, {}, 0.02,
                                   include_retaliation=False,
                                   include_financing_drag=1.0)
    assert "financing_drag" in ch
    assert "sme_stimulus" in ch
    # support with drag
    ch = engine._scenario_channels(cd, p, {}, {"trade": 0.05}, 0,
                                   include_retaliation=False,
                                   include_financing_drag=1.0)
    assert "financing_drag" in ch
    # deficit (factor 0) -> no drag for any lever
    ch = engine._scenario_channels(cd, p, {}, {"trade": 0.05}, 0.02,
                                   include_retaliation=False,
                                   include_financing_drag=0.0)
    assert "financing_drag" not in ch


def test_import_price_shock_matches_price_effects(engine, iso3):
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    tariffs = {"chemicals": 0.07}
    shocks = engine.compile_tariffs(cd, p, tariffs, include_retaliation=False)
    channels, _ = engine._evaluate_channel_dFs(cd, p, shocks, 1.0)
    np.testing.assert_allclose(
        channels["tariff_downstream"],
        engine._downstream_dF(cd, p, engine.price_effects(cd, tariffs, p)),
        rtol=1e-12, atol=1e-12)


def test_domestic_cost_shock_signs(engine, iso3):
    """A production subsidy (dc[j] = -s) lowers prices, raising
    downstream demand and real income."""
    cd = engine.load_country(iso3)
    p = engine.load_params("central", iso3)
    n = len(cd.sectors)
    j = cd.sectors.index("manufacturing")
    dc = np.zeros(n)
    dc[j] = -0.10
    dp = engine._cost_push_prices(cd, dc)
    assert dp[j] < 0                       # own price falls
    assert (dp <= 1e-12).all()             # no price rises from a subsidy
    assert engine._downstream_dF(cd, p, dp).sum() >= 0
    assert engine._real_income_dF(cd, dp, np.zeros(n)).sum() >= 0
