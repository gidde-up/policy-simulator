"""Appends the per-country `informality` block to the verified country
JSONs and registers inherited cells in the assumptions registry.

SAFETY: the verified numbers must not move. Before touching a file the
script asserts that parse -> re-dump (with the exact dump settings of
pipeline/build.py) reproduces the committed bytes; after insertion it
asserts every pre-existing key is structurally unchanged. Any failure
is a hard stop. The engine regression fixture independently proves
run_scenario output is unchanged.

Idempotent: re-running replaces the informality block and the
country's informality-scope registry entries.
"""
import datetime
import json
import sys

import config
from pipeline import assumptions, informality

DUMP = dict(indent=1, ensure_ascii=False)


def main():
    registry = assumptions.load_registry()
    today = datetime.date.today().isoformat()

    for iso3 in config.COUNTRIES:
        path = config.OUTPUT_DIR / f"{iso3}.json"
        original_text = path.read_text(encoding="utf-8")
        data = json.loads(original_text)

        # byte-identity gate (ignoring a previously added informality
        # block, so the script is idempotent)
        baseline = {k: v for k, v in data.items() if k != "informality"}
        had_block = "informality" in data
        if not had_block:
            redump = json.dumps(data, **DUMP) + "\n"
            assert redump == original_text, (
                f"{iso3}: parse->re-dump does not reproduce the committed "
                "bytes; HARD STOP (would risk perturbing verified data)")

        block, cells = informality.build_country_informality(iso3)
        if block is None:
            print(f"{iso3}: no sector-level informality data -> block "
                  "omitted (outputs hidden for this country)")
            assumptions.replace_scope_entries(registry, iso3,
                                              "informality", [])
            continue

        block["context"] = informality.national_context(iso3)

        entries = []
        for n, (sector, share, basis) in enumerate(cells, start=1):
            entries.append(assumptions.make_entry(
                entry_id=f"{iso3}-informality-{sector}",
                country=iso3, scope="informality", sector=sector,
                field="informal_share_of_employment",
                icio_codes=[], value=share, unit="share",
                method="share_inheritance", basis=basis,
                source={"dataset": f"ILOSTAT {block['indicator']} / "
                                   f"{block['denominator_indicator']}",
                        "url": config.ILOSTAT_BASE,
                        "accessed": today,
                        "reference_period": str(block["year_used"])}))
        assumptions.replace_scope_entries(registry, iso3, "informality",
                                          entries)
        block["provenance"] = [e["id"] for e in entries]

        new_data = dict(baseline)
        new_data["informality"] = block
        new_text = json.dumps(new_data, **DUMP) + "\n"

        # post-insertion structural identity of all pre-existing keys
        reread = json.loads(new_text)
        for k, v in baseline.items():
            assert reread[k] == v, f"{iso3}: key '{k}' changed; HARD STOP"

        path.write_text(new_text, encoding="utf-8")
        shares = block["informal_share_of_employment"]
        known = {k: v for k, v in shares.items() if v is not None}
        print(f"{iso3}: informality block written "
              f"({block['classification']}, year {block['year_used']}, "
              f"{len(known)}/14 sectors, {len(entries)} inherited cells "
              f"registered)")

    assumptions.write_registry(registry)
    print("registry updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
