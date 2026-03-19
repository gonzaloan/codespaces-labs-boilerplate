# AI Review Universal + README Standardization — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add AI coaching feedback to all 4 templates (playwright, python-copilot, java-spring already have automated grading but no AI review), standardize student-facing README templates, and rewrite the boilerplate README as a comprehensive instructor guide.

**Architecture:** `ai_evaluator.py` (Python) is copied verbatim to all templates. Each template's report generator (`summarize.py` or `summarize.js`) reads `ai-feedback.json` and appends the AI coaching section. Non-Python templates add a `setup-python` step in `grade.yml` to run the evaluator — the student devcontainer language is unaffected.

**Tech Stack:** Python 3.12 (AI evaluator), Node.js (existing JS summarizers in playwright/java-spring), GitHub Actions, Portkey AI (claude-3-haiku-20240307)

**Pre-condition:** Branch `feat/python-ai-template` must be merged to `main` before starting. This plan starts from `main`.

---

### Task 1: Merge feat/python-ai-template and create new branch

**Files:** None

- [ ] **Step 1: Merge current branch to main**

```bash
cd C:/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate
git checkout main
git merge feat/python-ai-template
```

- [ ] **Step 2: Create new feature branch**

```bash
git checkout -b feat/ai-review-all-templates
```

- [ ] **Step 3: Verify tests still pass**

```bash
pytest tests/ -v
```
Expected: 27 passed

- [ ] **Step 4: Confirm branch state**

```bash
git log --oneline -5
git branch --show-current
```

---

### Task 2: Boilerplate README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read current README.md**

Read `README.md` to understand current content before rewriting.

- [ ] **Step 2: Rewrite README.md**

Replace the entire file with:

```markdown
# codespaces-lab-boilerplate

Boilerplate for creating educational labs that run on GitHub Codespaces. Includes automated grading and AI coaching feedback on every student Pull Request.

## Templates

| Template | Language | Grader | AI Review |
|---|---|---|---|
| `playwright` | TypeScript | Playwright Test | Yes |
| `python-ai` | Python 3.12 | pytest | Yes |
| `python-copilot` | Python 3.11 | pytest | Yes |
| `java-spring` | Java 21 | JUnit 5 via Maven | Yes |

## Create a new lab

```bash
bash scripts/new-lab.sh
```

Follow the prompts to select a template, name the lab, and choose an output directory. The script copies the template and initializes a git repository.

## Repository structure

```
templates/
├── playwright/         TypeScript + Playwright labs
├── python-ai/          Python AI labs (MCP, agents, notebooks)
├── python-copilot/     Python labs focused on Copilot workflows
└── java-spring/        Java Spring Boot labs
scripts/
└── new-lab.sh          Lab generator
docs/
├── how-to-create-a-lab.md
├── grader-guide.md
└── template-differences.md
```

## How grading works

Every template uses the same grading pipeline, triggered on every Pull Request:

```
Student opens PR
    -> automated checks run (pytest / Playwright / Maven)
    -> AI evaluator reads student artifact against SPEC.md rubric
    -> report combines automated score + AI coaching feedback
    -> sticky comment posted on PR (updates on re-push)
    -> grader-results.json + ai-feedback.json uploaded as artifacts
```

### Automated checks

Checks live in `.grader/checks/` (or `.grader/src/test/java/grader/` for Java). Each check is a test that validates one specific requirement. Checks are grouped into categories (Structure, Execution, Quality). Points are awarded proportionally within each category.

See `docs/grader-guide.md` for how to write checks.

### AI coaching feedback

The AI evaluator reads:
1. `.grader/SPEC.md` — the instructor-defined rubric with criteria and point values
2. The student artifact — a Jupyter notebook, Markdown file, or Python file

It calls Claude Haiku via Portkey and returns structured feedback per criterion:
- Strength — what the student did well, with specific references to their work
- Gap — what is missing or imprecise
- Action — one concrete thing to improve

The feedback is formative coaching. It does not affect the automated score.

To enable AI review, set `PORTKEY_API_KEY` as a repository or organization secret in GitHub. Students never configure this key. If it is not set, the PR comment shows a "not configured" notice and grading continues normally.

The only file the instructor edits to configure AI review is `.grader/SPEC.md`. See `docs/grader-guide.md` for the SPEC.md schema.

## Documentation

| Document | Audience | Content |
|---|---|---|
| `docs/how-to-create-a-lab.md` | Instructors | Step-by-step lab creation guide |
| `docs/grader-guide.md` | Instructors | Writing checks and configuring AI review |
| `docs/template-differences.md` | Instructors | Per-template technical reference |
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: rewrite boilerplate README as comprehensive instructor guide"
```

