"""Live national labour-market context indicators from the ILOSTAT SDMX
API (informality rate and working-poverty rate), latest available year.

These are CONTEXT indicators only (shown in the Data tab); they are never
used in the simulation arithmetic. The sectoral informality used by the
job-quality module stays in the verified country JSONs - it is a model
input and must remain reproducible/hash-locked, so it is NOT fetched here.

Design: one cached fetch of each dataflow's latest observation for all
areas (24h TTL), parsed to {iso3: {value, year, period, source}}. Any
network/parse failure returns whatever is cached, else {} - the API layer
then falls back to the verified static snapshot. No third-party deps
(stdlib urllib + csv); no FastAPI import, so it is unit-testable by file
path. Source: ILOSTAT, https://ilostat.ilo.org (SDMX REST).
"""
import csv
import io
import time
import urllib.request

_SDMX = ("https://sdmx.ilo.org/rest/data/ILO,{flow},1.0/"
         "?format=csv&lastNObservations=1")

# indicator -> (SDMX dataflow, dimension filters selecting the total series)
FLOWS = {
    "informality": ("DF_EMP_NIFL_SEX_RT", {"SEX": "SEX_T"}),
    "working_poverty": ("DF_SDG_0111_SEX_AGE_RT",
                        {"SEX": "SEX_T", "AGE": "AGE_YTHADULT_YGE15"}),
}

_TIMEOUT = 8         # seconds per request
_TTL = 86400         # cache for 24h
_RETRY_AFTER_FAIL = 300   # after a failure, do not hammer for 5 min
_state = {"data": None, "ts": 0.0, "fail_ts": 0.0}


def parse_indicator_csv(text: str, filters: dict) -> dict:
    """{iso3: {value, year, period, source}} keeping, per country, the row
    with the latest TIME_PERIOD among those matching every filter. Pure
    function (no network) so it is directly unit-testable."""
    out: dict = {}
    for row in csv.DictReader(io.StringIO(text)):
        if any(row.get(k) != v for k, v in filters.items()):
            continue
        iso3 = row.get("REF_AREA")
        period = row.get("TIME_PERIOD") or ""
        raw = row.get("OBS_VALUE")
        if not iso3 or not period or raw in (None, ""):
            continue
        # TIME_PERIOD sorts correctly as a string ("2024-Q4" < "2025"
        # < "2025-Q2"); the year prefix dominates.
        cur = out.get(iso3)
        if cur is not None and period <= cur["period"]:
            continue
        try:
            value = float(raw)
        except ValueError:
            continue
        out[iso3] = {"value": value, "year": int(period[:4]),
                     "period": period, "source": row.get("SOURCE") or ""}
    return out


def _http_get(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "policy-simulator/live-indicators"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        return resp.read().decode("utf-8")


def _fetch_all() -> dict:
    data: dict = {}
    for key, (flow, filters) in FLOWS.items():
        parsed = parse_indicator_csv(_http_get(_SDMX.format(flow=flow)),
                                     filters)
        for iso3, rec in parsed.items():
            data.setdefault(iso3, {})[key] = rec
    return data


def get_live(now: float | None = None) -> dict:
    """Cached {iso3: {informality:{...}, working_poverty:{...}}}.
    Returns {} (never raises) when the source is unreachable and nothing
    is cached, so callers fall back to the static snapshot."""
    now = time.time() if now is None else now
    if _state["data"] is not None and now - _state["ts"] < _TTL:
        return _state["data"]
    if _state["data"] is None and now - _state["fail_ts"] < _RETRY_AFTER_FAIL:
        return {}
    try:
        data = _fetch_all()
        if not data:
            raise ValueError("empty response")
        _state["data"] = data
        _state["ts"] = now
        return data
    except Exception:
        _state["fail_ts"] = now
        return _state["data"] or {}


def get_country_live(iso3: str) -> dict:
    """{informality:{...}|absent, working_poverty:{...}|absent} for one
    country (empty dict when live data is unavailable)."""
    return (get_live() or {}).get(iso3.upper(), {})
