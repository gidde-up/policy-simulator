"""Workstream E: static UI-language guard.

Fails if active frontend UI text uses misleading forecast/recommendation
wording. Historical changelog/migration text is not scanned (this checks
frontend/src only). Mirrors the no-tariff-sign-forcing guard: a source
scan, not a runtime test.
"""
import re

import config

SRC = config.REPO_ROOT / "frontend" / "src"

# exact phrases that must not appear in active UI text
FORBIDDEN = [
    "projected employment",
    "forecast employment",
    "Job Creation Analysis Tool",
    "recommended policy",
    "optimal policy",
]


def _src_files():
    return [p for p in SRC.rglob("*")
            if p.suffix in (".jsx", ".js") and p.is_file()]


def test_no_forbidden_ui_text():
    offenders = []
    for f in _src_files():
        text = f.read_text(encoding="utf-8")
        for phrase in FORBIDDEN:
            if re.search(re.escape(phrase), text, re.IGNORECASE):
                offenders.append(f"{f.name}: '{phrase}'")
    assert not offenders, f"forbidden UI wording found: {offenders}"


def test_title_renamed():
    header = (SRC / "components" / "Header.jsx").read_text(encoding="utf-8")
    assert "Employment Policy Learning Simulator" in header
    assert "Job Creation Analysis Tool" not in header


def test_not_a_forecast_warning_present():
    """The results page carries the required not-a-forecast notice.
    Whitespace is normalised because JSX wraps text across source lines."""
    raw = (SRC / "components" / "ResultsPanel.jsx").read_text(encoding="utf-8")
    results = re.sub(r"\s+", " ", raw)
    assert "not a forecast or policy recommendation" in results
    # exchange-rate wording replaced
    assert "does not estimate endogenous exchange-rate movements" in results
