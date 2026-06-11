"""CLI entry point.

  python run_pipeline.py --inspect          structure discovery only
  python run_pipeline.py ZAF TUN            build country JSONs
"""
import argparse
import sys

import config
from pipeline import build, download, icio_parse
from pipeline.errors import PipelineError


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("countries", nargs="*", help="ISO3 codes, e.g. ZAF TUN")
    ap.add_argument("--inspect", action="store_true",
                    help="print discovered ICIO structure and exit")
    args = ap.parse_args()

    try:
        zip_path = download.acquire_icio()
        struct = icio_parse.read_structure(zip_path, config.REFERENCE_YEAR)

        if args.inspect:
            print(struct.describe())
            present = [c for c in config.COUNTRIES if c in struct.countries]
            absent = [c for c in config.COUNTRIES if c not in struct.countries]
            print(f"\ntarget countries present: {present}")
            if absent:
                print(f"target countries ABSENT:  {absent}")
            return 0

        if not args.countries:
            ap.error("give ISO3 codes or --inspect")

        for c in args.countries:
            if c not in config.COUNTRIES:
                ap.error(f"unknown country {c}; configured: {config.COUNTRIES}")
            print(f"=== building {c} ===")
            data, results = build.build_country(c, struct=struct)
            for name, passed, details in results:
                print(f"  {'PASS' if passed else 'FAIL'} {name}: {details}")
            print(f"  -> backend/app/data/countries/{c}.json written")
        return 0

    except PipelineError as e:
        print(e.report())
        return 1


if __name__ == "__main__":
    sys.exit(main())
