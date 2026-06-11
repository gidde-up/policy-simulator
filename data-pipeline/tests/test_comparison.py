"""Spec check 6: comparison table of new vs old multipliers.

Prints the table for the record and asserts the committed report matches
a recomputation (guards stale reports)."""
import numpy as np

import config
import make_comparison


def test_comparison_table_current(country_data, old_multipliers, capsys):
    # recompute and print
    for c, d in country_data.items():
        e = np.array(d["employment_coefficients"])
        m1 = e @ np.array(d["L_typeI"])
        m2 = e @ np.array(d["L_typeII"])
        old = old_multipliers[c]
        print(f"\n[{c}] sector: new direct/typeI/typeII vs old")
        for k, s in enumerate(config.SECTORS_14):
            o = old[s]
            print(f"  {s:18s} {e[k]:7.2f}/{m1[k]:7.2f}/{m2[k]:7.2f}  vs "
                  f"{o.direct:7.2f}/{o.type_1:7.2f}/{o.type_2:7.2f}")

    # committed report must match a fresh render
    report = config.REPORTS_DIR / "comparison_multipliers.md"
    assert report.exists(), "run make_comparison.py"
    before = report.read_text(encoding="utf-8")
    make_comparison.main()
    after = report.read_text(encoding="utf-8")
    assert before == after, ("committed comparison_multipliers.md is stale; "
                             "re-run make_comparison.py")
