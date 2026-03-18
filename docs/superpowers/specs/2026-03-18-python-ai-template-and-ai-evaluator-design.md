# python-ai Template + AI Evaluator — Design Spec
**Date:** 2026-03-18
**Project:** codespaces-lab-boilerplate
**Status:** Approved (3 review rounds — Sections 1, 2, 3)

---

## Context

The boilerplate currently has one template: `playwright` (TypeScript + Playwright Test). This spec defines the `python-ai` template (Python 3.12 + pytest) and a built-in AI evaluator feature that provides qualitative coaching feedback on student artifacts via GitHub Actions.

**Why the AI evaluator:** L2 (notebook, 20% of grade) and L3 (ADR, 30% of grade) require qualitative evaluation that cannot be captured by automated tests. The evaluator replaces manual instructor review with Claude Haiku via Portkey (~$0.003/evaluation).

**Deployment model:** The instructor/admin sets `PORTKEY_API_KEY` once at the org or repo level. Students never configure it. Every student PR automatically gets AI feedback posted to the grader PR comment.

---

## Section 1: Template Structure

```
templates/python-ai/
├── .devcontainer/
│   └── devcontainer.json            ← Python 3.12 + Copilot extension
├── .github/
│   └── workflows/
│       └── grade.yml                ← Grader + AI evaluator, runs on every PR
├── .grader/
│   ├── checks/
│   │   ├── test_structure.py        ← Placeholder — instructor overwrites
│   │   ├── test_execution.py        ← Placeholder — instructor overwrites
│   │   └── test_quality.py          ← Placeholder — instructor overwrites
│   ├── ai_evaluator.py              ← Reusable script: reads artifact + SPEC.md → calls Portkey → writes ai-feedback.json
│   ├── SPEC.md                      ← Rubric template; instructor customizes per lab
│   └── summarize.py                 ← Parses pytest JSON + incorporates AI feedback → grader-report.md
├── src/
│   └── .gitkeep                     ← Starter code goes here (optional; new-lab.sh copies this folder as-is)
├── docs/
│   └── instructions.md              ← Instructor defines the exercise here
├── requirements.txt                 ← pytest, pytest-asyncio, portkey-ai, python-frontmatter
├── pytest.ini                       ← asyncio_mode = auto, testpaths = tests
└── README.md
```

**Conventions:**
- `ai_evaluator.py` and `summarize.py` are boilerplate infrastructure — never modified per lab.
- `SPEC.md` is the only file the instructor touches to configure the AI review.
- Python version: **3.12 default**. Labs that require an older runtime (e.g. `mcp==1.3.0` targets 3.11) override the version in `devcontainer.json`. This is documented in `docs/template-differences.md`.

---

## Section 2: Grading Workflow and Scripts

### `grade.yml` — step sequence

```
PR opened/updated
       │
1. actions/checkout@v4
       │
2. actions/setup-python@v5  (python-version: '3.12')
       │
3. pip install -r requirements.txt
       │
4. pytest .grader/checks/
     --json-report
     --json-report-file=grader-results-raw.json
   (continue-on-error: true)
       │
5. python .grader/ai_evaluator.py
   (env: PORTKEY_API_KEY from secrets; continue-on-error: true)
   → writes ai-feedback.json
       │
6. python .grader/summarize.py
   (reads grader-results-raw.json + ai-feedback.json → grader-report.md + grader-results.json)
       │
7. marocchino/sticky-pull-request-comment@v2  (path: grader-report.md)
       │
8. actions/upload-artifact@v4
   (grader-results.json, ai-feedback.json; retention-days: 30)
```

**Workflow permissions:** `pull-requests: write` (required for sticky comment).

### `ai_evaluator.py` — responsibilities

1. Reads `.grader/SPEC.md` — parses YAML frontmatter for `artifact`, `artifact_type`, `max_score`. Parses criteria from `## Criterion Name (max: N)` headings.
2. Reads the student artifact at the path specified by `artifact`.
   - `artifact_type: jupyter` → extracts cell `source` fields (markdown + code) only; does not pass raw `.ipynb` JSON to the model.
   - `artifact_type: markdown` or `artifact_type: python` → reads file as plain text.
