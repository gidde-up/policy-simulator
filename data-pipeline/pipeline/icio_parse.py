"""ICIO file parsing: structure discovery and per-country block extraction.

Nothing about the file layout is hardcoded beyond documented conventions;
countries, industries, final-demand categories and special rows are
discovered from the file itself. Any label that cannot be classified
stops the pipeline (ground rule 5).

Layout conventions (OECD ICIO CSV, verified at runtime):
  - first column: row labels "COU_IND" (e.g. "ZAF_01T02") for
    country-industry rows, plus special bottom rows (taxes, value added,
    output);
  - columns: "COU_IND" intermediate-use columns, "COU_FD" final-demand
    columns (HFCE, NPISH, GGFC, GFCF, INVNT, ...), and a total output
    column ("OUT"/"TOTAL").

Key economics of the extraction (per country c, native industry detail):
  Z_dd  domestic intermediate block: rows c, industry columns of c
  M     imported intermediates: non-c industry rows into c's industry
        columns, summed over partner countries, by supplying industry (n x n)
  F_dom domestic final demand: rows c into c's FD columns (n x nFD)
  F_imp imported final demand: non-c rows into c's FD columns, summed
        over partners by supplying industry (n x nFD)
  x     gross output of c's industries (OUT column at c's rows)
  va, tls  value added and taxes-less-subsidies rows at c's columns
  exports_i = x_i - sum_j Z_dd[i,j] - sum_fd F_dom[i,fd]   (residual:
        everything not used domestically is used abroad)
"""
import zipfile

import numpy as np
import pandas as pd

import config
from pipeline.errors import PipelineError

# Final-demand category codes accepted (OECD ICIO conventions).
# Anything else in a column suffix that is not an industry stops the run.
KNOWN_FD = ["HFCE", "NPISH", "GGFC", "GFCF", "INVNT", "NONRES", "DPABR", "FD"]

# Special (non country_industry) row labels accepted.
KNOWN_SPECIAL_ROWS = {"TLS", "VA", "VALU", "OUT", "OUTPUT", "TOTAL"}


def find_year_csv(zip_path, year: int) -> str:
    """Locate the CSV for the reference year inside the ICIO zip."""
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
    candidates = [n for n in names
                  if str(year) in n and n.lower().endswith(".csv")]
    if len(candidates) != 1:
        raise PipelineError(
            stage="icio_parse.find_year_csv",
            expected=f"exactly one CSV for {year} in {zip_path.name}",
            found=f"{candidates or names}",
            location=str(zip_path),
            action="Inspect the archive; adjust year or bundle.",
        )
    return candidates[0]


