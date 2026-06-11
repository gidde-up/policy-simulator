"""Concordance from native ICIO industries to the 14 didactic sectors.

The mapping itself is human-authored (a classification judgement, not an
invented number) and committed as concordance_icio_to_14.csv with a
rationale per row. This module only validates it against the discovered
industry list and builds the aggregation matrix. Validation failures stop
the pipeline; the mapping is never auto-completed.
"""
import csv

import numpy as np

import config
from pipeline.errors import PipelineError


def load_concordance() -> dict[str, str]:
    """Returns {icio_code: sector_14}; validates the CSV in isolation."""
    if not config.CONCORDANCE_CSV.exists():
        raise PipelineError(
            stage="concordance.load",
            expected=f"{config.CONCORDANCE_CSV.name} present",
            found="file missing",
            location=str(config.CONCORDANCE_CSV),
            action="Author the concordance from the --inspect industry list.",
        )
    mapping = {}
    with open(config.CONCORDANCE_CSV, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required = {"icio_code", "description", "sector_14", "rationale"}
        if set(reader.fieldnames or []) < required:
            raise PipelineError(
                stage="concordance.load",
                expected=f"columns {sorted(required)}",
                found=f"{reader.fieldnames}",
                action="Fix the concordance CSV header.",
            )
        for i, row in enumerate(reader, start=2):
            code = row["icio_code"].strip()
            sector = row["sector_14"].strip()
            if not code:
                continue
            if code in mapping:
                raise PipelineError(
                    stage="concordance.load",
                    expected="each ICIO code exactly once",
                    found=f"duplicate '{code}' (line {i})",
                    action="Remove the duplicate row.",
                )
            if sector not in config.SECTORS_14:
                raise PipelineError(
                    stage="concordance.load",
                    expected=f"sector_14 in {config.SECTORS_14}",
                    found=f"'{sector}' for '{code}' (line {i})",
                    action="Fix the sector name.",
                )
            mapping[code] = sector
    return mapping


def validate_against(mapping: dict[str, str], industries: list[str]):
    """The concordance must enumerate the discovered list exactly."""
    unmapped = [i for i in industries if i not in mapping]
    extra = [c for c in mapping if c not in industries]
    if unmapped or extra:
        raise PipelineError(
            stage="concordance.validate",
            expected="concordance == discovered ICIO industry list, 1:1",
            found=f"unmapped in CSV: {unmapped}; in CSV but not in file: {extra}",
            action="Edit concordance_icio_to_14.csv; every code exactly once.",
        )
    used = {s for s in mapping.values()}
    missing_sectors = [s for s in config.SECTORS_14 if s not in used]
    if missing_sectors:
        raise PipelineError(
            stage="concordance.validate",
            expected="every one of the 14 sectors receives at least one industry",
            found=f"empty sectors: {missing_sectors}",
            action="Review the mapping.",
        )


def aggregator(mapping: dict[str, str], industries: list[str]) -> np.ndarray:
    """S (14 x n): S[k, i] = 1 if native industry i maps to sector k."""
    S = np.zeros((len(config.SECTORS_14), len(industries)))
    for i, code in enumerate(industries):
        S[config.SECTORS_14.index(mapping[code]), i] = 1.0
    return S


def sector_composition() -> dict[str, list[dict]]:
    """{sector: [{code, description}]} for JSON metadata / UI tooltips."""
    comp: dict[str, list[dict]] = {s: [] for s in config.SECTORS_14}
    with open(config.CONCORDANCE_CSV, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            code = row["icio_code"].strip()
            if not code:
                continue
            comp[row["sector_14"].strip()].append(
                {"code": code, "description": row["description"].strip()})
    return comp


def describe(mapping: dict[str, str]) -> str:
    lines = []
    for sector in config.SECTORS_14:
        codes = sorted(c for c, s in mapping.items() if s == sector)
        lines.append(f"{sector:18s} <- {', '.join(codes)}")
    return "\n".join(lines)
