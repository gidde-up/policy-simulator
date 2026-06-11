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
    p = preset["params"]
    return engine.run_scenario(
        preset["country_code"],
        tariffs={s: v / 100 for s, v in p.get("tariff_changes", {}).items()},
        sector_support={s: v / 100
                        for s, v in p.get("sector_support", {}).items()},
        sme_stimulus=p.get("sme_stimulus", 0) / 100,
    )


def test_presets_structure(presets):
    assert len(presets) == 15
    ids = [p["id"] for p in presets]
    assert len(set(ids)) == 15
    for p in presets:
        assert p["country_code"] in config.COUNTRIES
        assert p["walkthrough"], p["id"]
        assert p["expected"]["net_sign"] in ("positive", "negative",
                                             "near_zero")


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
