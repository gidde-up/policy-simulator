"""Spec checks 1 and 2: coefficient column sums and non-negativity."""
from pipeline import validate


def test_coefficient_sums(country, country_data):
    passed, details = validate.check_coefficient_sums(country_data[country])
    assert passed, details


def test_nonnegative(country, country_data):
    passed, details = validate.check_nonnegative(country_data[country])
    assert passed, details
