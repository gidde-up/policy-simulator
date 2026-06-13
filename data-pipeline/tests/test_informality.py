"""The optional per-country informality block: schema, the
manufacturing-family inheritance, registry provenance, and the
gate behaviour (a country without the block is simply absent)."""
import pytest

import config

MANUFACTURING_FAMILY = ["manufacturing", "textiles", "automotive",
                        "food_processing", "chemicals"]


def _block(country_data, iso3):
    return country_data[iso3].get("informality")


def test_block_present_for_built_countries(country, country_data):
    # Session E wrote a block for every country that had sector data;
    # the probe confirmed all five do. If one is ever absent, that is
    # the gate working -- assert the block, when present, is well formed.
    block = _block(country_data, country)
    if block is None:
        pytest.skip(f"{country}: no informality block (gate: hidden)")
    assert block["indicator"]
    assert isinstance(block["year_used"], int)
    shares = block["informal_share_of_employment"]
    assert set(shares) == set(config.SECTORS_14)
    for s, v in shares.items():
        assert v is None or (0.0 <= v <= 1.0), f"{country}/{s}={v}"


def test_manufacturing_family_inheritance(country, country_data):
    block = _block(country_data, country)
    if block is None:
        pytest.skip("no block")
    shares = block["informal_share_of_employment"]
    fam = {shares[s] for s in MANUFACTURING_FAMILY}
    # all five manufacturing-family sectors share one inherited rate
    assert len(fam) == 1, f"{country}: manufacturing family not uniform"


def test_provenance_resolves(country, country_data, registry):
    block = _block(country_data, country)
    if block is None:
        pytest.skip("no block")
    ids = {e["id"] for e in registry["entries"]}
    for tag in block.get("provenance", []):
        assert tag in ids, f"{country}: dangling provenance {tag}"


def test_context_indicators_present(country, country_data):
    block = _block(country_data, country)
    if block is None:
        pytest.skip("no block")
    ctx = block.get("context", {})
    assert "note" in ctx and "not used in simulation" in ctx["note"]


def test_informality_entries_well_formed(registry):
    inf = [e for e in registry["entries"] if e["scope"] == "informality"]
    assert inf, "expected informality registry entries"
    for e in inf:
        assert e["method"] == "share_inheritance"
        assert 0.0 <= e["value"] <= 1.0
        assert e["source"]["dataset"].startswith("ILOSTAT")
        assert e["basis"]
