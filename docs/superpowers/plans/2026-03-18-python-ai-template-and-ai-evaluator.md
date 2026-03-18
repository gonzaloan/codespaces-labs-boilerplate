# python-ai Template + AI Evaluator — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `python-ai` boilerplate template (Python 3.12 + pytest) with a built-in AI evaluator that posts qualitative coaching feedback on every student PR via GitHub Actions.

**Architecture:** A new `templates/python-ai/` directory follows the same grading pattern as the existing `playwright` template. `ai_evaluator.py` is a standalone script that reads a lab-specific `SPEC.md` rubric and a student artifact, calls Claude Haiku via Portkey, and writes `ai-feedback.json`. `summarize.py` merges automated pytest results and AI feedback into a single unified PR comment.

**Tech Stack:** Python 3.12, pytest + pytest-json-report, portkey-ai, python-frontmatter, GitHub Actions (marocchino/sticky-pull-request-comment@v2)

**Spec:** `docs/superpowers/specs/2026-03-18-python-ai-template-and-ai-evaluator-design.md`

---

## File Map

### New files — template

| File | Responsibility |
|---|---|
| `templates/python-ai/.devcontainer/devcontainer.json` | Python 3.12 + Copilot extension for Codespaces |
| `templates/python-ai/.github/workflows/grade.yml` | Full CI pipeline: install → pytest → ai_evaluator → summarize → PR comment → artifacts |
| `templates/python-ai/.grader/summarize.py` | Parses pytest-json-report output + ai-feedback.json → grader-report.md + grader-results.json |
| `templates/python-ai/.grader/ai_evaluator.py` | Reads SPEC.md + artifact → calls Portkey → writes ai-feedback.json |
| `templates/python-ai/.grader/SPEC.md` | Rubric template with YAML frontmatter; instructor customizes per lab |
| `templates/python-ai/.grader/checks/test_structure.py` | Placeholder Structure checks |
| `templates/python-ai/.grader/checks/test_execution.py` | Placeholder Execution checks |
| `templates/python-ai/.grader/checks/test_quality.py` | Placeholder Quality checks |
| `templates/python-ai/src/.gitkeep` | Starter code placeholder |
| `templates/python-ai/docs/instructions.md` | Exercise instructions template |
| `templates/python-ai/requirements.txt` | pytest, pytest-asyncio, pytest-json-report, portkey-ai, python-frontmatter |
| `templates/python-ai/pytest.ini` | asyncio_mode = auto, testpaths = .grader/checks |
| `templates/python-ai/README.md` | Lab README |

### New files — boilerplate tests

| File | Responsibility |
|---|---|
| `tests/conftest.py` | Adds `.grader/` to sys.path for imports |
| `tests/test_summarize.py` | Unit tests for summarize.py helper functions |
| `tests/test_ai_evaluator.py` | Unit tests for ai_evaluator.py (mocks Portkey) |

### Modified files — docs

| File | Change |
|---|---|
| `docs/template-differences.md` | Add `python-ai` row with Python version override note |
| `docs/how-to-create-a-lab.md` | Add step: configure SPEC.md for AI evaluation |
| `docs/grader-guide.md` | Add section: writing AI-evaluable specs (SPEC.md schema) |

---

## Task 1: Template Skeleton (Static Files)

**Files:**
- Create: `templates/python-ai/.devcontainer/devcontainer.json`
- Create: `templates/python-ai/requirements.txt`
- Create: `templates/python-ai/pytest.ini`
- Create: `templates/python-ai/README.md`
- Create: `templates/python-ai/docs/instructions.md`
- Create: `templates/python-ai/src/.gitkeep`
- Create: `templates/python-ai/.grader/checks/test_structure.py`
- Create: `templates/python-ai/.grader/checks/test_execution.py`
- Create: `templates/python-ai/.grader/checks/test_quality.py`
- Create: `templates/python-ai/.grader/SPEC.md`

- [ ] **Step 1: Create .devcontainer/devcontainer.json**

```json
{
  "name": "Python AI Lab",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "postCreateCommand": "pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": ["GitHub.copilot", "ms-python.python"]
    }
  }
}
```

- [ ] **Step 2: Create requirements.txt**

```
pytest>=8,<9
pytest-asyncio>=0.23,<0.24
pytest-json-report>=1.5,<2
portkey-ai>=1,<2
python-frontmatter>=1,<2
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
# testpaths is not set here — grade.yml passes the path explicitly:
#   pytest .grader/checks/ --json-report ...
# Running pytest from repo root without arguments will not collect checks by design.
```

- [ ] **Step 4: Create placeholder check files**

`templates/python-ai/.grader/checks/test_structure.py`:
```python
# Structure checks — replace with lab-specific tests
# Class name must match a key in CATEGORY_POINTS in summarize.py
class Structure:
    def test_placeholder(self):
        assert True, "Replace this placeholder with real structure checks"
```

