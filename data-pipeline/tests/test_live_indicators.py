"""Live ILOSTAT context indicators: CSV parsing (latest period, dimension
filters) and graceful fallback. No network is touched - the parser is a
pure function fed canned SDMX-CSV, and the fetch failure path is exercised
by monkeypatching the HTTP getter.
"""
import importlib.util

import config


def _mod():
    path = config.REPO_ROOT / "backend" / "app" / "api" / "live_indicators.py"
    spec = importlib.util.spec_from_file_location("live_indicators", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# real ILOSTAT SDMX-CSV shape (subset of columns used by the parser)
INFORMALITY_CSV = (
    "REF_AREA,SEX,TIME_PERIOD,OBS_VALUE,SOURCE\n"
    "ZAF,SEX_T,2024-Q4,33.0,LFS - QLFS\n"
    "ZAF,SEX_T,2025-Q2,34.894,LFS - QLFS\n"   # latest, total
    "ZAF,SEX_M,2025-Q2,30.0,LFS - QLFS\n"     # wrong sex, ignored
    "TUN,SEX_T,2019,36.899,LFS\n"
    "SEN,SEX_T,2025-Q1,91.177,LFS\n"
)

WP_CSV = (
    "REF_AREA,SEX,AGE,TIME_PERIOD,OBS_VALUE,SOURCE\n"
    "ZAF,SEX_T,AGE_YTHADULT_YGE15,2025,14.475,ILO Modelled\n"  # total 15+
    "ZAF,SEX_T,AGE_YTHADULT_Y15-24,2025,20.0,ILO Modelled\n"   # youth, ignored
    "ZAF,SEX_M,AGE_YTHADULT_YGE15,2025,12.0,ILO Modelled\n"    # male, ignored
)


def test_parse_informality_latest_total():
    m = _mod()
    out = m.parse_indicator_csv(INFORMALITY_CSV, {"SEX": "SEX_T"})
    assert out["ZAF"]["value"] == 34.894
    assert out["ZAF"]["period"] == "2025-Q2"
    assert out["ZAF"]["year"] == 2025
    assert out["TUN"]["year"] == 2019
    assert out["SEN"]["value"] == 91.177


def test_parse_working_poverty_age_filter():
    m = _mod()
    out = m.parse_indicator_csv(
        WP_CSV, {"SEX": "SEX_T", "AGE": "AGE_YTHADULT_YGE15"})
    assert set(out) == {"ZAF"}
    assert out["ZAF"]["value"] == 14.475   # not the youth or male rows


def test_parse_skips_blank_values():
    m = _mod()
    csv = ("REF_AREA,SEX,TIME_PERIOD,OBS_VALUE,SOURCE\n"
           "ZAF,SEX_T,2025,,LFS\n")
    assert m.parse_indicator_csv(csv, {"SEX": "SEX_T"}) == {}


def test_fetch_failure_falls_back_to_empty(monkeypatch):
    m = _mod()

    def boom(url):
        raise OSError("network blocked")

    monkeypatch.setattr(m, "_http_get", boom)
    m._state["data"] = None
    m._state["ts"] = 0.0
    m._state["fail_ts"] = 0.0
    assert m.get_live(now=1000.0) == {}
    assert m.get_country_live("ZAF") == {}


def test_cache_served_within_ttl(monkeypatch):
    m = _mod()
    calls = {"n": 0}

    def fake_fetch():
        calls["n"] += 1
        return {"ZAF": {"informality": {"value": 34.9, "year": 2025,
                                        "period": "2025-Q2", "source": "LFS"}}}

    monkeypatch.setattr(m, "_fetch_all", fake_fetch)
    m._state["data"] = None
    m._state["ts"] = 0.0
    m._state["fail_ts"] = 0.0
    a = m.get_live(now=1000.0)
    b = m.get_live(now=1000.0 + 10)   # within TTL -> cached, no refetch
    assert a is b
    assert calls["n"] == 1
    assert m.get_country_live("ZAF")["informality"]["value"] == 34.9
