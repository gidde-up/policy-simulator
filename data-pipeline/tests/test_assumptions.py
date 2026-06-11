"""Registry integrity: schema-valid entries; every provenance tag in a
country JSON resolves to a registry entry; every entry has a real
source."""
from pipeline import assumptions


def test_registry_schema(registry):
    assert registry["schema_version"] == assumptions.SCHEMA_VERSION
    for e in registry["entries"]:
        assert e["scope"] in assumptions.VALID_SCOPES, e["id"]
        assert e["method"] in assumptions.VALID_METHODS, e["id"]
        assert e["source"]["dataset"], e["id"]
        assert e["source"]["accessed"], e["id"]
        assert isinstance(e["value"], (int, float)), e["id"]
        assert e["basis"] or e["citation"], (
            f"{e['id']}: needs a basis or citation")


def test_provenance_tags_resolve(country, country_data, registry):
    ids = {e["id"] for e in registry["entries"]}
    prov = country_data[country]["employment"].get("provenance", {})
    for sector, tags in prov.items():
        for tag in tags:
            assert tag in ids, f"{country}/{sector}: dangling tag {tag}"


def test_no_orphan_entries(country_data, registry):
    """Every registry entry belongs to a built country."""
    built = set(country_data)
    for e in registry["entries"]:
        assert e["country"] in built, f"orphan entry {e['id']}"