Same pattern for `test_execution.py` (class `Execution`) and `test_quality.py` (class `Quality`).

- [ ] **Step 5: Create SPEC.md template**

`templates/python-ai/.grader/SPEC.md`:
```markdown
---
artifact: docs/REFLECTION.md
artifact_type: markdown
max_score: 20
---

# AI Evaluation Rubric

Replace the frontmatter above with the path and type of the artifact to evaluate.
Replace the criteria below with lab-specific rubric items.

## Understanding (max: 10)
Describe what a passing response must include for this criterion.

## Reflection (max: 10)
Describe what a passing response must include for this criterion.
```

- [ ] **Step 6: Create docs/instructions.md**

```markdown
# Lab Instructions

TODO: Replace this file with the lab exercise description.
```

- [ ] **Step 7: Create src/.gitkeep and README.md**

`src/.gitkeep`: empty file.

`README.md`:
```markdown
# Lab Name

Brief description of the lab.

## Getting Started

1. Read `docs/instructions.md` for the exercise description.
2. Open this repo in GitHub Codespaces.
3. Complete the tasks described in the instructions.
4. Submit your work by opening a Pull Request against `main`.

## Grading

A grader runs automatically on every Pull Request and posts a score comment.
```

- [ ] **Step 8: Commit skeleton**

```bash
git -C "templates/python-ai" init  # not needed if working in boilerplate
cd codespaces-lab-boilerplate
git add templates/python-ai/
git commit -m "feat: add python-ai template skeleton"
```

---

## Task 2: summarize.py — Automated Grading Report

**Files:**
- Create: `templates/python-ai/.grader/summarize.py`
- Create: `tests/conftest.py`
- Create: `tests/test_summarize.py`

This task implements `summarize.py` for the automated pytest score only (no AI section yet — added in Task 5).

### pytest-json-report output format (reference)

```json
{
  "duration": 1.2,
  "tests": [
    {
      "nodeid": ".grader/checks/test_structure.py::Structure::test_file_exists",
      "outcome": "passed",
      "call": {"duration": 0.001, "outcome": "passed"}
    },
    {
      "nodeid": ".grader/checks/test_execution.py::Execution::test_output_correct",
      "outcome": "failed",
      "call": {"duration": 0.001, "outcome": "failed", "longrepr": "AssertionError: output should be 42\nassert 0 == 42"}
    }
  ]
}
```

Category = class name in nodeid (`Structure`, `Execution`, `Quality`).
Check name = method name after `test_`, underscores → spaces, capitalized.

- [ ] **Step 1: Create tests/conftest.py**

```python
import sys
from pathlib import Path

# Make .grader/ importable in boilerplate tests
sys.path.insert(0, str(Path(__file__).parent.parent / "templates" / "python-ai" / ".grader"))
```

- [ ] **Step 2: Write failing tests for parse_pytest_results()**

`tests/test_summarize.py`:
```python
from summarize import parse_pytest_results, progress_bar, render_ai_section

SAMPLE_RAW = {
    "duration": 0.5,
    "tests": [
        {
            "nodeid": ".grader/checks/test_structure.py::Structure::test_file_exists",
            "outcome": "passed",
            "call": {"duration": 0.001, "outcome": "passed"},
        },
        {
            "nodeid": ".grader/checks/test_execution.py::Execution::test_output_correct",
            "outcome": "failed",
            "call": {
                "duration": 0.001,
                "outcome": "failed",
                "longrepr": "AssertionError: output should be 42\nassert 0 == 42",
            },
        },
    ],
}


def test_parse_extracts_categories():
    cats = parse_pytest_results(SAMPLE_RAW)
    names = [c["name"] for c in cats]
    assert "Structure" in names
    assert "Execution" in names


def test_parse_passed_check():
    cats = parse_pytest_results(SAMPLE_RAW)
    structure = next(c for c in cats if c["name"] == "Structure")
    assert structure["score"] == 1
    assert structure["total"] == 1
    assert structure["checks"][0]["passed"] is True
    assert structure["checks"][0]["hint"] is None


def test_parse_failed_check_has_hint():
    cats = parse_pytest_results(SAMPLE_RAW)
    execution = next(c for c in cats if c["name"] == "Execution")
    assert execution["score"] == 0
    check = execution["checks"][0]
    assert check["passed"] is False
    assert "output should be 42" in check["hint"]


def test_parse_check_name_formatted():
    cats = parse_pytest_results(SAMPLE_RAW)
    execution = next(c for c in cats if c["name"] == "Execution")
    # "test_output_correct" → "Output correct"
    assert execution["checks"][0]["name"] == "Output correct"


def test_progress_bar_full():
    assert "██████████" in progress_bar(10, 10)


def test_progress_bar_empty():
    assert "░░░░░░░░░░" in progress_bar(0, 10)


def test_progress_bar_half():
    bar = progress_bar(5, 10)
    assert "█████░░░░░" in bar
```

