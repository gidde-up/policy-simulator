"""Comparison of new pipeline-derived employment multipliers vs the old
hardcoded values in backend/app/data/tiva_multipliers.py -- "for the
record" (Phase 1 spec, validation item). The old module is loaded by file
path (it imports only stdlib); it is NOT modified this session.

  new direct   = e_j                    (jobs per USD million output)
  new Type I   = sum_i e_i L_I[i, j]    (jobs per USD million final demand)
  new Type II  = sum_i e_i L_II[i, j]
"""
import importlib.util
import json

import numpy as np

import config


def load_old_multipliers():
    spec = importlib.util.spec_from_file_location(
        "tiva_multipliers", config.OLD_MULTIPLIERS_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {
        "ZAF": mod.SOUTH_AFRICA_TIVA,
        "TUN": mod.TUNISIA_STYLIZED,
    }


def main():
    old_all = load_old_multipliers()
    lines = [
        "# Employment multipliers: new (OECD ICIO 2025 pipeline) vs old "
        "(hardcoded, removed in Phase 2)",
        "",
        "Old values were typed into source code and labelled 'OECD "
        "TiVA/ICIO 2023' (ZAF) or 'stylized' (TUN); the audit found no "
        "code deriving them from any dataset. New values are computed by "
        "this pipeline from OECD ICIO 2025 (year 2022, current USD) with "
        "employment from OECD TiM 2025/ILOSTAT. Old values claim "
        "reference year 2020; level differences therefore combine "
        "methodology and price-year effects.",
        "",
    ]
    for country in ["ZAF", "TUN"]:
        path = config.OUTPUT_DIR / f"{country}.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        e = np.array(d["employment_coefficients"])
        m1 = e @ np.array(d["L_typeI"])
        m2 = e @ np.array(d["L_typeII"])
        old = old_all[country]

        lines += [
            f"## {config.COUNTRY_NAMES[country]} ({country})",
            "",
            "| sector | new direct | old direct | new Type I | old Type I "
            "| new Type II | old Type II |",
            "|---|---|---|---|---|---|---|",
        ]
        for k, s in enumerate(config.SECTORS_14):
            o = old[s]
            lines.append(
                f"| {s} | {e[k]:.2f} | {o.direct:.2f} | {m1[k]:.2f} | "
                f"{o.type_1:.2f} | {m2[k]:.2f} | {o.type_2:.2f} |")
        lines.append("")

    out = config.REPORTS_DIR / "comparison_multipliers.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
