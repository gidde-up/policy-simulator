"""Hand-checkable 3-sector toy country exercising the same engine code
paths used in production (CountryData.from_dict injection)."""
import numpy as np
import pytest


@pytest.fixture(scope="module")
def toy(engine):
    """3 sectors; numbers chosen for hand verification.

    Z_dd = [[10, 20,  0],   M = [[ 5,  0, 0],    x = [100, 200, 100]
            [30, 40, 20],        [10, 20, 0],
            [ 0, 10, 10]]        [ 0,  0, 5]]
    A_d = Z diag(x)^-1; va = x - colsums(Z+M) (tls = 0).
    F_dom rows (households, gov, gfcf, inv, exports chosen so the row
    identity x = Z*1 + F*1 holds):
      s0: 100 - 30 = 70  -> hh 40, gov 10, gfcf 10, inv 0, exp 10
      s1: 200 - 90 = 110 -> hh 60, gov 20, gfcf 10, inv 0, exp 20
      s2: 100 - 20 = 80  -> hh 30, gov 20, gfcf 10, inv 0, exp 20
    employment 10/20/5 jobs per sector-million? -> persons 1000/4000/500,
    e = persons/x = [10, 20, 5].
    """
    Z = np.array([[10.0, 20, 0], [30, 40, 20], [0, 10, 10]])
    M = np.array([[5.0, 0, 0], [10, 20, 0], [0, 0, 5]])
    x = np.array([100.0, 200, 100])
    A_d = Z / x
    A_m = M / x
    L_I = np.linalg.inv(np.eye(3) - A_d)
    # Type II: tiny labour closure for testing dominance
    h_r = np.array([0.3, 0.3, 0.3])
    h_c = np.array([0.4, 0.4, 0.2])
    A_star = np.zeros((4, 4))
    A_star[:3, :3] = A_d
    A_star[:3, 3] = h_c
    A_star[3, :3] = h_r
    L_II = np.linalg.inv(np.eye(4) - A_star)[:3, :3]
    persons = np.array([1000.0, 4000, 500])
    va = x - (Z + M).sum(axis=0)
    fd = {
        "households": [40.0, 60, 30],
        "government": [10.0, 20, 20],
        "gfcf": [10.0, 10, 10],
        "inventories": [0.0, 0, 0],
        "exports": [10.0, 20, 20],
    }
    imp_int = M.sum(axis=1)
    imp_fin = np.array([5.0, 10, 0])
    dom_absorb = x - np.array(fd["exports"])
    d = {
        "metadata": {"iso3": "TOY", "country": "Toyland",
                     "reference_year": 2022, "icio_edition": "test",
                     "employment_source": "test", "notes": []},
        "sectors": ["alpha", "beta", "gamma"],
        "A_d": A_d.tolist(), "A_m": A_m.tolist(),
        "L_typeI": L_I.tolist(), "L_typeII": L_II.tolist(),
        "x": x.tolist(), "VA": va.tolist(), "TLS": [0.0, 0, 0],
        "employment_coefficients": (persons / x).tolist(),
        "employment": {"persons": persons.tolist()},
        "final_demand": fd,
        "imported_final_demand": {
            "households": imp_fin.tolist(),
            "government": [0.0, 0, 0],
            "gfcf": [0.0, 0, 0],
            "inventories": [0.0, 0, 0],
        },
        "imports_by_product": {"intermediate": imp_int.tolist(),
                               "final": imp_fin.tolist()},
        "import_shares": {"domestic_absorption":
                          (dom_absorb / (dom_absorb + imp_int + imp_fin)
                           ).tolist()},
        "baseline_totals": {"gdp_usd_million": float(va.sum())},
    }
    return engine.CountryData.from_dict(d)


def test_decompose_identity(engine, toy):
    """L f = x for the baseline final demand (fundamental identity)."""
    f = sum(toy.fd[k] for k in ["households", "government", "gfcf",
                                "inventories", "exports"])
    np.testing.assert_allclose(toy.L_I @ f, toy.x, rtol=1e-12)


def test_decompose_direct_hand_check(engine, toy):
    """dF = +10 in beta: direct = e_beta*10 = 200 jobs; total =
    e' L_I dF, hand-computable."""
    dF = np.array([0.0, 10, 0])
    d = engine.decompose(toy, dF, include_type_ii=False)
    assert d["direct"][1] == pytest.approx(20.0 / 1 * 10)  # e=20 jobs/M
    expected_total = float(toy.e @ (toy.L_I @ dF))
    assert d["total"].sum() == pytest.approx(expected_total, rel=1e-12)
    assert d["induced"].sum() == 0.0


def test_type_ii_dominates(engine, toy):
    dF = np.array([5.0, 5, 5])
    d1 = engine.decompose(toy, dF, include_type_ii=False)
    d2 = engine.decompose(toy, dF, include_type_ii=True)
    assert d2["total"].sum() > d1["total"].sum()
    assert d2["induced"].sum() > 0


def test_sector_support_and_drag(engine, toy):
    dF_sup = engine.sector_support_dF(toy, {"beta": 0.1})
    assert dF_sup[1] == pytest.approx(20.0)        # 0.1 * x_beta(200)
    drag = engine.financing_drag_dF(toy, float(dF_sup.sum()))
    assert drag.sum() == pytest.approx(-20.0)
    # drag spread by household shares
    hh = np.array(toy.fd["households"])
    np.testing.assert_allclose(drag, -20.0 * hh / hh.sum(), rtol=1e-12)


def test_price_effects_hand_check(engine, toy):
    """dp' = dp_m' A_m L_I with a 10% tariff on alpha (imported input)."""
    p = engine.EngineParams(eps=-1.0, eta=-0.5, retaliation_share=0.5,
                            retaliation_top_n=1, fiscal_multiplier=0.5)
    dp = engine.price_effects(toy, {"alpha": 0.1}, p)
    dp_m = np.array([0.1, 0, 0])
    expected = toy.L_I.T @ (toy.A_m.T @ dp_m)
    np.testing.assert_allclose(dp, expected, rtol=1e-12)
    assert (dp >= 0).all() and dp.max() > 0
