"""Source acquisition and provenance recording.

OECD endpoints sit behind a bot challenge (verified 2026-06-10): scripted
download returns HTTP 403 from this network for www.oecd.org,
webfs-sti.oecd.org and sdmx.oecd.org alike. The pipeline therefore
supports two acquisition methods, both recorded in sources.lock.json:

  script  -- direct download (attempted first; works for ILOSTAT)
  manual  -- user downloads in a real browser and drops the file into
             data-pipeline/raw/; the pipeline detects it, hashes it and
             records provenance.

Every acquired file gets an entry: url, filename, sha256, bytes,
access_date, method. Ground rule: no file without recorded provenance.
"""
import datetime
import hashlib
import json

import httpx

import config
from pipeline.errors import PipelineError

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/126.0.0.0 Safari/537.36")

# The ICIO 2025-edition bundle covering reference year 2022
# (regular "SML" version: 80 economies + ROW; "EXT" = China/Mexico split).
# URL discovered from the OECD dataset page (via Wayback snapshot of
# https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html).
ICIO_ZIP_URL = "https://webfs-sti.oecd.org/files/STI-PIE/ICIO/2025/2016-2022_SML.zip"
ICIO_ZIP_NAME = "2016-2022_SML.zip"

TIM_URL_TEMPLATE = (
    "https://sdmx.oecd.org/public/rest/data/"
    "OECD.STI.PIE,DSD_TIM_2025@DF_TIM_2025,1.0/"
    "{measure}.{countries}....A"
    "?startPeriod={year}&endPeriod={year}&format=csvfilewithlabels"
)


def _sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _load_lock():
    if config.SOURCES_LOCK.exists():
        return json.loads(config.SOURCES_LOCK.read_text(encoding="utf-8"))
    return {"sources": {}}


def _save_lock(lock):
    config.SOURCES_LOCK.write_text(
        json.dumps(lock, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_file(key: str, path, url: str, method: str):
    """Hash a file and record its provenance in sources.lock.json."""
    lock = _load_lock()
    lock["sources"][key] = {
        "url": url,
        "filename": path.name,
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "access_date": datetime.date.today().isoformat(),
        "method": method,
    }
    _save_lock(lock)
    return lock["sources"][key]


def fetch_or_detect(key: str, filename: str, url: str, min_bytes: int = 1000):
    """Try scripted download; else detect a manually provided file.

    Returns the local Path. Raises PipelineError if neither works.
    """
    target = config.RAW_DIR / filename
    lock = _load_lock()

    # Already acquired and hashed?
    if target.exists() and key in lock["sources"]:
        entry = lock["sources"][key]
        if entry.get("sha256") == _sha256(target):
            return target
        # file changed since recorded -> re-record below

    # Manually provided file present but not yet recorded?
    if target.exists() and target.stat().st_size >= min_bytes:
        record_file(key, target, url, method="manual")
        return target

    # Scripted attempt
    try:
        with httpx.Client(timeout=300, follow_redirects=True,
                          headers={"User-Agent": BROWSER_UA}) as c:
            with c.stream("GET", url) as r:
                if r.status_code == 200:
                    with open(target, "wb") as f:
                        for chunk in r.iter_bytes(1 << 20):
                            f.write(chunk)
                    if target.stat().st_size >= min_bytes:
                        record_file(key, target, url, method="script")
                        return target
                status = r.status_code
    except httpx.HTTPError as e:
        status = f"transport error: {e}"

    raise PipelineError(
        stage="download",
        expected=f"{filename} available via script or manually in data-pipeline/raw/",
        found=f"HTTP {status}; file not present locally",
        location=url,
        action=("Download the file in a normal browser (passes the bot "
                f"challenge) and save it as data-pipeline/raw/{filename}, "
                "then re-run."),
    )


def acquire_icio():
    return fetch_or_detect("icio_2016_2022_sml", ICIO_ZIP_NAME, ICIO_ZIP_URL,
                           min_bytes=10 << 20)


def acquire_tim(measure: str, countries: list[str], year: int):
    url = TIM_URL_TEMPLATE.format(measure=measure,
                                  countries="+".join(countries), year=year)
    return fetch_or_detect(f"tim_{measure.lower()}_{year}",
                           f"TIM_{measure}_{year}.csv", url)


def fetch_ilostat(indicator: str, ref_area: str, params: dict | None = None):
    """ILOSTAT bulk API (reachable via script, verified 2026-06-10).

    Caches per (indicator, ref_area) as CSV in raw/ and records provenance.
    """
    fname = f"ILOSTAT_{indicator}_{ref_area}.csv"
    target = config.RAW_DIR / fname
    q = {"id": indicator, "ref_area": ref_area, "format": ".csv"}
    if params:
        q.update(params)
    url = config.ILOSTAT_BASE + "?" + "&".join(f"{k}={v}" for k, v in q.items())

    if target.exists() and target.stat().st_size > 200:
        key = f"ilostat_{indicator.lower()}_{ref_area.lower()}"
        lock = _load_lock()
        if key not in lock["sources"]:
            record_file(key, target, url, method="script")
        return target

    try:
        with httpx.Client(timeout=120, follow_redirects=True,
                          headers={"User-Agent": BROWSER_UA}) as c:
            r = c.get(url)
            if r.status_code == 200 and len(r.content) > 200:
                target.write_bytes(r.content)
                record_file(f"ilostat_{indicator.lower()}_{ref_area.lower()}",
                            target, url, method="script")
                return target
            status = r.status_code
    except httpx.HTTPError as e:
        status = f"transport error: {e}"

    raise PipelineError(
        stage="download.ilostat",
        expected=f"{indicator} for {ref_area} from ILOSTAT",
        found=f"HTTP {status}",
        location=url,
        action="Check ILOSTAT availability; do not substitute values.",
    )