- [ ] **Step 3: Run tests — verify they FAIL**

```bash
cd codespaces-lab-boilerplate
pip install pytest
pytest tests/test_summarize.py -v
```
Expected: `ImportError: No module named 'summarize'`

- [ ] **Step 4: Implement summarize.py (parse + render helpers only)**

`templates/python-ai/.grader/summarize.py`:
```python
"""
Reads grader-results-raw.json (pytest-json-report format)
Reads ai-feedback.json (from ai_evaluator.py)
Writes grader-results.json (boilerplate standard format)
Writes grader-report.md (PR comment)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
RAW_FILE = ROOT / "grader-results-raw.json"
AI_FILE = ROOT / "ai-feedback.json"
OUT_JSON = ROOT / "grader-results.json"
OUT_MD = ROOT / "grader-report.md"

# ---------------------------------------------------------------------------
# Rubric — points per category.
# These values MUST match the per-file point totals in GitHub Classroom.
# Modify these per lab to match the actual point distribution.
# ---------------------------------------------------------------------------
CATEGORY_POINTS = {
    "Structure": 6,
    "Execution": 15,
    "Quality": 8,
}

TOTAL_POINTS = sum(CATEGORY_POINTS.values())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_pytest_results(raw: dict) -> list:
    """Parse pytest-json-report output into category dicts."""
    categories: dict = {}
    for test in raw.get("tests", []):
        parts = test["nodeid"].split("::")
        if len(parts) < 3:
            continue
        class_name = parts[-2]
        method_name = parts[-1]
        check_name = (
            method_name.replace("test_", "", 1).replace("_", " ").strip().capitalize()
        )
        passed = test.get("outcome") == "passed"
        hint = None
        if not passed:
            longrepr = test.get("call", {}).get("longrepr", "")
            if isinstance(longrepr, str) and longrepr:
                hint = longrepr.split("\n")[0][:400] or None

        categories.setdefault(class_name, []).append(
            {"name": check_name, "passed": passed, "hint": hint}
        )

    result = []
    for name, checks in categories.items():
        score = sum(1 for c in checks if c["passed"])
        total = len(checks)
        max_pts = CATEGORY_POINTS.get(name, 0)
        points = round((score / total) * max_pts, 1) if total > 0 and max_pts > 0 else 0.0
        result.append(
            {
                "name": name,
                "score": score,
                "total": total,
                "points": points,
                "maxPoints": max_pts,
                "checks": checks,
            }
        )
    return result


def progress_bar(score: float, total: float) -> str:
    if total == 0:
        return "`░░░░░░░░░░`"
    filled = round((score / total) * 10)
    return "`" + "█" * filled + "░" * (10 - filled) + "`"


def status_message(pct: int) -> str:
    if pct == 100:
        return "Perfect score! Excellent work!"
    if pct >= 80:
        return "Almost there — just a few more to fix!"
    if pct >= 50:
        return "Good progress, keep going!"
    if pct >= 20:
        return "You've started! Keep building."
    return "Time to write some code!"


def cat_icon(cat: dict) -> str:
    if cat["score"] == cat["total"]:
        return "✅"
    if cat["score"] == 0:
        return "❌"
    return "⚠️"


def render_ai_section(ai: dict) -> str:
    """Render the AI Review section of the PR comment."""
    if not ai.get("evaluated"):
        reason = ai.get("reason", "AI Review: not configured.")
        return f"\n---\n\n> {reason}\n\n"

    artifact = ai.get("artifact", "")
    total = ai.get("total_score", 0)
    max_s = ai.get("max_score", 0)
    artifact_label = Path(artifact).name if artifact else "artifact"

    md = f"\n---\n\n### 🤖 AI Review — {artifact_label}   {total} / {max_s}\n\n"
    for i, criterion in enumerate(ai.get("criteria", [])):
        open_attr = " open" if i == 0 else ""
        md += f"<details{open_attr}>\n"
        md += (
            f"<summary><b>{criterion['name']}</b>"
            f" — {criterion['score']} / {criterion['max']}</summary>\n\n"
        )
        md += f"✅ **Strength:** {criterion.get('strength', '')}\n\n"
        md += f"⚠️ **Gap:** {criterion.get('gap', '')}\n\n"
        md += f"💡 **Action:** {criterion.get('action', '')}\n\n"
        md += "</details>\n\n"

    summary = ai.get("summary", "")
    if summary:
        md += f"> 💬 **Overall:** {summary}\n\n"
    return md


def build_report(categories: list, ai: dict, lab_name: str) -> tuple:
    """Return (grader-report.md content, grader-results dict)."""
    earned = round(sum(c["points"] for c in categories), 1)
    pct = round(earned / TOTAL_POINTS * 100) if TOTAL_POINTS > 0 else 0

    md = "## Lab Grader Results\n\n"
    md += f"> **Score: {earned} / {TOTAL_POINTS} pts ({pct}%)** — {status_message(pct)}\n"
    md += f"> {progress_bar(earned, TOTAL_POINTS)}\n\n"
    md += "---\n\n"
    md += "### Score Breakdown\n\n"
    md += "| | Category | Points | Checks |\n"
    md += "|---|---|---|---|\n"
    for cat in categories:
        icon = cat_icon(cat)
        chk = f"{cat['score']}/{cat['total']}" if cat["score"] < cat["total"] else "all passing"
        md += f"| {icon} | **{cat['name']}** | {cat['points']} / {cat['maxPoints']} | {chk} |\n"
    md += "\n---\n\n"
    md += "### Details\n\n"
    for cat in categories:
        icon = cat_icon(cat)
        pts = f"{cat['points']} / {cat['maxPoints']} pts"
        chk = f"{cat['score']}/{cat['total']} checks"
        failing = [c for c in cat["checks"] if not c["passed"]]
        md += "<details>\n"
        md += f"<summary>{icon} <b>{cat['name']}</b> — {pts} — {chk}</summary>\n\n"
        md += "| Check | Status | Hint |\n|---|---|---|\n"
        for check in cat["checks"]:
            status = "✅ Pass" if check["passed"] else "❌ Fail"
            hint = check.get("hint") or ""
            md += f"| {check['name']} | {status} | {hint} |\n"
        if failing:
            md += "\n**What to fix:**\n"
            for check in failing:
                suffix = f" — {check['hint']}" if check.get("hint") else ""
                md += f"- `{check['name']}`{suffix}\n"
        md += "\n</details>\n\n"

    md += render_ai_section(ai)

    results = {
        "lab": lab_name,
        "score": earned,
        "total": TOTAL_POINTS,
        "duration": 0,
        "categories": categories,
    }
    return md, results


def main():
    raw = json.loads(RAW_FILE.read_text())
    ai = (
        json.loads(AI_FILE.read_text())
        if AI_FILE.exists()
        else {"evaluated": False, "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable."}
    )
    categories = parse_pytest_results(raw)
    lab_name = ROOT.name
    md, results = build_report(categories, ai, lab_name)
    OUT_JSON.write_text(json.dumps(results, indent=2))
    OUT_MD.write_text(md)
    print(f"grader-results.json written ({results['score']}/{results['total']} pts)")
    print("grader-report.md written")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — verify they PASS**

```bash
pip install pytest python-frontmatter portkey-ai pytest-json-report
pytest tests/test_summarize.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add templates/python-ai/.grader/summarize.py tests/
git commit -m "feat: add summarize.py and tests for automated grading report"
```

---

## Task 3: ai_evaluator.py — SPEC Parsing and Artifact Reading

**Files:**
- Create: `templates/python-ai/.grader/ai_evaluator.py` (partial — SPEC parsing + artifact reading only)
- Modify: `tests/test_ai_evaluator.py`

- [ ] **Step 1: Write failing tests for parse_spec() and read_artifact()**

`tests/test_ai_evaluator.py`:
```python
import json
import sys
from pathlib import Path
import pytest