---

### Task 3: AI review for python-copilot template

**Files:**
- Create: `templates/python-copilot/.grader/ai_evaluator.py`
- Create: `templates/python-copilot/.grader/SPEC.md`
- Modify: `templates/python-copilot/requirements.txt`
- Modify: `templates/python-copilot/.grader/summarize.py`
- Modify: `templates/python-copilot/.github/workflows/grade.yml`
- Create: `tests/test_python_copilot_summarize.py`

**Note:** `ai_evaluator.py` is an exact copy of `templates/python-ai/.grader/ai_evaluator.py`. Do not modify it.

- [ ] **Step 1: Write failing test**

Create `tests/test_python_copilot_summarize.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "templates" / "python-copilot" / ".grader"))

from summarize import render_ai_section

SAMPLE_AI = {
    "evaluated": True,
    "artifact": "src/solution.py",
    "total_score": 8.0,
    "max_score": 10,
    "criteria": [
        {
            "name": "Code Quality",
            "score": 4.0,
            "max": 5,
            "strength": "Good variable names.",
            "gap": "Missing docstrings.",
            "action": "Add a docstring to each function.",
        },
        {
            "name": "Copilot Usage",
            "score": 4.0,
            "max": 5,
            "strength": "Evidence of Copilot in comments.",
            "gap": "No prompt engineering shown.",
            "action": "Include one example of a Copilot prompt you refined.",
        },
    ],
    "summary": "Strong start. Focus on documentation next.",
}


def test_render_ai_section_shows_score():
    result = render_ai_section(SAMPLE_AI)
    assert "8.0 / 10" in result


def test_render_ai_section_has_disclaimer():
    result = render_ai_section(SAMPLE_AI)
    assert "not included in your automated score" in result


def test_render_ai_section_summary_before_criteria():
    result = render_ai_section(SAMPLE_AI)
    summary_pos = result.index("Strong start")
    details_pos = result.index("<details")
    assert summary_pos < details_pos, "Summary must appear before criteria details"


def test_render_ai_section_first_criterion_open():
    result = render_ai_section(SAMPLE_AI)
    assert "<details open>" in result


def test_render_ai_section_not_configured():
    result = render_ai_section({"evaluated": False, "reason": "AI Review: not configured."})
    assert "not configured" in result
    assert "<details" not in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_python_copilot_summarize.py -v
```
Expected: ImportError or AttributeError — `render_ai_section` not defined yet.

- [ ] **Step 3: Copy ai_evaluator.py verbatim**

Read `templates/python-ai/.grader/ai_evaluator.py` in full, then write it to `templates/python-copilot/.grader/ai_evaluator.py` with identical content.

- [ ] **Step 4: Create SPEC.md**

Create `templates/python-copilot/.grader/SPEC.md`:

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

- [ ] **Step 5: Add portkey-ai and python-frontmatter to requirements.txt**

Read `templates/python-copilot/requirements.txt`, then append two lines:
```
portkey-ai>=1,<2
python-frontmatter>=1,<2
```

- [ ] **Step 6: Add render_ai_section to summarize.py**

Read `templates/python-copilot/.grader/summarize.py` in full.

Add this function before the final report-writing block (before the `md = "## Lab Grader Results"` line or equivalent):

