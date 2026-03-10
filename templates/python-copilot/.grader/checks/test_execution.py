"""
Execution checks — validates that the student's functions exist and return correct results.
Replace the examples below with the actual checks for your lab.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# ---------------------------------------------------------------------------
# Example: import the student's module
# Replace 'solution' with the actual module name defined in your lab.
# ---------------------------------------------------------------------------

# try:
#     from solution import add, multiply
# except ImportError:
#     pytest.skip("solution.py not found in src/", allow_module_level=True)


class Execution:
    """
    Add one test per function/requirement in your lab.
    Each test becomes one graded check in the PR comment.
    """

    def test_placeholder(self):
        """Remove this and add your real checks."""
        assert True, "Replace with actual execution checks for your lab"
