"""Produces the external verifier's engine deliverable: the ZAF 10%
manufacturing tariff scenario with full channel decomposition, under
default parameters (retaliation off, financing drag n/a, Type I), plus
the retaliation-on variant.

Output: reports/engine_zaf_tariff10.json
"""
import importlib.util
import json

import config


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "engine",
        config.REPO_ROOT / "backend" / "app" / "models" / "engine.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    engine = load_engine()
    out = {
        "scenario": "ZAF, 10% tariff on manufacturing, default parameters",
        "engine_parameters": {
            e["id"]: e["value"]
            for e in json.loads(
                config.ASSUMPTIONS_JSON.read_text(encoding="utf-8")
            )["entries"]
            if e["country"] == "GLOBAL" or e["method"] == "authored_constant"
        },
        "retaliation_off": engine.run_scenario(
            "ZAF", tariffs={"manufacturing": 0.10}),
        "retaliation_on": engine.run_scenario(
            "ZAF", tariffs={"manufacturing": 0.10},
            include_retaliation=True),
        "type_ii_variant": engine.run_scenario(
            "ZAF", tariffs={"manufacturing": 0.10}, include_type_ii=True),
    }
    path = config.REPORTS_DIR / "engine_zaf_tariff10.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    net = out["retaliation_off"]["aggregate"]["total_jobs"]
    print(f"written: {path}")
    print(f"net (retaliation off): {net:,.0f} jobs")
    for name, ch in out["retaliation_off"]["tariff_channels"].items():
        if ch:
            print(f"  {name}: {ch['jobs']:,.0f} jobs")


if __name__ == "__main__":
    main()