from ai_evaluator import parse_spec, read_artifact, build_prompt, clamp_scores

SAMPLE_SPEC = """\
---
artifact: notebook/walkthrough.ipynb
artifact_type: jupyter
max_score: 20
---

# AI Evaluation Rubric

## MCP Explanation (max: 5)
Must mention: server, client, stdio.

## ASCII Diagram (max: 5)
Must include 3 or more nodes.
"""

SAMPLE_NOTEBOOK = {
    "cells": [
        {"cell_type": "markdown", "source": ["# Walkthrough\n", "Some text."]},
        {"cell_type": "code", "source": ["print('hello')"]},
        {"cell_type": "raw", "source": ["ignored"]},
    ]
}


def test_parse_spec_frontmatter(tmp_path):
    spec_file = tmp_path / "SPEC.md"
    spec_file.write_text(SAMPLE_SPEC)
    spec = parse_spec(spec_file)
    assert spec["artifact"] == "notebook/walkthrough.ipynb"
    assert spec["artifact_type"] == "jupyter"
    assert spec["max_score"] == 20


def test_parse_spec_criteria(tmp_path):
    spec_file = tmp_path / "SPEC.md"
    spec_file.write_text(SAMPLE_SPEC)
    spec = parse_spec(spec_file)
    assert len(spec["criteria"]) == 2
    assert spec["criteria"][0]["name"] == "MCP Explanation"
    assert spec["criteria"][0]["max"] == 5
    assert "server" in spec["criteria"][0]["description"]


