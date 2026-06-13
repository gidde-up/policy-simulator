"""One-off: locate per-country export demand elasticities in Tokarick
(2010) IMF WP/10/180. Confirms the concept (export DEMAND, not supply)
and which of ZAF/TUN/VNM/THA/SEN appear, before any registration."""
import re
import sys

from pypdf import PdfReader

import config

PATH = config.RAW_DIR / "wp10180.pdf"
WANT = {"South Africa", "Tunisia", "Viet Nam", "Vietnam", "Thailand",
        "Senegal"}


def main():
    reader = PdfReader(str(PATH))
    print(f"pages: {len(reader.pages)}")

    # 1) find where export demand elasticities are defined/tabulated
    for pno, page in enumerate(reader.pages):
        t = " ".join((page.extract_text() or "").split())
        low = t.lower()
        if "export demand" in low and "elasticit" in low:
            for m in re.finditer(r"export demand elasticit\w*", low):
                lo = max(0, m.start() - 120)
                print(f"  p{pno + 1}: ...{t[lo:m.end() + 180]}...")
            break

    # 2) country rows: print any line mentioning a target country with numbers
    print("\n--- country rows ---")
    for pno, page in enumerate(reader.pages):
        for line in (page.extract_text() or "").splitlines():
            s = " ".join(line.split())
            if any(w in s for w in WANT) and re.search(r"-?\d+\.\d", s):
                print(f"  p{pno + 1}: {s[:200]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
