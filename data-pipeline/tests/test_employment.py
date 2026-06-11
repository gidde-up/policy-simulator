"""Spec check 5: sectoral employment vs ILOSTAT national total."""
import numpy as np

from pipeline import validate


def test_employment_total(country, country_data, capsys):
    passed, details = validate.check_employment_total(country_data[country])
    print(f"\n[{country}] {details}")
    assert passed, details


def test_employment_coefficients_consistent(country, country_data):
    """e = employment / x must hold on the published values."""
    d = country_data[country]
    e = np.array(d["employment_coefficients"])
    persons = np.array(d["employment"]["persons"])
    x = np.array(d["x"])
    np.testing.assert_allclose(e, persons / x, rtol=1e-3)


def test_employment_positive(country, country_data):
    persons = np.array(country_data[country]["employment"]["persons"])
    assert (persons > 0).all(), "every sector must employ someone"
