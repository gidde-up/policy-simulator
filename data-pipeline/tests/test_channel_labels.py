"""Workstream F.1: the central channel-label map must cover every channel
key the engine can emit, and no user-facing label may be raw snake_case.

The map lives in frontend/src/channelLabels.js (the single source used by
the results UI and guided-mode summaries). This test parses it and checks
coverage against the keys the engine actually emits across a lever
battery, so the two cannot drift.
"""
import re

import pytest

import config

LABELS_JS = config.REPO_ROOT / "frontend" / "src" / "channelLabels.js"

# the four user-facing tariff-channel keys (engine maps internal names to
# these in run_scenario's tariff_channels block)
TARIFF_KEYS = {"protected_sector_gain", "downstream_cost",
               "real_income_loss", "retaliation"}

BATTERY = [
    dict(tariffs={"manufacturing": 0.10}, include_retaliation=True),
    dict(sector_support={"construction": 0.05}),
    dict(sme_stimulus=0.01),
    dict(sme_stimulus=0.01, extensions={"stimulus_target": "government"}),
    dict(extensions={"public_investment": {"amount_pct_gdp": 0.01}}),
    dict(extensions={"production_subsidy": {"manufacturing": 1.0}}),
    dict(extensions={"wage_subsidy": {"manufacturing": 1.0}}),
    dict(extensions={"investment_tax_incentive":
                     {"fiscal_cost_pct_gdp": 0.01, "intensity": 0.3}}),
    dict(extensions={"public_works": {"budget_pct_gdp": 0.01,
                                      "method": "labour_based"}}),
    dict(extensions={"public_works": {"budget_pct_gdp": 0.01,
                                      "method": "conventional"}}),
    dict(extensions={"direct_public_employment": {"budget_pct_gdp": 0.01}}),
    dict(extensions={"depreciation": 0.10}),
]


def _parse_labels():
    """Return {key: label} from the JS map (flat object of string labels)."""
    text = LABELS_JS.read_text(encoding="utf-8")
    pairs = re.findall(r"^\s*([A-Za-z_]+):\s*\{\s*label:\s*'([^']*)'",
                       text, re.MULTILINE)
    return dict(pairs)


def _emitted_keys(engine):
    keys = set()
    for s in BATTERY:
        for tii in (False, True):
            r = engine.run_scenario("ZAF", include_type_ii=tii, **s)
            if r["tariff_channels"]:
                keys |= {k for k, v in r["tariff_channels"].items() if v}
            if r["other_channels"]:
                keys |= set(r["other_channels"].keys())
    return keys


def test_map_covers_every_emitted_channel(engine):
    labels = _parse_labels()
    emitted = _emitted_keys(engine)
    missing = sorted(emitted - set(labels))
    assert not missing, f"channel keys with no label: {missing}"


def test_no_snake_case_label():
    """No label value may contain a snake_case token (lowercase_lowercase),
    i.e. no raw engine key leaks into user-facing text."""
    labels = _parse_labels()
    bad = {k: v for k, v in labels.items() if re.search(r"[a-z]_[a-z]", v)}
    assert not bad, f"snake_case labels: {bad}"
    # also: the label must differ from the raw key
    same = {k for k, v in labels.items() if k == v}
    assert not same, f"labels identical to the key: {same}"


def test_financing_label_is_offset():
    """User-facing financing label is 'Financing offset', never 'drag'."""
    labels = _parse_labels()
    assert labels.get("financing_drag") == "Financing offset"
    assert "drag" not in labels.get("financing_drag", "").lower()