class IcioStructure:
    """Discovered structure of one ICIO CSV."""

    def __init__(self, columns, row_labels):
        self.label_col = columns[0]
        data_cols = list(columns[1:])

        # classify columns
        self.out_col = None
        col_country, col_kind, col_code = {}, {}, {}
        countries = set()
        fd_seen = set()
        industries_seen = set()

        # first pass: split prefix_suffix; suffix in KNOWN_FD -> FD col
        for col in data_cols:
            if col in ("OUT", "OUTPUT", "TOTAL"):
                self.out_col = col
                continue
            if "_" not in col:
                raise PipelineError(
                    stage="icio_parse.structure",
                    expected="columns 'COU_IND', 'COU_FD' or OUT/TOTAL",
                    found=f"unclassifiable column '{col}'",
                    action="Inspect the file; update parser conventions deliberately.",
                )
            prefix, suffix = col.split("_", 1)
            col_country[col] = prefix
            countries.add(prefix)
            if suffix in KNOWN_FD:
                col_kind[col] = "fd"
                col_code[col] = suffix
                fd_seen.add(suffix)
            else:
                col_kind[col] = "ind"
                col_code[col] = suffix
                industries_seen.add(suffix)

        self.col_country = col_country
        self.col_kind = col_kind
        self.col_code = col_code
        self.countries = sorted(countries)
        self.fd_categories = [f for f in KNOWN_FD if f in fd_seen]
        self.industries = sorted(industries_seen)

        # classify rows
        self.special_rows = []
        row_country, row_code = {}, {}
        row_industries = set()
        for lab in row_labels:
            if "_" not in lab:
                if lab in KNOWN_SPECIAL_ROWS:
                    self.special_rows.append(lab)
                    continue
                raise PipelineError(
                    stage="icio_parse.structure",
                    expected=f"special rows in {sorted(KNOWN_SPECIAL_ROWS)}",
                    found=f"unclassifiable row '{lab}'",
                    action="Inspect the file; update parser conventions deliberately.",
                )
            prefix, suffix = lab.split("_", 1)
            if prefix not in countries:
                # e.g. "TLS_..." or unexpected scheme
                if prefix in KNOWN_SPECIAL_ROWS:
                    self.special_rows.append(lab)
                    continue
                raise PipelineError(
                    stage="icio_parse.structure",
                    expected="row prefixes matching discovered country codes",
                    found=f"row '{lab}' with unknown prefix '{prefix}'",
                    action="Inspect the file; update parser conventions deliberately.",
                )
            row_country[lab] = prefix
            row_code[lab] = suffix
            row_industries.add(suffix)
        self.row_country = row_country
        self.row_code = row_code

        # row industries must equal column industries
        if row_industries != industries_seen:
            raise PipelineError(
                stage="icio_parse.structure",
                expected="identical industry lists on rows and columns",
                found=(f"row-only: {sorted(row_industries - industries_seen)}; "
                       f"col-only: {sorted(industries_seen - row_industries)}"),
                action="Inspect the file format.",
            )

        if self.out_col is None:
            raise PipelineError(
                stage="icio_parse.structure",
                expected="a total output column (OUT/OUTPUT/TOTAL)",
                found="none",
                action="Inspect the file format.",
            )

        # identify the VA / TLS / OUT special rows
        def pick(*names):
            for n in names:
                if n in self.special_rows:
                    return n
            return None
        self.va_row = pick("VA", "VALU")
        self.tls_row = pick("TLS")
        self.out_row = pick("OUT", "OUTPUT", "TOTAL")
        missing = [n for n, v in
                   [("VA", self.va_row), ("TLS", self.tls_row),
                    ("OUT", self.out_row)] if v is None]
        if missing:
            raise PipelineError(
                stage="icio_parse.structure",
                expected="special rows for TLS, VA and OUT",
                found=f"missing {missing}; present: {self.special_rows}",
                action="Inspect the file format.",
            )

    def describe(self) -> str:
        lines = [
            f"countries ({len(self.countries)}): {', '.join(self.countries)}",
            "",
            f"industries ({len(self.industries)}): {', '.join(self.industries)}",
            "",
            f"final demand categories: {', '.join(self.fd_categories)}",
            f"special rows: {', '.join(self.special_rows)}",
            f"output column: {self.out_col}",
        ]
        return "\n".join(lines)


def read_structure(zip_path, year: int) -> IcioStructure:
    """Read only the header and the row-label column (cheap)."""
    csv_name = find_year_csv(zip_path, year)
    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_name) as f:
            header = pd.read_csv(f, nrows=0)
        with z.open(csv_name) as f:
            labels = pd.read_csv(f, usecols=[0], dtype=str).iloc[:, 0].tolist()
    return IcioStructure(list(header.columns), labels)


