"""
Quality checks — validates code style and documentation.
Checks for docstrings, type hints, and other best practices.
"""

import ast
import os
import pytest

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src")


def get_src_functions() -> list[ast.FunctionDef]:
    """Parse all .py files in src/ and return all function definitions."""
    functions = []
    for filename in os.listdir(SRC_DIR):
        if not filename.endswith(".py"):
            continue
        filepath = os.path.join(SRC_DIR, filename)
        with open(filepath, "r") as f:
            try:
                tree = ast.parse(f.read())
            except SyntaxError:
                continue
        functions.extend(
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        )
    return functions


class Quality:
    def test_functions_have_docstrings(self):
        functions = get_src_functions()
        if not functions:
            pytest.skip("No functions found in src/ yet")

        missing = [
            fn.name for fn in functions
            if not (fn.body and isinstance(fn.body[0], ast.Expr)
                    and isinstance(fn.body[0].value, ast.Constant))
        ]
        assert not missing, (
            f"These functions are missing docstrings: {', '.join(missing)}"
        )

    def test_functions_have_type_hints(self):
        functions = get_src_functions()
        if not functions:
            pytest.skip("No functions found in src/ yet")

        missing = [
            fn.name for fn in functions
            if fn.returns is None
        ]
        assert not missing, (
            f"These functions are missing return type hints: {', '.join(missing)}"
        )
