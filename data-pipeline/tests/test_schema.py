"""Country JSON shape and metadata checks."""
import numpy as np

import config

N = len(config.SECTORS_14)

REQUIRED_KEYS = [
    "metadata", "sectors", "A_d", "A_m", "L_typeI", "L_typeII", "x", "VA",
    "TLS", "employment", "employment_coefficients", "final_demand",
    "imported_final_demand", "import_shares", "type_ii", "baseline_totals",
]


def test_required_keys(country, country_data):
    d = country_data[country]
    missing = [k for k in REQUIRED_KEYS if k not in d]
    assert not missing, f"missing keys: {missing}"


def test_sector_order(country, country_data):
    assert country_data[country]["sectors"] == config.SECTORS_14


def test_matrix_shapes(country, country_data):
    d = country_data[country]
    for key in ["A_d", "A_m", "L_typeI", "L_typeII"]:
        assert np.array(d[key]).shape == (N, N), key
    for key in ["x", "VA", "TLS", "employment_coefficients"]:
        assert np.array(d[key]).shape == (N,), key
    assert np.array(d["employment"]["persons"]).shape == (N,)
    for cat in ["households", "government", "gfcf", "inventories", "exports"]:
        assert np.array(d["final_demand"][cat]).shape == (N,), cat


def test_metadata(country, country_data):
    m = country_data[country]["metadata"]
    assert m["iso3"] == country
    assert m["reference_year"] == config.REFERENCE_YEAR
    assert m["icio_edition"] == config.ICIO_EDITION
    assert m["pipeline_version"] == config.PIPELINE_VERSION
    assert m["access_dates"], "access dates must be recorded"
    # no false provenance: employment source must name actual datasets
    assert "TiM" in m["employment_source"]


def test_accounting_identity(country, country_data):
    """x = Z*1 + F*1 must hold on the published aggregates."""
    d = country_data[country]
    x = np.array(d["x"])
    A_d = np.array(d["A_d"])
    Z_row_sums = (A_d * x).sum(axis=1)  # Z = A_d diag(x)
    f = sum(np.array(d["final_demand"][k]) for k in
            ["households", "government", "gfcf", "inventories", "exports"])
    gap = np.abs(Z_row_sums + f - x) / np.maximum(x, 1e-9)
    assert gap.max() < 0.01, f"row identity violated: max gap {gap.max():.4%}"