```python
def render_ai_section(ai: dict) -> str:
    """Render the AI Review section of the PR comment."""
    if not ai.get("evaluated"):
        reason = ai.get("reason", "AI Review: not configured.")
        return f"\n---\n\n> {reason}\n\n"

    import os as _os
    artifact = ai.get("artifact", "")
    artifact_label = _os.path.basename(artifact) if artifact else "artifact"
    total = ai.get("total_score", 0)
    max_s = ai.get("max_score", 0)

    md = f"\n---\n\n### AI Review — {artifact_label}   {total} / {max_s}\n\n"
    md += "> *Coaching feedback — not included in your automated score.*\n\n"
    summary = ai.get("summary", "")
    if summary:
        md += f"> **Overall:** {summary}\n\n"
    for i, criterion in enumerate(ai.get("criteria", [])):
        open_attr = " open" if i == 0 else ""
        md += f"<details{open_attr}>\n"
        md += f"<summary><b>{criterion['name']}</b> — {criterion['score']} / {criterion['max']}</summary>\n\n"
        md += f"**Strength:** {criterion.get('strength', '')}\n\n"
        md += f"**Gap:** {criterion.get('gap', '')}\n\n"
        md += f"**Action:** {criterion.get('action', '')}\n\n"
        md += "</details>\n\n"
    return md
```

Then, just before writing `OUT_MD`, add:

```python
import json as _json
_ai_path = os.path.join(ROOT, "ai-feedback.json")
_ai_data = (
    _json.loads(open(_ai_path).read())
    if os.path.exists(_ai_path)
    else {"evaluated": False, "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable."}
)
md += render_ai_section(_ai_data)
```

- [ ] **Step 7: Update grade.yml**

Read `templates/python-copilot/.github/workflows/grade.yml`. Insert after the "Run grader" step:

```yaml
      - name: Run AI evaluator
        run: python .grader/ai_evaluator.py
        env:
          PORTKEY_API_KEY: ${{ secrets.PORTKEY_API_KEY }}
        continue-on-error: true
```

Update the upload-artifact `path` block to include `ai-feedback.json`:

```yaml
          path: |
            grader-results.json
            ai-feedback.json
```

- [ ] **Step 8: Run tests**

```bash
pytest tests/test_python_copilot_summarize.py tests/test_ai_evaluator.py tests/test_summarize.py -v
```
Expected: all passing (27 + 5 = 32 total).

- [ ] **Step 9: Commit**

```bash
git add templates/python-copilot/ tests/test_python_copilot_summarize.py
git commit -m "feat: add AI review to python-copilot template"
```

---

### Task 4: AI review for playwright template

**Files:**
- Create: `templates/playwright/.grader/ai_evaluator.py`
- Create: `templates/playwright/.grader/SPEC.md`
- Create: `templates/playwright/.grader/requirements-ai.txt`
- Modify: `templates/playwright/.grader/summarize.js`
- Modify: `templates/playwright/.github/workflows/grade.yml`

- [ ] **Step 1: Copy ai_evaluator.py verbatim**

Read `templates/python-ai/.grader/ai_evaluator.py`, write to `templates/playwright/.grader/ai_evaluator.py` with identical content.

- [ ] **Step 2: Create SPEC.md**

Create `templates/playwright/.grader/SPEC.md` with same content as python-copilot's SPEC.md.

- [ ] **Step 3: Create requirements-ai.txt**

Create `templates/playwright/.grader/requirements-ai.txt`:

```
portkey-ai>=1,<2
python-frontmatter>=1,<2
```

- [ ] **Step 4: Add renderAiSection to summarize.js**

Read `templates/playwright/.grader/summarize.js` in full.

Add this function in the helpers section (after `catIcon`):