def test_read_artifact_jupyter(tmp_path):
    nb_file = tmp_path / "notebook.ipynb"
    nb_file.write_text(json.dumps(SAMPLE_NOTEBOOK))
    content = read_artifact(nb_file, "jupyter")
    assert "[MARKDOWN CELL]" in content
    assert "Some text." in content
    assert "[CODE CELL]" in content
    assert "print('hello')" in content
    # raw cells are excluded
    assert "ignored" not in content


def test_read_artifact_markdown(tmp_path):
    md_file = tmp_path / "ADR.md"
    md_file.write_text("# Decision\n\nWe chose X.")
    content = read_artifact(md_file, "markdown")
    assert content == "# Decision\n\nWe chose X."


def test_read_artifact_jupyter_excludes_empty_cells(tmp_path):
    nb = {"cells": [{"cell_type": "markdown", "source": ["   "]}, {"cell_type": "code", "source": ["x = 1"]}]}
    nb_file = tmp_path / "nb.ipynb"
    nb_file.write_text(json.dumps(nb))
    content = read_artifact(nb_file, "jupyter")
    # empty markdown cell excluded
    assert content.count("[MARKDOWN CELL]") == 0
    assert "x = 1" in content


def test_clamp_scores():
    criteria_result = [{"name": "A", "score": 7.0, "max": 5}]
    criteria_spec = [{"name": "A", "max": 5}]
    result = clamp_scores(criteria_result, criteria_spec)
    assert result[0]["score"] == 5.0


def test_clamp_scores_no_clamp_needed():
    criteria_result = [{"name": "A", "score": 3.5, "max": 5}]
    criteria_spec = [{"name": "A", "max": 5}]
    result = clamp_scores(criteria_result, criteria_spec)
    assert result[0]["score"] == 3.5
```

- [ ] **Step 2: Run tests — verify they FAIL**

```bash
pytest tests/test_ai_evaluator.py -v
```
Expected: `ImportError: No module named 'ai_evaluator'`

- [ ] **Step 3: Implement parse_spec(), read_artifact(), build_prompt(), clamp_scores()**

`templates/python-ai/.grader/ai_evaluator.py`:
```python
"""
Reads .grader/SPEC.md (rubric) and the student artifact.
Calls Claude Haiku via Portkey.
Writes ai-feedback.json with structured coaching feedback.
"""
import json
import os
import re
import sys
from pathlib import Path

import frontmatter


# ---------------------------------------------------------------------------
# SPEC parsing
# ---------------------------------------------------------------------------

def parse_spec(spec_path: Path) -> dict:
    """Parse SPEC.md frontmatter and ## Criterion (max: N) headings."""
    post = frontmatter.loads(spec_path.read_text(encoding="utf-8"))

    criteria = []
    pattern = r"^## (.+?) \(max: (\d+)\)\n(.*?)(?=^## |\Z)"
    for m in re.finditer(pattern, post.content, re.MULTILINE | re.DOTALL):
        criteria.append(
            {
                "name": m.group(1).strip(),
                "max": int(m.group(2)),
                "description": m.group(3).strip(),
            }
        )

    return {
        "artifact": str(post["artifact"]),
        "artifact_type": str(post["artifact_type"]),
        "max_score": int(post["max_score"]),
        "criteria": criteria,
    }


# ---------------------------------------------------------------------------
# Artifact reading
# ---------------------------------------------------------------------------

def read_artifact(artifact_path: Path, artifact_type: str) -> str:
    """Read student artifact. For Jupyter notebooks, extract cell sources only."""
    if artifact_type == "jupyter":
        nb = json.loads(artifact_path.read_text(encoding="utf-8"))
        parts = []
        for cell in nb.get("cells", []):
            if cell.get("cell_type") not in ("markdown", "code"):
                continue
            source = "".join(cell.get("source", []))
            if source.strip():
                parts.append(f"[{cell['cell_type'].upper()} CELL]\n{source}")
        return "\n\n".join(parts)
    else:
        return artifact_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(artifact_content: str, artifact_type: str, criteria: list) -> str:
    rubric_text = "\n\n".join(
        f"## {c['name']} (max: {c['max']})\n{c['description']}" for c in criteria
    )
    return f"""You are an expert technical coach reviewing a consultant's work at Perficient.
Your goal is to give feedback that is specific, actionable, and encouraging.

## Artifact to evaluate
Type: {artifact_type}
Content:
{artifact_content}

## Rubric
{rubric_text}

## Instructions
For each criterion:
1. Identify what the consultant did well (be specific — quote or reference their work).
2. Identify what is missing or imprecise (be concrete, not vague).
3. Give one specific action they can take to improve this criterion.

Score each criterion from 0 to its max (floats allowed, 1 decimal).
Do not round up — partial credit only when the criterion is partially met.

Return ONLY valid JSON matching this schema:
{{
  "criteria": [
    {{
      "name": "...",
      "score": N.N,
      "max": N,
      "strength": "What they did well",
      "gap": "What is missing or imprecise",
      "action": "One specific thing to improve"
    }}
  ],
  "summary": "2-3 sentence coaching summary. Start with a genuine strength, then the most impactful improvement."
}}"""


