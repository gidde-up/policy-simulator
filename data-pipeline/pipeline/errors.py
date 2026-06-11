"""Uniform stop-and-report mechanism.

Ground rule 5: if required data is missing, stop and report; never
substitute a guessed value. Every hard gate in the pipeline raises
PipelineError; run_pipeline.py catches it, prints the structured block
and exits 1 without writing anything under backend/app/data/.
"""


class PipelineError(Exception):
    def __init__(self, stage: str, expected: str, found: str,
                 location: str = "", action: str = ""):
        self.stage = stage
        self.expected = expected
        self.found = found
        self.location = location
        self.action = action
        super().__init__(f"[{stage}] expected {expected}, found {found}")

    def report(self) -> str:
        lines = [
            "=" * 70,
            "PIPELINE STOP",
            f"  stage:    {self.stage}",
            f"  expected: {self.expected}",
            f"  found:    {self.found}",
        ]
        if self.location:
            lines.append(f"  location: {self.location}")
        if self.action:
            lines.append(f"  action:   {self.action}")
        lines.append("=" * 70)
        return "\n".join(lines)
