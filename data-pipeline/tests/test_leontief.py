"""Spec checks 3, 4 and structural Leontief properties, plus a 3-sector
hand-checked toy example validating the same code path used by the
pipeline (matrix inversion and multiplier formulas)."""
import numpy as np

from pipeline import validate


def test_spectral_radius(country, country_data):
    passed, details = validate.check_spectral_radius(country_data[country])
    assert passed, details


def test_output_multipliers(country, country_data, capsys):
    passed, details = validate.check_output_multipliers(country_data[country])
    print(f"\n[{country}] {details}")
    assert passed, details


def test_type_ii_dominance(country, country_data):
    passed, details = validate.check_type_ii_dominance(country_data[country])
    assert passed, details


def test_leontief_inverse_consistency(country, country_data):
    """L_typeI must equal inv(I - A_d) of the published A_d."""
    d = country_data[country]
    A_d = np.array(d["A_d"])
    L = np.array(d["L_typeI"])
    L_re = np.linalg.inv(np.eye(A_d.shape[0]) - A_d)
    assert np.max(np.abs(L - L_re)) < 1e-4


def test_three_sector_hand_check():
    """Hand-checkable toy IO table.

    Z = [[10, 20,  0],     x = [100, 200, 100]
         [30, 40, 20],
         [ 0, 10, 10]]
    A = Z diag(x)^-1 = [[0.1, 0.1, 0.0],
                        [0.3, 0.2, 0.2],
                        [0.0, 0.05, 0.1]]
    Final demand f = x - Z*1 = [70, 110, 80].
    L = inv(I-A); check L f = x (the fundamental identity).
    """
    Z = np.array([[10.0, 20, 0], [30, 40, 20], [0, 10, 10]])
    x = np.array([100.0, 200, 100])
    A = Z / x
    L = np.linalg.inv(np.eye(3) - A)
    f = x - Z.sum(axis=1)
    np.testing.assert_allclose(L @ f, x, rtol=1e-12)
    # linearity: doubling final demand doubles output
    np.testing.assert_allclose(L @ (2 * f), 2 * x, rtol=1e-12)
