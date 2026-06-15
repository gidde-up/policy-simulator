"""Generates the engine regression fixture (Session E lock).

Captures the verbatim run_scenario output of the v1.0.0 engine for 35
cases (the 15 guided presets + a 20-case tariff battery) so the Session
E composable-shock refactor can be proven numerically inert
(tests/test_engine_regression_lock.py asserts equality at
rel=1e-6 / abs=1e-8).

Process discipline: this script REFUSES to run if engine.py has
uncommitted changes -- the fixture must come from the engine as last
committed. The fixture records the HEAD commit, the engine file's
sha256 and the numpy version as an audit trail of which engine
produced the numbers.
"""
import datetime
import hashlib
import importlib.util
import json
import subprocess
import sys

import numpy as np

import config

ENGINE_PATH = config.REPO_ROOT / "backend" / "app" / "models" / "engine.py"
FIXTURE_PATH = (config.PIPELINE_DIR / "tests" / "fixtures"
                / "engine_regression_v1.json")


def load_engine():
    spec = importlib.util.spec_from_file_location("engine", ENGINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_presets():
    path = config.REPO_ROOT / "backend" / "app" / "api" / "presets_data.py"
    spec = importlib.util.spec_from_file_location("presets_data", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PRESETS


def _load_to_engine_kwargs():
    """The shared API percent->fraction helper (loaded by file path; no
    FastAPI dependency), so the fixture exercises every lever exactly as
    the live /api/simulate route and the preset tests do."""
    path = config.REPO_ROOT / "backend" / "app" / "api" / "lever_params.py"
    spec = importlib.util.spec_from_file_location("lever_params", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.to_engine_kwargs


_TO_ENGINE_KWARGS = _load_to_engine_kwargs()


def preset_kwargs(preset):
    """Exactly how the API route and tests/test_presets.py build the call
    (covers every lever and the financing mode, not just v1.0 levers)."""
    kw = _TO_ENGINE_KWARGS(preset["params"])
    kw["iso3"] = preset["country_code"]
    return kw


def battery_cases():
    for iso3 in config.COUNTRIES:
        for retaliation in (False, True):
            for type_ii in (False, True):
                yield {
                    "case_id": (f"battery_{iso3}_mfg10"
                                f"_ret{int(retaliation)}_t2{int(type_ii)}"),
                    "kwargs": {
                        "iso3": iso3,
                        "tariffs": {"manufacturing": 0.10},
                        "include_retaliation": retaliation,
                        "include_type_ii": type_ii,
                    },
                }


def main():
    # the fixture must be generated from the committed engine
    dirty = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--",
         str(ENGINE_PATH)], cwd=config.REPO_ROOT).returncode != 0
    if dirty:
        print("REFUSED: backend/app/models/engine.py has uncommitted "
              "changes; the regression fixture must be generated from "
              "the committed v1.0.0 engine.")
        return 1

    head = subprocess.run(["git", "rev-parse", "HEAD"],
                          cwd=config.REPO_ROOT, capture_output=True,
                          text=True).stdout.strip()
    engine_sha = hashlib.sha256(ENGINE_PATH.read_bytes()).hexdigest()

    engine = load_engine()
    cases = []
    for preset in load_presets():
        cases.append({"case_id": f"preset_{preset['id']}",
                      "kwargs": preset_kwargs(preset)})
    cases.extend(battery_cases())

    for case in cases:
        kwargs = dict(case["kwargs"])
        iso3 = kwargs.pop("iso3")
        case["result"] = engine.run_scenario(iso3, **kwargs)
        case["kwargs"]["iso3"] = iso3

    fixture = {
        "description": "v1.2.0 engine regression lock: locks run_scenario "
                       "output (default tax_financed financing, corrected "
                       "Senegal elasticity, all levers via to_engine_kwargs) "
                       "at rel=1e-6 / abs=1e-8 to catch future drift",
        "generated": datetime.date.today().isoformat(),
        "head_commit": head,
        "engine_sha256": engine_sha,
        "numpy_version": np.__version__,
        "n_cases": len(cases),
        "cases": cases,
    }
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(
        json.dumps(fixture, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"written: {FIXTURE_PATH}")
    print(f"cases: {len(cases)}; engine sha256: {engine_sha[:16]}...; "
          f"HEAD: {head[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