def extract_country_blocks(zip_path, year: int, struct: IcioStructure,
                           targets: list[str]) -> dict:
    """One streaming pass over the CSV; returns per-country native blocks.

    Loads only the columns belonging to target countries plus the OUT
    column (memory: ~#rows x (#targets x ~50 + 1) floats).
    """
    missing = [t for t in targets if t not in struct.countries]
    if missing:
        raise PipelineError(
            stage="icio_parse.extract",
            expected=f"target countries {targets} present in ICIO",
            found=f"missing: {missing}",
            location=str(zip_path),
            action="Country not in ICIO 2025; do not substitute.",
        )

    csv_name = find_year_csv(zip_path, year)
    needed_cols = [struct.label_col]
    for col in struct.col_country:
        if struct.col_country[col] in targets:
            needed_cols.append(col)
    needed_cols.append(struct.out_col)

    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_name) as f:
            df = pd.read_csv(f, usecols=needed_cols)
    df = df.set_index(struct.label_col)

    n_native = len(struct.industries)
    ind_pos = {code: i for i, code in enumerate(struct.industries)}

    # industry rows grouped: domestic per target; foreign aggregated by industry
    out = {}
    industry_rows = [lab for lab in df.index if lab in struct.row_country]

    # precompute row metadata aligned with df
    row_cou = np.array([struct.row_country.get(lab, "") for lab in df.index])
    row_ind = np.array([ind_pos.get(struct.row_code.get(lab, ""), -1)
                        for lab in df.index])

    for c in targets:
        ind_cols = [col for col in df.columns
                    if struct.col_kind.get(col) == "ind"
                    and struct.col_country[col] == c]
        fd_cols = [col for col in df.columns
                   if struct.col_kind.get(col) == "fd"
                   and struct.col_country[col] == c]
        # order columns by industry code order / FD order
        ind_cols.sort(key=lambda col: ind_pos[struct.col_code[col]])
        fd_order = [f for f in struct.fd_categories]
        fd_cols.sort(key=lambda col: fd_order.index(struct.col_code[col]))
        fd_codes = [struct.col_code[col] for col in fd_cols]

        dom_mask = row_cou == c
        for_mask = (row_cou != c) & (row_ind >= 0)

        Zc = df.loc[:, ind_cols].to_numpy(dtype=np.float64)
        Fc = df.loc[:, fd_cols].to_numpy(dtype=np.float64)

        # domestic rows ordered by industry
        dom_idx = np.where(dom_mask)[0]
        dom_order = dom_idx[np.argsort(row_ind[dom_idx])]
        if len(dom_order) != n_native:
            raise PipelineError(
                stage="icio_parse.extract",
                expected=f"{n_native} domestic industry rows for {c}",
                found=f"{len(dom_order)}",
                action="Industry coverage differs by country; inspect file.",
            )
        Z_dd = Zc[dom_order, :]
        F_dom = Fc[dom_order, :]
        x = df[struct.out_col].to_numpy(dtype=np.float64)[dom_order]

        # foreign rows aggregated by supplying industry
        M = np.zeros((n_native, len(ind_cols)))
        F_imp = np.zeros((n_native, len(fd_cols)))
        fi = np.where(for_mask)[0]
        np.add.at(M, row_ind[fi], Zc[fi, :])
        np.add.at(F_imp, row_ind[fi], Fc[fi, :])

        # special rows at c's columns
        def special(row_label):
            return df.loc[row_label, ind_cols].to_numpy(dtype=np.float64)
        va = special(struct.va_row)
        tls = special(struct.tls_row)
        out_row = special(struct.out_row)

        out[c] = {
            "industries": list(struct.industries),
            "fd_categories": fd_codes,
            "Z_dd": Z_dd,
            "M": M,
            "F_dom": F_dom,
            "F_imp": F_imp,
            "x": x,
            "va": va,
            "tls": tls,
            "out_row": out_row,
        }

    # free the big frame before returning
    del df
    return out


def cache_blocks(blocks: dict, year: int):
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for c, b in blocks.items():
        np.savez_compressed(
            config.CACHE_DIR / f"{c}_{year}.npz",
            industries=np.array(b["industries"]),
            fd_categories=np.array(b["fd_categories"]),
            Z_dd=b["Z_dd"], M=b["M"], F_dom=b["F_dom"], F_imp=b["F_imp"],
            x=b["x"], va=b["va"], tls=b["tls"], out_row=b["out_row"],
        )


def load_cached_blocks(country: str, year: int) -> dict | None:
    p = config.CACHE_DIR / f"{country}_{year}.npz"
    if not p.exists():
        return None
    z = np.load(p, allow_pickle=False)
    return {
        "industries": [str(s) for s in z["industries"]],
        "fd_categories": [str(s) for s in z["fd_categories"]],
        "Z_dd": z["Z_dd"], "M": z["M"], "F_dom": z["F_dom"],
        "F_imp": z["F_imp"], "x": z["x"], "va": z["va"], "tls": z["tls"],
        "out_row": z["out_row"],
    }
