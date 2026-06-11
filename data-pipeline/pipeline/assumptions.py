"""Assumptions registry: backend/app/data/assumptions.json.

Every value in a country JSON that was not computed 1:1 from a source
dataset (fallbacks, allocations, caps) gets an entry here. The registry
is the single audit trail; country JSONs reference entries by id.
"""
import datetime
import json

import config

SCHEMA_VERSION = "1.0"

VALID_SCOPES = {"employment", "labour_compensation", "manufacturing_split",
                "consumption_propensity", "elasticity", "other"}
VALID_METHODS = {"ILOSTAT_fallback", "child_sum", "proportional_allocation",
                 "authored_constant", "cap", "clip", "economy_share"}

# country code used for engine-wide behavioural parameters that are not
# tied to a single economy (import demand elasticity, fiscal multiplier...)
GLOBAL_COUNTRY = "GLOBAL"


def new_registry():
    return {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": config.PIPELINE_VERSION,
        "updated": datetime.date.today().isoformat(),
        "entries": [],
    }


def make_entry(*, entry_id: str, country: str, scope: str, sector: str,
               field: str, icio_codes: list[str], value: float, unit: str,
               method: str, basis: str, source: dict, citation: str = "",
               notes: str = ""):
    assert scope in VALID_SCOPES, scope
    assert method in VALID_METHODS, method
    return {
        "id": entry_id,
        "country": country,
        "reference_year": config.REFERENCE_YEAR,
        "scope": scope,
        "sector": sector,
        "field": field,
        "icio_codes": icio_codes,
        "value": round(float(value), 4),
        "unit": unit,
        "method": method,
        "basis": basis,
        "source": source,
        "citation": citation,
        "notes": notes,
    }


def write_registry(registry: dict):
    registry["updated"] = datetime.date.today().isoformat()
    config.ASSUMPTIONS_JSON.parent.mkdir(parents=True, exist_ok=True)
    config.ASSUMPTIONS_JSON.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")


def load_registry():
    if config.ASSUMPTIONS_JSON.exists():
        return json.loads(config.ASSUMPTIONS_JSON.read_text(encoding="utf-8"))
    return new_registry()


def replace_country_entries(registry: dict, country: str,
                            entries: list[dict]):
    """Idempotent rebuild: drop this country's entries, append new ones."""
    registry["entries"] = [e for e in registry["entries"]
                           if e.get("country") != country] + entries
    return registry


def replace_pipeline_entries(registry: dict, country: str,
                             entries: list[dict]):
    """Like replace_country_entries, but preserves authored engine
    parameters (method=authored_constant) registered for the country --
    a data rebuild must not delete cited behavioural parameters."""
    registry["entries"] = [
        e for e in registry["entries"]
        if e.get("country") != country
        or e.get("method") == "authored_constant"
    ] + entries
    return registry