3. Builds and sends the prompt to Claude Haiku via `portkey-ai` SDK.
4. Parses the JSON response. Scores are floats rounded to 1 decimal. If a model-returned `score` exceeds the criterion `max`, it is clamped to `max`.
5. Computes `total_score = sum(c["score"] for c in criteria)`.
6. Writes `ai-feedback.json`.

**If `PORTKEY_API_KEY` is not set:** writes `{"evaluated": false, "reason": "PORTKEY_API_KEY not configured"}` and exits with code 0.

#### `ai-feedback.json` schema

```json
{
  "evaluated": true,
  "artifact": "notebook/walkthrough.ipynb",
  "total_score": 14.5,
  "max_score": 20,
  "criteria": [
    {
      "name": "MCP Explanation",
      "score": 4.0,
      "max": 5,
      "strength": "Clearly explains server-client pattern and identifies stdio as transport.",
      "gap": "Does not mention subprocess pipes — the mechanism behind stdio in a Codespace.",
      "action": "Add: 'The client launches the server as a subprocess and communicates via stdin/stdout pipes.'"
    }
  ],
  "summary": "Architectural understanding is solid. Strengthen the error trace in Cell 3 by walking each hop explicitly."
}
```

### `summarize.py` — integration

Reads `grader-results-raw.json` and `ai-feedback.json`. Produces `grader-report.md` and `grader-results.json`.

The denominator for the automated score is derived from `CATEGORY_POINTS` dict defined at the top of `summarize.py` — same pattern as the `playwright` template.

---

## Section 3: AI Evaluator Prompt Design and Output UX

### Feedback philosophy

The evaluator is a coach, not a judge. The PR comment answers three questions per criterion:
- Strength: what the consultant did well (specific, referencing their work)
- Gap: what is missing or imprecise (concrete, not vague)
- Action: one specific thing to improve

The model returns plain text fields (`strength`, `gap`, `action`). `summarize.py` maps them to ✅ ⚠️ 💡 icons when rendering the PR comment. The model never sees or outputs emoji.

### Prompt sent to Claude Haiku

```
You are an expert technical coach reviewing a consultant's work at Perficient.
Your goal is to give feedback that is specific, actionable, and encouraging.

## Artifact to evaluate
Type: {artifact_type}
Content:
{artifact_content}

## Rubric
{rubric_criteria}

## Instructions
For each criterion:
1. Identify what the consultant did well (be specific — quote or reference their work).
2. Identify what is missing or imprecise (be concrete, not vague).
3. Give one specific action they can take to improve this criterion.

Score each criterion from 0 to its max (floats allowed, 1 decimal).
Do not round up — partial credit only when the criterion is partially met.

Return ONLY valid JSON matching this schema:
{
  "criteria": [
    {
      "name": "...",
      "score": N.N,
      "max": N,
      "strength": "What they did well",
      "gap": "What is missing or imprecise",
      "action": "One specific thing to improve"
    }
  ],
  "summary": "2-3 sentence coaching summary. Start with a genuine strength, then the most impactful improvement."
}
```

### PR Comment — AI Review section

```markdown
### Robot AI Review — Notebook Walkthrough   14.5 / 20

<details open>
<summary><b>MCP Explanation</b> — 4.0 / 5</summary>

Strength: Clearly explains the server-client pattern and correctly identifies stdio as the transport layer.
Gap: Does not mention that stdio uses subprocess pipes under the hood.
Action: Add one sentence: "The client launches the server as a subprocess and communicates via stdin/stdout pipes."

</details>

<details>
<summary><b>ASCII Diagram</b> — 3.0 / 5</summary>

Strength: Diagram has User, Agent, MCP Server — covers the required 3 nodes.
Gap: Arrows are not labeled — direction of data flow is not clear.
Action: Add labels: --[tool_call]--> and <--[result]--.

</details>

---
> Overall: Architectural understanding is solid. Strengthen the error trace in Cell 3 by walking each hop explicitly.
```

**Rendering rules:**
- First criterion renders `<details open>` (visible by default).
- Remaining criteria render `<details>` (collapsed).
- Strength prefixed with checkmark icon, Gap with warning icon, Action with lightbulb icon in actual rendered output.

