"""Every curated scenario must run on the engine and 'tell a true
story': the sign/structure claims its walkthrough makes are asserted
here against the actual engine output (Phase 3 requirement)."""
import importlib.util

import pytest

import config


@pytest.fixture(scope="module")
def presets():
    path = (config.REPO_ROOT / "backend" / "app" / "api"
            / "presets_data.py")
    spec = importlib.util.spec_from_file_location("presets_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRESETS


def _run(engine, preset):
    # use the EXACT conversion the /api/simulate route uses, so the
    # tests and the live app can never drift on percent->fraction
    return engine.run_scenario(preset["country_code"],
                               **_to_engine_kwargs(preset["params"]))


def _load_lever_params():
    """Load backend/app/api/lever_params.py by file path (the shared
    API conversion helper; no FastAPI dependency)."""
    import importlib.util
    path = (config.REPO_ROOT / "backend" / "app" / "api"
            / "lever_params.py")
    spec = importlib.util.spec_from_file_location("lever_params", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_to_engine_kwargs = _load_lever_params().to_engine_kwargs


_FISCAL_LEVERS = ("sector_support", "sme_stimulus", "production_subsidy",
                  "wage_subsidy", "public_investment", "public_works",
                  "direct_public_employment", "investment_tax_incentive")


def test_presets_structure(presets):
    assert len(presets) == 28
    ids = [p["id"] for p in presets]
    assert len(set(ids)) == len(presets)
    for p in presets:
        assert p["country_code"] in config.COUNTRIES
        assert p["walkthrough"], p["id"]
        assert p["expected"]["net_sign"] in ("positive", "negative",
                                             "near_zero")


def test_presets_guided_metadata(presets):
    """Workstream I.1: every preset carries the guided-mode metadata, every
    fiscal preset has a financing mode, and no user-facing summary leaks a
    raw snake_case key."""
    import re
    snake = re.compile(r"[a-z]_[a-z]")
    for p in presets:
        assert p.get("lever_group"), p["id"]
        assert p.get("illustrates"), p["id"]
        assert p.get("do_not_conclude"), p["id"]
        assert isinstance(p.get("caveat_tags"), list) and p["caveat_tags"], p["id"]
        # summaries are prose -- no raw snake_case channel/param keys
        for fld in ("illustrates", "do_not_conclude"):
            assert not snake.search(p[fld]), (p["id"], fld, p[fld])
        # caveat tags are kebab-case, never snake_case
        for t in p["caveat_tags"]:
            assert "_" not in t, (p["id"], t)
        has_fiscal = any(p["params"].get(k) for k in _FISCAL_LEVERS)
        if has_fiscal:
            assert p.get("financing_mode") == "tax_financed", p["id"]
        else:
            assert p.get("financing_mode") is None, p["id"]


def test_presets_tell_true_stories(engine, presets, capsys):
    for preset in presets:
        r = _run(engine, preset)
        net = r["aggregate"]["total_jobs"]
        baseline = r["baseline"]["sector_sum_employment_persons"]
        exp = preset["expected"]
        print(f"{preset['id']}: net {net:,.0f} ({net / baseline:+.3%})")
        if exp["net_sign"] == "positive":
            assert net > 0, f"{preset['id']}: claims positive, got {net:,.0f}"
        elif exp["net_sign"] == "negative":
            assert net < 0, f"{preset['id']}: claims negative, got {net:,.0f}"
        else:  # near_zero: the walkthrough says "approximately zero"
            assert abs(net) < 0.001 * baseline, (
                f"{preset['id']}: claims near-zero, got {net:,.0f} "
                f"({net / baseline:+.3%})")
        if exp.get("has_tariff_channels"):
            assert r["tariff_channels"] is not None, preset["id"]
        else:
            assert r["tariff_channels"] is None, preset["id"]
        if exp.get("gains_positive"):
            gain = r["tariff_channels"]["protected_sector_gain"]
            assert gain and gain["jobs"] > 0, preset["id"]
        if exp.get("has_windfall"):
            assert r.get("investment_incentive"), preset["id"]
            assert r["investment_incentive"]["windfall_usd_million"] > 0
        if exp.get("has_job_years"):
            assert r.get("job_years_note"), preset["id"]