# ---------------------------------------------------------------------------
# Score validation
# ---------------------------------------------------------------------------

def clamp_scores(criteria_result: list, criteria_spec: list) -> list:
    """Clamp model-returned scores to their criterion max. Round to 1 decimal."""
    spec_map = {c["name"]: c["max"] for c in criteria_spec}
    for c in criteria_result:
        max_val = spec_map.get(c["name"], c.get("max", 10))
        c["score"] = round(min(float(c["score"]), float(max_val)), 1)
        c["max"] = max_val
    return criteria_result
```

Note: `call_portkey()` and `main()` are added in Task 4.

- [ ] **Step 4: Run tests — verify they PASS**

```bash
pytest tests/test_ai_evaluator.py -v
```
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add templates/python-ai/.grader/ai_evaluator.py tests/test_ai_evaluator.py
git commit -m "feat: add ai_evaluator SPEC parsing and artifact reading"
```

---

## Task 4: ai_evaluator.py — Portkey Call and main()

**Files:**
- Modify: `templates/python-ai/.grader/ai_evaluator.py` (add call_portkey + main)
- Modify: `tests/test_ai_evaluator.py` (add Portkey call tests)

- [ ] **Step 1: Write failing tests for call_portkey() and main() behavior**

Add to `tests/test_ai_evaluator.py`:
```python
from unittest.mock import MagicMock, patch
import os

from ai_evaluator import call_portkey


def test_call_portkey_returns_parsed_json():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "criteria": [{"name": "A", "score": 4.0, "max": 5, "strength": "s", "gap": "g", "action": "a"}],
        "summary": "Good work."
    })
    # Patch at the module level (not inside with block) to avoid cached-import issues
    with patch("ai_evaluator.Portkey") as MockPortkey:
        MockPortkey.return_value.chat.completions.create.return_value = mock_response
        result = call_portkey("some prompt", "fake-key")
    assert result["criteria"][0]["name"] == "A"
    assert result["summary"] == "Good work."


def test_main_no_api_key_writes_not_configured(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)
    # Create dummy SPEC.md so spec parsing doesn't fail first
    (tmp_path / ".grader").mkdir()
    (tmp_path / ".grader" / "SPEC.md").write_text(
        "---\nartifact: x.md\nartifact_type: markdown\nmax_score: 10\n---\n## C (max: 10)\nDesc\n"
    )
    from ai_evaluator import main
    main()
    feedback = json.loads((tmp_path / "ai-feedback.json").read_text())
    assert feedback["evaluated"] is False
    assert "PORTKEY_API_KEY" in feedback["reason"]


def test_main_artifact_not_found_writes_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PORTKEY_API_KEY", "fake-key")
    (tmp_path / ".grader").mkdir()
    (tmp_path / ".grader" / "SPEC.md").write_text(
        "---\nartifact: missing/file.md\nartifact_type: markdown\nmax_score: 10\n---\n## C (max: 10)\nDesc\n"
    )
    from ai_evaluator import main
    main()
    feedback = json.loads((tmp_path / "ai-feedback.json").read_text())
    assert feedback["evaluated"] is False
    assert "artifact not found" in feedback["reason"]
```

- [ ] **Step 2: Run new tests — verify they FAIL**

```bash
pytest tests/test_ai_evaluator.py::test_call_portkey_returns_parsed_json -v
pytest tests/test_ai_evaluator.py::test_main_no_api_key_writes_not_configured -v
```
Expected: `ImportError` or `AttributeError` (call_portkey / main not defined yet).

- [ ] **Step 3: Add call_portkey() and main() to ai_evaluator.py**

