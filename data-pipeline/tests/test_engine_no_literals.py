"""Ground rule 1 enforcement: engine.py must not contain numeric
literals beyond structural constants ({0, 1, 2}). Every behavioural
number must come from the assumptions registry; every unit conversion
lives in the API layer."""
import ast

import config

WHITELIST = {0, 1, 2}


def test_engine_has_no_numeric_literals():
    path = config.REPO_ROOT / "backend" / "app" / "models" / "engine.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(
                node.value, (int, float)) and not isinstance(
                node.value, bool):
            if node.value not in WHITELIST:
                offenders.append((node.lineno, node.value))
    assert not offenders, (
        f"numeric literals outside whitelist {sorted(WHITELIST)} in "
        f"engine.py (line, value): {offenders} -- move parameters to "
        "assumptions.json and unit conversions to the API layer")