```javascript
function renderAiSection(ai) {
    if (!ai.evaluated) {
        const reason = ai.reason || 'AI Review: not configured.';
        return `\n---\n\n> ${reason}\n\n`;
    }
    const artifactLabel = path.basename(ai.artifact || 'artifact');
    const total = ai.total_score ?? 0;
    const maxS = ai.max_score ?? 0;
    let md = `\n---\n\n### AI Review — ${artifactLabel}   ${total} / ${maxS}\n\n`;
    md += '> *Coaching feedback — not included in your automated score.*\n\n';
    const summary = ai.summary || '';
    if (summary) {
        md += `> **Overall:** ${summary}\n\n`;
    }
    const criteria = ai.criteria || [];
    criteria.forEach((criterion, i) => {
        const openAttr = i === 0 ? ' open' : '';
        md += `<details${openAttr}>\n`;
        md += `<summary><b>${criterion.name}</b> — ${criterion.score} / ${criterion.max}</summary>\n\n`;
        md += `**Strength:** ${criterion.strength || ''}\n\n`;
        md += `**Gap:** ${criterion.gap || ''}\n\n`;
        md += `**Action:** ${criterion.action || ''}\n\n`;
        md += '</details>\n\n';
    });
    return md;
}
```

Just before the final `fs.writeFileSync(OUT_MD, md)` line, add:

```javascript
const aiFile = path.join(ROOT, 'ai-feedback.json');
let ai = { evaluated: false, reason: 'AI Review: not configured — set PORTKEY_API_KEY to enable.' };
if (fs.existsSync(aiFile)) {
    try { ai = JSON.parse(fs.readFileSync(aiFile, 'utf-8')); } catch (_) {}
}
md += renderAiSection(ai);
```

- [ ] **Step 5: Update grade.yml**

Read `templates/playwright/.github/workflows/grade.yml`. After the "Run grader" step, add:

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install AI evaluator dependencies
        run: pip install -r .grader/requirements-ai.txt

      - name: Run AI evaluator
        run: python .grader/ai_evaluator.py
        env:
          PORTKEY_API_KEY: ${{ secrets.PORTKEY_API_KEY }}
        continue-on-error: true
```

Update upload-artifact `path` to include `ai-feedback.json`:

```yaml
          path: |
            grader-results.json
            ai-feedback.json
```

- [ ] **Step 6: Smoke test summarize.js**

```bash
cd C:/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/playwright
echo '{"suites":[]}' > grader-results-raw.json
echo '{"evaluated":false,"reason":"AI Review: not configured."}' > ai-feedback.json
node .grader/summarize.js
grep -q "not configured" grader-report.md && echo "PASS" || echo "FAIL"
rm grader-results-raw.json ai-feedback.json grader-results.json grader-report.md
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
cd C:/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate
git add templates/playwright/
git commit -m "feat: add AI review to playwright template"
```

---

### Task 5: AI review for java-spring template

**Files:**
- Create: `templates/java-spring/.grader/ai_evaluator.py`
- Create: `templates/java-spring/.grader/SPEC.md`
- Create: `templates/java-spring/.grader/requirements-ai.txt`
- Modify: `templates/java-spring/.grader/summarize.js`
- Modify: `templates/java-spring/.github/workflows/grade.yml`

Same pattern as Task 4. Key difference: `summarize.js` reads Surefire XML (not JSON) and has a different structure. The AI section is appended identically.

- [ ] **Step 1: Copy ai_evaluator.py verbatim**

Read `templates/python-ai/.grader/ai_evaluator.py`, write to `templates/java-spring/.grader/ai_evaluator.py` with identical content.

- [ ] **Step 2: Create SPEC.md**

Create `templates/java-spring/.grader/SPEC.md` with same content as python-copilot's SPEC.md.

- [ ] **Step 3: Create requirements-ai.txt**

Create `templates/java-spring/.grader/requirements-ai.txt`:
```
portkey-ai>=1,<2
python-frontmatter>=1,<2
```

- [ ] **Step 4: Add renderAiSection to summarize.js**

Read `templates/java-spring/.grader/summarize.js` in full.

