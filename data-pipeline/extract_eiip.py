"""One-off: pull the labour-content statements from the ILO EIIP PDFs in
raw/, so the registered GLOBAL-eiip-labour-cost-share-* values can be
transcribed from the actual documents (not this prompt)."""
import re
import sys

from pypdf import PdfReader

import config

PDFS = ["eiip_green_works_wcms_619821.pdf", "eiip_guidance_wcms_743537.pdf"]


def main():
    for name in PDFS:
        path = config.RAW_DIR / name
        if not path.exists():
            print(f"MISSING: {name}")
            continue
        print(f"\n===== {name} =====")
        reader = PdfReader(str(path))
        for pno, page in enumerate(reader.pages):
            text = " ".join((page.extract_text() or "").split())
            for m in re.finditer(r"labour content", text, re.IGNORECASE):
                lo = max(0, m.start() - 60)
                hi = min(len(text), m.end() + 320)
                print(f"  p{pno + 1}: ...{text[lo:hi]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