### Error behavior

| Situation | PR comment text | Exit code |
|---|---|---|
| `PORTKEY_API_KEY` not configured | `AI Review: not configured — set PORTKEY_API_KEY to enable.` | 0 |
| Artifact not found | `AI Review: artifact not found at \`{path}\`.` | 0 |
| Portkey timeout / API error | `AI Review: evaluation failed (API error). Score not affected.` | 0 |
| Invalid JSON in model response | Retry once. If still invalid: `AI Review: evaluation failed (invalid response). Score not affected.` | 0 |

All error cases exit with code 0 — automated grading is never blocked.

---

## SPEC.md Template (for each lab)

```markdown
---
artifact: notebook/walkthrough.ipynb
artifact_type: jupyter
max_score: 20
---

# AI Evaluation Rubric

## MCP Explanation (max: 5)
Must mention: server, client, stdio, and at least one of: subprocess, pipe, transport.

## ASCII Diagram (max: 5)
Must include 3 or more nodes (user/agent/server) and 2 or more labeled arrows.

## Error Trace (max: 5)
Must trace: SyntaxError to caught in handler to error dict to Claude to user explanation.

## Reflection (max: 5)
Minimum 2 sentences with rationale for proposed improvement.
```

**Schema contract (parsed by `ai_evaluator.py`):**
- YAML frontmatter: `artifact` (relative path from repo root), `artifact_type` (`jupyter` | `markdown` | `python`), `max_score` (integer).
- Criteria: headings matching `## Criterion Name (max: N)`. Body text under each heading becomes the rubric description passed to the model.

---

## Files to Create or Modify

### New files (in boilerplate)

| File | Notes |
|---|---|
| `templates/python-ai/.devcontainer/devcontainer.json` | Python 3.12 + GitHub Copilot extension |
| `templates/python-ai/.github/workflows/grade.yml` | Full grading + AI eval workflow |
| `templates/python-ai/.grader/ai_evaluator.py` | Evaluator script — reads SPEC.md + artifact, calls Portkey, writes ai-feedback.json |
| `templates/python-ai/.grader/SPEC.md` | Rubric template for instructors |
| `templates/python-ai/.grader/summarize.py` | Parses pytest JSON + ai-feedback.json, renders grader-report.md |
| `templates/python-ai/.grader/checks/test_structure.py` | Placeholder check file |
| `templates/python-ai/.grader/checks/test_execution.py` | Placeholder check file |
| `templates/python-ai/.grader/checks/test_quality.py` | Placeholder check file |
| `templates/python-ai/src/.gitkeep` | Starter code placeholder |
| `templates/python-ai/docs/instructions.md` | Blank exercise instructions |
| `templates/python-ai/requirements.txt` | pytest, pytest-asyncio, portkey-ai, python-frontmatter, pytest-json-report |
| `templates/python-ai/pytest.ini` | asyncio_mode = auto, testpaths = tests |
| `templates/python-ai/README.md` | Lab README template |

### Modified files (in boilerplate)

| File | Change |
|---|---|
| `docs/template-differences.md` | Add `python-ai` section with Python version override note |
| `docs/how-to-create-a-lab.md` | Add Step: configure SPEC.md for AI evaluation |
| `docs/grader-guide.md` | Add section: writing AI-evaluable specs |

---

## Success Criteria

- [ ] `new-lab.sh python-ai` creates a working lab directory with all files
- [ ] `pytest .grader/checks/` runs without errors on the blank template
- [ ] `ai_evaluator.py` with valid `PORTKEY_API_KEY` calls Portkey and writes valid `ai-feedback.json`
- [ ] `ai_evaluator.py` without `PORTKEY_API_KEY` writes `{"evaluated": false, ...}` and exits 0
- [ ] `summarize.py` produces a valid `grader-report.md` with and without AI feedback
- [ ] PR comment sticky update works on re-push
- [ ] Jupyter notebook cell extraction works (does not pass raw .ipynb JSON to model)
- [ ] Invalid JSON from model is retried once, then gracefully degraded
- [ ] All four error cases produce the specified comment strings and exit 0
- [ ] Python version override documented in `template-differences.md`