Add the `renderAiSection(ai)` function (identical to playwright's) in the helpers section at the bottom (after `hasFiles`).

Just before the final `fs.writeFileSync(OUT_MD, md)` line, add the same `aiFile` + `renderAiSection(ai)` block as playwright.

- [ ] **Step 5: Update grade.yml**

Read `templates/java-spring/.github/workflows/grade.yml`. After the "Run grader" step, add the same 3 Python steps as playwright.

Update upload-artifact to include `ai-feedback.json`.

- [ ] **Step 6: Smoke test summarize.js**

```bash
cd C:/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/java-spring
mkdir -p .grader/target/surefire-reports
echo '{"evaluated":false,"reason":"AI Review: not configured."}' > ai-feedback.json
node .grader/summarize.js 2>&1
grep -q "not configured" grader-report.md && echo "PASS" || echo "FAIL"
rm -rf .grader/target ai-feedback.json grader-results.json grader-report.md
```
Expected: PASS (note: may print "no surefire reports" warning — that is acceptable)

- [ ] **Step 7: Commit**

```bash
cd C:/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate
git add templates/java-spring/
git commit -m "feat: add AI review to java-spring template"
```

---

### Task 6: Standardize template READMEs

**Files:**
- Modify: `templates/playwright/README.md`
- Modify: `templates/java-spring/README.md`
- Modify: `templates/python-copilot/README.md`
- Modify: `templates/python-ai/README.md`

All template READMEs are student-facing. They get copied into each lab repo. The instructor fills in TODO markers. The reference standard is `templates/python-copilot/README.md`.

- [ ] **Step 1: Read all four READMEs**

Read each file before rewriting.

- [ ] **Step 2: Rewrite playwright/README.md**

Match the structure of `python-copilot/README.md` exactly. Adjust for TypeScript/Playwright:
- Setup: `npm install` + `npx playwright install --with-deps chromium`
- Run: `npm test`
- Grading: mention automated checks + AI coaching feedback
- Troubleshooting: Playwright-specific items (browser not found, Codespace memory)

- [ ] **Step 3: Rewrite java-spring/README.md**

Same structure. Adjust for Java/Maven:
- Setup: requires JDK 21 + Maven, run `mvn dependency:resolve`
- Run: `mvn test`
- Grading: mention automated checks + AI coaching feedback
- Troubleshooting: Java/Maven-specific items

- [ ] **Step 4: Update python-copilot/README.md**

In the "How the grader works" section, add after the existing pipeline description:

```markdown
If your instructor has configured AI review, you will also receive coaching feedback on your submitted artifact — what you did well, what is missing, and one specific action to improve. This feedback is formative and does not affect your automated score.
```

- [ ] **Step 5: Update python-ai/README.md**

Read current content. Verify the Grading section mentions AI coaching feedback. If not, add the same sentence as Step 4.

- [ ] **Step 6: Run tests**

```bash
pytest tests/ -v
```
Expected: all passing.

- [ ] **Step 7: Commit**

```bash
git add templates/playwright/README.md templates/java-spring/README.md templates/python-copilot/README.md templates/python-ai/README.md
git commit -m "docs: standardize student-facing README templates"
```

---

### Task 7: Update docs/template-differences.md

**Files:**
- Modify: `docs/template-differences.md`

- [ ] **Step 1: Read current template-differences.md**

Read the file in full.

- [ ] **Step 2: Rewrite with all 4 templates + AI review**

The updated file must:
1. Add "AI review" to the "What's the same" section at the top
2. Add a `python-copilot` section (currently missing)
3. Add an "AI evaluator" row to every template's table

python-copilot section to add:

```markdown
## python-copilot

| | |
|---|---|
| Language | Python 3.11 |
| Runner | pytest + pytest-json-report |
| Grade command | `pytest .grader/checks/ --json-report --json-report-file=grader-results-raw.json` |
| Checks location | `.grader/checks/test_*.py` |
| Report input | `grader-results-raw.json` + `ai-feedback.json` |
| Report script | `.grader/summarize.py` |
| Category = | Class name inside check file (e.g. `class Structure:`) |
| Check = | Method name (e.g. `def test_file_exists`) |
| Hint = | Assertion message |
| AI evaluator | `.grader/ai_evaluator.py` + `.grader/SPEC.md` |
| PR trigger | `feedback` branch (not `main`) |
| Python version | 3.11 default. Override in `devcontainer.json` if needed. |
```

Add AI evaluator row to playwright, java-spring, and python-ai sections:
```
| AI evaluator | .grader/ai_evaluator.py + .grader/SPEC.md |
```

- [ ] **Step 3: Commit**

```bash
git add docs/template-differences.md
git commit -m "docs: add python-copilot section and AI review rows to template-differences.md"
```

---

### Final verification

- [ ] **Run full test suite**

```bash
pytest tests/ -v
```
Expected: 32 passing (27 original + 5 python-copilot render_ai_section tests).

- [ ] **Check all 4 templates have AI evaluator files**

```bash
find templates -name "ai_evaluator.py" | sort
find templates -name "SPEC.md" | sort
```
Expected: 4 of each.

- [ ] **Check all 4 grade.yml files reference AI evaluator**

```bash
grep -l "ai_evaluator.py" templates/*/\.github/workflows/grade.yml
```
Expected: 4 files.

- [ ] **Use superpowers:finishing-a-development-branch to complete**
