"""
Structure checks — validates that the student created the expected files.
These run first and block execution checks if the structure is wrong.
"""

import os
import pytest

SRC_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "src")


class Structure:
    def test_src_directory_exists(self):
        assert os.path.isdir(SRC_DIR), "src/ directory is missing"

    def test_src_has_python_files(self):
        py_files = [f for f in os.listdir(SRC_DIR) if f.endswith(".py")]
        assert len(py_files) > 0, "No .py files found in src/ — add your solution files there"
