"""DirectEmployment shock on a hand-built toy economy WITH a Miyazawa
type_ii block. Verifies job placement, the Type II wage-bill recycling
(e * L_II * h_c * W), the closure identity it rests on, and the
no-type_ii guard."""
import numpy as np
import pytest


@pytest.fixture(scope="module")
def toy(engine):
    """3-sector toy with an explicit household closure."""
    Z = np.array([[10.0, 20, 0], [30, 40, 20], [0, 10, 10]])
    M = np.array([[5.0, 0, 0], [10, 20, 0], [0, 0, 5]])
    x = np.array([100.0, 200, 100])
    A_d = Z / x
    A_m = M / x
    L_I = np.linalg.inv(np.eye(3) - A_d)
    h_r = np.array([0.3, 0.3, 0.3])
    h_c = np.array([0.4, 0.4, 0.2])
    A_star = np.zeros((4, 4))
    A_star[:3, :3] = A_d
    A_star[:3, 3] = h_c
    A_star[3, :3] = h_r
    L_II = np.linalg.inv(np.eye(4) - A_star)[:3, :3]
    persons = np.array([1000.0, 4000, 500])
    va = x - (Z + M).sum(axis=0)
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
        "final_demand": {"households": [40.0, 60, 30],
                         "government": [10.0, 20, 20],
                         "gfcf": [10.0, 10, 10], "inventories": [0.0, 0, 0],
                         "exports": [10.0, 20, 20]},
        "imported_final_demand": {"households": [5.0, 10, 0],
                                  "government": [0.0, 0, 0],
                                  "gfcf": [0.0, 0, 0],
                                  "inventories": [0.0, 0, 0]},
        "imports_by_product": {"intermediate": M.sum(axis=1).tolist(),
                               "final": [5.0, 10, 0]},
        "import_shares": {"domestic_absorption": [0.5, 0.5, 0.5]},
        "baseline_totals": {"gdp_usd_million": float(va.sum())},
        "type_ii": {"consumption_coefficients": h_c.tolist(),
                    "labour_income_coefficients": h_r.tolist()},
    }
    return engine.CountryData.from_dict(d)


def _params(engine):
    return engine.EngineParams(eps=-1.0, eta=-0.5, retaliation_share=0.5,
                               retaliation_top_n=1, fiscal_multiplier=0.5)


def test_direct_jobs_placement_type_i(engine, toy):
    """Type II off: 100 direct jobs in beta, nothing else."""
    de = engine.DirectEmployment(jobs=100.0, wage_bill=5.0,
                                 sector="beta", channel="public_works")
    r = engine.evaluate_scenario(toy, _params(engine), [de],
                                 include_type_ii=False)
    assert r["direct"][1] == pytest.approx(100.0)
    assert r["induced"].sum() == pytest.approx(0.0)
    assert r["total"].sum() == pytest.approx(100.0)
    assert r["direct_employment_channels"]["public_works"] == pytest.approx(100.0)


def test_direct_jobs_type_ii_recycling(engine, toy):
    """Type II on: induced == e * L_II * (h_c * wage_bill), hand-checked."""
    W = 8.0
    de = engine.DirectEmployment(jobs=100.0, wage_bill=W,
                                 sector="beta", channel="public_works")
    r = engine.evaluate_scenario(toy, _params(engine), [de],
                                 include_type_ii=True)
    expected_induced = toy.e * (toy.L_II @ (toy.consumption_coefficients * W))
    np.testing.assert_allclose(r["induced"], expected_induced, rtol=1e-12)
    assert r["direct"][1] == pytest.approx(100.0)
    assert r["total"].sum() == pytest.approx(
        100.0 + expected_induced.sum(), rel=1e-12)
    # channel jobs include the induced recycling
    assert r["direct_employment_channels"]["public_works"] == pytest.approx(
        100.0 + expected_induced.sum(), rel=1e-12)


def test_miyazawa_closure_identity(engine, toy):
    """L_II @ h_c == s * (L_I @ h_c) with s = 1/(1 - h_r' L_I h_c):
    the identity the wage-bill recycling rests on."""
    h_c = toy.consumption_coefficients
    h_r = toy.labour_income_coefficients
    s = 1.0 / (1.0 - h_r @ (toy.L_I @ h_c))
    np.testing.assert_allclose(toy.L_II @ h_c, s * (toy.L_I @ h_c),
                               rtol=1e-9)


def test_type_ii_without_block_raises(engine):
    """A DirectEmployment with Type II on must fail loudly when the
    country has no Miyazawa block (never silently zero)."""
    Z = np.array([[10.0, 20, 0], [30, 40, 20], [0, 10, 10]])
    M = np.array([[5.0, 0, 0], [10, 20, 0], [0, 0, 5]])
    x = np.array([100.0, 200, 100])
    A_d = Z / x
    L_I = np.linalg.inv(np.eye(3) - A_d)
    d = {
        "metadata": {"iso3": "TOY2", "country": "Toyless",
                     "reference_year": 2022, "icio_edition": "test",
                     "employment_source": "test", "notes": []},
        "sectors": ["alpha", "beta", "gamma"],
        "A_d": A_d.tolist(), "A_m": (M / x).tolist(),
        "L_typeI": L_I.tolist(), "L_typeII": L_I.tolist(),
        "x": x.tolist(), "VA": (x - (Z + M).sum(axis=0)).tolist(),
        "TLS": [0.0, 0, 0],
        "employment_coefficients": [1.0, 1, 1],
        "employment": {"persons": [100.0, 200, 100]},
        "final_demand": {"households": [40.0, 60, 30],
                         "government": [10.0, 20, 20],
                         "gfcf": [10.0, 10, 10], "inventories": [0.0, 0, 0],
                         "exports": [10.0, 20, 20]},
        "imported_final_demand": {"households": [5.0, 10, 0],
                                  "government": [0.0, 0, 0],
                                  "gfcf": [0.0, 0, 0],
                                  "inventories": [0.0, 0, 0]},
        "imports_by_product": {"intermediate": M.sum(axis=1).tolist(),
                               "final": [5.0, 10, 0]},
        "import_shares": {"domestic_absorption": [0.5, 0.5, 0.5]},
        "baseline_totals": {"gdp_usd_million": 100.0},
    }
    cd = engine.CountryData.from_dict(d)
    assert cd.consumption_coefficients is None
    de = engine.DirectEmployment(jobs=10.0, wage_bill=1.0,
                                 sector="beta", channel="x")
    with pytest.raises(ValueError):
        engine.evaluate_scenario(cd, _params(engine), [de],
                                 include_type_ii=True)