Add after `clamp_scores()`:
```python
# ---------------------------------------------------------------------------
# Portkey API call
# ---------------------------------------------------------------------------

def call_portkey(prompt: str, api_key: str) -> dict:
    """Call Claude Haiku via Portkey. Returns parsed JSON dict."""
    from portkey_ai import Portkey

    client = Portkey(api_key=api_key)
    response = client.chat.completions.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _write_error(reason: str) -> None:
    Path("ai-feedback.json").write_text(
        json.dumps({"evaluated": False, "reason": reason}, indent=2), encoding="utf-8"
    )


def main() -> None:
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        _write_error("AI Review: not configured — set PORTKEY_API_KEY to enable.")
        print("PORTKEY_API_KEY not set — skipping AI evaluation")
        return

    spec_path = Path(".grader") / "SPEC.md"
    spec = parse_spec(spec_path)

    artifact_path = Path(spec["artifact"])
    if not artifact_path.exists():
        _write_error(f"AI Review: artifact not found at `{spec['artifact']}`.")
        print(f"Artifact not found: {spec['artifact']}")
        return

    artifact_content = read_artifact(artifact_path, spec["artifact_type"])
    prompt = build_prompt(artifact_content, spec["artifact_type"], spec["criteria"])

    raw_result = None
    for attempt in range(2):
        try:
            raw_result = call_portkey(prompt, api_key)
            break
        except json.JSONDecodeError:
            if attempt == 1:
                _write_error("AI Review: evaluation failed (invalid response). Score not affected.")
                return
        except Exception:
            _write_error("AI Review: evaluation failed (API error). Score not affected.")
            return

    criteria_result = clamp_scores(raw_result["criteria"], spec["criteria"])
    total_score = round(sum(c["score"] for c in criteria_result), 1)

    output = {
        "evaluated": True,
        "artifact": spec["artifact"],
        "total_score": total_score,
        "max_score": spec["max_score"],
        "criteria": criteria_result,
        "summary": raw_result.get("summary", ""),
    }
    Path("ai-feedback.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"ai-feedback.json written ({total_score}/{spec['max_score']})")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all ai_evaluator tests — verify they PASS**

```bash
pytest tests/test_ai_evaluator.py -v
```
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add templates/python-ai/.grader/ai_evaluator.py tests/test_ai_evaluator.py
git commit -m "feat: add ai_evaluator Portkey call and main entrypoint"
```

---

## Task 5: summarize.py — AI Review Section

**Files:**
- `summarize.py` already has `render_ai_section()` from Task 2.
- This task adds tests to verify the AI section renders correctly.

- [ ] **Step 1: Write failing tests for render_ai_section()**

Add to `tests/test_summarize.py`:
```python
SAMPLE_AI_FEEDBACK = {
    "evaluated": True,
    "artifact": "notebook/walkthrough.ipynb",
    "total_score": 14.5,
    "max_score": 20,
    "criteria": [
        {
            "name": "MCP Explanation",
            "score": 4.0,
            "max": 5,
            "strength": "Explains server-client well.",
            "gap": "Missing subprocess detail.",
            "action": "Add a sentence about stdin/stdout pipes.",
        },
        {
            "name": "ASCII Diagram",
            "score": 3.0,
            "max": 5,
            "strength": "Has 3 nodes.",
            "gap": "Arrows not labeled.",
            "action": "Add --[tool_call]--> labels.",
        },
    ],
    "summary": "Good architectural understanding.",
}

SAMPLE_AI_NOT_CONFIGURED = {
    "evaluated": False,
    "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable.",
}


def test_render_ai_section_shows_score():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "14.5 / 20" in md


def test_render_ai_section_first_criterion_open():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "<details open>" in md


def test_render_ai_section_second_criterion_collapsed():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    # First occurrence is open, subsequent ones are collapsed
    assert "<details>" in md


def test_render_ai_section_has_strength_gap_action():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "Strength" in md
    assert "Gap" in md
    assert "Action" in md
    assert "Explains server-client well." in md


def test_render_ai_section_has_summary():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "Good architectural understanding." in md


def test_render_ai_section_not_configured():
    md = render_ai_section(SAMPLE_AI_NOT_CONFIGURED)
    assert "PORTKEY_API_KEY" in md
    assert "<details" not in md
```

- [ ] **Step 2: Run new tests — verify they PASS** (render_ai_section was already implemented)

```bash
pytest tests/test_summarize.py -v
```
Expected: all tests PASS (the function was written in Task 2; these tests validate it).

- [ ] **Step 3: Commit**

```bash
git add tests/test_summarize.py
git commit -m "test: add AI Review section rendering tests for summarize.py"
```

---

## Task 6: grade.yml

**Files:**
- Create: `templates/python-ai/.github/workflows/grade.yml`

No unit tests for YAML. Verified by reading the file carefully.

- [ ] **Step 1: Create grade.yml**

`templates/python-ai/.github/workflows/grade.yml`:
```yaml
name: Grade Lab

on:
  pull_request:
    branches: [main]

permissions:
  pull-requests: write

jobs:
  grade:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run grader
        run: |
          pytest .grader/checks/ \
            --json-report \
            --json-report-file=grader-results-raw.json \
            -v
        continue-on-error: true

      - name: Run AI evaluator
        run: python .grader/ai_evaluator.py
        env:
          PORTKEY_API_KEY: ${{ secrets.PORTKEY_API_KEY }}
        continue-on-error: true

      - name: Generate report
        run: python .grader/summarize.py

      - name: Post comment
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          header: grader
          path: grader-report.md

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: grader-results
          path: |
            grader-results.json
            ai-feedback.json
          retention-days: 30
```

- [ ] **Step 2: Verify the workflow manually**

