# Grader Guide

## How it works

Every lab has a `.github/workflows/grade.yml` that runs on every Pull Request:

1. Runs the grader (Playwright or pytest)
2. Parses results and generates `grader-results.json` and `grader-report.md`
3. Posts a score comment on the PR with a rubric breakdown, per-check status, and actionable hints
4. Uploads `grader-results.json` as an artifact

## Rubric and point system

Checks are grouped into categories. Each category has a **point value** defined in `CATEGORY_POINTS` inside `summarize.js` (or `summarize.py` for Python labs). Points within a category are awarded **proportionally** — if a student passes 7 of 9 checks in a 15-point category, they earn 11.7 pts.

### Standard categories

| Category | Description | Typical weight |
|---|---|---|
| **Structure** | Required files and directories exist, correct project layout | ~20% |
| **Execution** | Core logic works correctly — the main exercise | ~50% |
| **Quality** | Code style, docstrings/JSDoc, type hints, naming conventions | ~20% |
| **AI Usage** | Evidence of Copilot/AI tool usage in the code (lab-specific) | ~10% |

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

> The exact point values for each lab are defined in `CATEGORY_POINTS` in `summarize.js` / `summarize.py`.
> These values **must match** the per-file point totals configured in GitHub Classroom.

### GitHub Classroom configuration

For the CSV export to show meaningful scores, configure **one autograder test per category file** in the Classroom UI:

| GitHub Classroom test | Command | Points |
|---|---|---|
| Structure | `pytest .grader/checks/test_structure.py` | 6 |
| Execution | `pytest .grader/checks/test_execution.py` | 15 |
| Quality | `pytest .grader/checks/test_quality.py` | 4 |
| AI Usage | `pytest .grader/checks/test_student_work.py` | 4 |

> Classroom scoring is binary per category (all-or-nothing per file). The PR comment from `grade.yml` shows proportional partial credit within each category.

## grader-results.json format

All templates produce this standard JSON:

```json
{
  "lab": "lab-name",
  "score": 24.3,
  "total": 29,
  "duration": 4500,
  "categories": [
    {
      "name": "Structure",
      "score": 3,
      "total": 3,
      "points": 6.0,
      "maxPoints": 6,
      "checks": [
        { "name": "check description", "passed": true,  "hint": null },
        { "name": "other check",       "passed": false, "hint": "Actionable hint for the student" }
      ]
    }
  ]
}
```

## Writing checks — Playwright (TypeScript)

Checks live in `.grader/checks/`. Each file is a category, each `test()` is a check.

```typescript
import { test, expect } from '@playwright/test';

test.describe('Execution', () => {

    test('component renders the correct title', async ({ page }) => {
        // The first argument to expect() becomes the hint shown to the student on failure
        await expect(page.getByRole('heading'), 'Add a <h1> with the lab title inside App.tsx').toBeVisible();
    });

});
```

**Tips:**
- Use descriptive test names — they appear as-is in the PR comment
- Put the hint as the second argument to `expect()`: `expect(locator, 'your hint here').toBeVisible()`
- Category name (the `test.describe` title) must match a key in `CATEGORY_POINTS`

## Writing checks — Python (pytest)

Checks live in `.grader/checks/`. Each file is a category, each method inside a class is a check.

```python
class Execution:

    def test_parse_csv_row_splits_by_comma(self):
        result = parse_csv_row("alice,95,engineering")
        assert result == ["alice", "95", "engineering"], (
            "parse_csv_row should split the row by comma and return a list"
        )
```

**Tips:**
- Class name = category name → must match a key in `CATEGORY_POINTS`
- Method name → check label (underscores replaced with spaces, capitalized)
- Assertion message → hint shown to the student on failure. Write it as a human-readable fix instruction.

## Recommended category structure

| Category | What to check |
|---|---|
| Structure | Required files and directories exist |
| Execution | Code runs and produces correct output |
| Quality | Code style, docstrings, type hints, naming |
| AI Usage | Evidence of AI tool usage (Copilot comments, etc.) |