Read through the file and confirm:
- Steps 1–4 match the spec sequence exactly
- `PORTKEY_API_KEY` is passed as `env:`, not hardcoded
- Both grader and AI evaluator use `continue-on-error: true`
- `summarize.py` runs after both (no `continue-on-error` — if summarize fails, the PR comment won't post)
- Both output files are uploaded as artifacts

- [ ] **Step 3: Commit**

```bash
git add templates/python-ai/.github/workflows/grade.yml
git commit -m "feat: add grade.yml workflow for python-ai template"
```

---

## Task 7: Documentation Updates

**Files:**
- Modify: `docs/template-differences.md`
- Modify: `docs/how-to-create-a-lab.md`
- Modify: `docs/grader-guide.md`

- [ ] **Step 1: Add python-ai to template-differences.md**

Add a new section at the end:

```markdown
## python-ai

| | |
|---|---|
| Language | Python 3.12 (default) |
| Runner | pytest + pytest-json-report |
| Grade command | `pytest .grader/checks/ --json-report --json-report-file=grader-results-raw.json` |
| Checks location | `.grader/checks/test_*.py` |
| Report input | `grader-results-raw.json` (pytest-json-report) + `ai-feedback.json` |
| Report script | `.grader/summarize.py` |
| Category = | Class name inside check file (e.g. `class Structure:`) |
| Check = | Method name (e.g. `def test_file_exists`) |
| Hint = | Assertion message |
| AI evaluator | `.grader/ai_evaluator.py` — reads `.grader/SPEC.md` + student artifact → Portkey → `ai-feedback.json` |

**Python version override:** If a lab requires an older Python (e.g. `mcp==1.3.0` targets 3.11),
override the version in `.devcontainer/devcontainer.json`:
```json
"image": "mcr.microsoft.com/devcontainers/python:3.11"
```
Also update `actions/setup-python` in `grade.yml` to match.
```

- [ ] **Step 2: Add SPEC.md configuration step to how-to-create-a-lab.md**

After Step 3 ("Write the grading criteria"), add:

```markdown
### 3b. Configure the AI evaluator (optional)

Edit `.grader/SPEC.md` to define the rubric for qualitative AI evaluation:

1. Set `artifact` to the path of the student artifact to evaluate (relative to repo root).
2. Set `artifact_type` to `jupyter`, `markdown`, or `python`.
3. Set `max_score` to the total points this artifact is worth.
4. Replace the placeholder criteria with lab-specific rubric items using the format:
   `## Criterion Name (max: N)`

The AI evaluator runs automatically if `PORTKEY_API_KEY` is set as a repository secret.
If the secret is not set, the AI Review section in the PR comment shows "not configured."
```

- [ ] **Step 3: Add SPEC.md authoring guide to grader-guide.md**

Add a new section at the end:

```markdown
## Writing AI-evaluable specs (SPEC.md)

The AI evaluator reads `.grader/SPEC.md` to know what to evaluate and how.

### Schema

SPEC.md uses YAML frontmatter followed by Markdown rubric criteria:

```markdown
---
artifact: notebook/walkthrough.ipynb   # path relative to repo root
artifact_type: jupyter                 # jupyter | markdown | python
max_score: 20                          # total points for this artifact
---

## Criterion Name (max: 5)
Describe what a passing response must include. Be specific — the model
uses this description to score and give feedback.
```

### artifact_type values

| Type | When to use |
|---|---|
| `jupyter` | `.ipynb` notebooks — cell sources are extracted automatically |
| `markdown` | `.md` files (ADRs, reflections, READMEs) |
| `python` | `.py` files you want qualitatively reviewed |

### Writing good criteria

Each criterion body is passed directly to the model. Be explicit about minimum bars:

**Too vague:** "Student understands MCP."

**Good:** "Must mention: server, client, stdio, and at least one of: subprocess, pipe, transport."

### Criterion total vs max_score

The sum of all `(max: N)` values should equal `max_score`. The evaluator does not enforce this,
but a mismatch will produce confusing scores in the PR comment.
```

- [ ] **Step 4: Commit documentation**

```bash
git add docs/template-differences.md docs/how-to-create-a-lab.md docs/grader-guide.md
git commit -m "docs: add python-ai template documentation and AI evaluator guide"
```

---

## Final Verification

- [ ] Run the full test suite from the boilerplate root:
  ```bash
  pytest tests/ -v
  ```
  Expected: all tests PASS.

- [ ] Verify `new-lab.sh` works with the new template:
  ```bash
  bash scripts/new-lab.sh
  # Select: python-ai
  # Lab name: test-lab-python-ai
  # Output dir: /tmp/
  ```
  Expected: `/tmp/test-lab-python-ai/` created with all template files.

- [ ] Confirm `new-lab.sh` does not need modification (it uses `ls templates/` to list available options — `python-ai` will appear automatically).

- [ ] Clean up test lab:
  ```bash
  rm -rf /tmp/test-lab-python-ai
  ```
