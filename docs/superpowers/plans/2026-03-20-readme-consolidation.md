# README Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate all student-facing content into README.md across the L1 assignment repo and all 4 boilerplate templates, eliminating docs/instructions.md from the student flow.

**Architecture:** Each lab repo's README becomes the single source of truth. The boilerplate templates gain a `## Tasks` section with instructor TODOs. `docs/instructions.md` is deleted everywhere. `how-to-create-a-lab.md` updated to point instructors to README.

**Tech Stack:** Markdown, Git

---

## File Map

### assignment-l1-dev-ai-assisted
| File | Action |
|---|---|
| `README.md` | Rewrite — merge current README + docs/instructions.md content |
| `docs/instructions.md` | Delete |

### codespaces-lab-boilerplate
| File | Action |
|---|---|
| `templates/python-ai/README.md` | Rewrite — adopt rich structure + Tasks TODO |
| `templates/python-ai/docs/instructions.md` | Delete |
| `templates/python-copilot/README.md` | Update — replace "Read instructions.md" step with Tasks TODO |
| `templates/python-copilot/docs/instructions.md` | Delete |
| `templates/playwright/README.md` | Update — same as python-copilot |
| `templates/playwright/docs/instructions.md` | Delete |
| `templates/java-spring/README.md` | Update — same as python-copilot |
| `templates/java-spring/docs/instructions.md` | Delete |
| `docs/how-to-create-a-lab.md` | Update step 2 |

---

## Task 1: Rewrite L1 assignment README

**Files:**
- Modify: `assignment-l1-dev-ai-assisted/README.md`
- Delete: `assignment-l1-dev-ai-assisted/docs/instructions.md`

- [ ] **Step 1: Rewrite README.md with full content**

Replace the entire file with:

```markdown
# Legacy Rescue Sprint

**Perficient Global AI Academy · PATH A · Level 1 · ~60–90 min**

---

## The scenario

You've just joined a Perficient project mid-sprint. The previous developer left a half-built Python module — `src/data_processor.py` — that is part of the Acme Corp Q2 sales analytics pipeline.

The handover notes say:
- 2 functions are stubbed (not implemented)
- 3 functions have bugs
- 1 function works but was rejected in code review for poor readability

Your job: bring it to production-ready using your AI assistant of choice — Claude Code, ChatGPT, Cursor, Copilot, or any other tool.

---

## Before you start

### Open your Codespace

Click the green **"Code"** button at the top of this page → **"Codespaces"** tab → **"Create codespace on main"**.

> The environment configures itself automatically in ~60 seconds. Python 3.12 and all dependencies are pre-installed.

### Verify your starting state

```bash
pytest .grader/checks/ tests/ -v
```

Everything will fail — that is intentional. Your goal is to reach **70% or higher**.

---

## Tasks

### Task 1 — Understand the legacy code with AI (~10–15 min)

Before changing anything, use your AI assistant to understand what the module does.

**What to do:**
- Show your AI the full contents of `src/data_processor.py`
- Ask it to explain each function, identify the stubs, and describe what the bugs likely are
- Do not apply any changes yet — this task is about building understanding

**What to capture in REFLECTION.md:**
- Which AI tool you used
- The exact prompt (or a close paraphrase) you gave it
- The most useful or surprising insight it gave you about the code

---

### Task 2 — Complete the stubbed functions with AI (~10–15 min)

Two functions have only a comment and `pass`. Use your AI to implement them.

**Functions to complete:**
- `parse_csv_row(row)` — splits a CSV string into a clean list
- `filter_records(records, field, value)` — filters a list of dicts by a field value

**How to approach this:**
1. Show the stub to your AI and ask it to implement it based on the comment
2. Evaluate whether the suggestion is correct before applying it
3. Run the tests to verify: `pytest tests/ -v`
4. If it fails, refine your prompt and try again

**What to capture in REFLECTION.md:**
- Whether your first prompt produced a working implementation, or if you had to iterate

---

### Task 3 — Fix the 3 bugs with AI (~15–20 min)

Three functions have intentional bugs. Use your AI to diagnose and fix them.

**Functions with bugs:**
- `calculate_average(values)` — returns wrong results
- `normalize_score(score, min_val, max_val)` — formula is incorrect
- `format_summary(name, scores)` — raises a NameError

**How to approach this:**
1. Ask your AI to explain what each function does and whether it sees any issues
2. Try to understand the root cause before applying a fix
3. Fix the bug and run the tests to confirm it is resolved

**What to capture in REFLECTION.md:**
- For at least 2 of the 3 bugs: what prompt led to finding it, and whether the AI explained the root cause or just gave you a fix

---

### Task 4 — Generate tests with AI (~10–15 min)

Open `tests/test_data_processor.py` and write tests for all 6 functions using your AI.

**Requirements:**
- At least one test per function (6 functions = minimum 6 tests)
- Replace all `pass` placeholders in `tests/test_data_processor.py`
- Tests must pass after you have fixed all bugs and completed all stubs

**How to approach this:**
- Ask your AI: *"Write pytest tests for the functions in data_processor.py"*
- Or ask for specific edge cases: *"What edge cases should I test for calculate_average?"*

```bash
pytest tests/ -v
```

**What to capture in REFLECTION.md:**
- Whether the AI suggested edge cases you had not considered
- Whether any AI-generated tests failed, and why

---

### Task 5 — Refactor with AI (~5–10 min)

The function `get_top_performers(r, n)` works correctly but was rejected in code review for poor readability.

**How to approach this:**
1. Show the function to your AI
2. Ask it: *"Refactor this function. Add type hints and make it Pythonic."*
3. Review the suggestion — do you understand every change it made?
4. Apply the refactor and verify your tests still pass

**What good looks like:** typed parameters, a docstring, list comprehensions or `sorted()` instead of manual loops.

**What to capture in REFLECTION.md:**
- Whether you accepted the suggestion as-is or modified it, and why

---

### Task 6 — Add docstrings and type hints with AI (~5–10 min)

Every function in `data_processor.py` must have a **docstring** and **type hints** before submitting. This is graded automatically — no REFLECTION.md entry required.

**How to approach this:**
- Ask your AI: *"Add a docstring and type hints to this function"*
- Or show it the whole module: *"Add docstrings and type hints to all functions in this file"*

**What is checked:**
- Every function has a docstring (non-empty string as first statement)
- Every function has a return type annotation (`-> type`)

---

### Task 7 — Fill in REFLECTION.md (~10–15 min)

Open `REFLECTION.md` and replace every `...your answer here...` with your actual answers.

Write at least 2–3 sentences per section. Vague or one-line answers score low on the AI coaching rubric.

**This is graded** — the file must be complete (no placeholders, at least 200 words) before you submit.

---

## Grading

| Category | Points | What is checked |
|---|---|---|
| Structure | 6 | Required files exist, stubs implemented, tests have content (≥6 methods) |
| Execution | 15 | All 6 functions return correct results |
| Quality | 4 | Every function has a docstring and return type annotation |
| StudentWork | 4 | REFLECTION.md: all 6 sections filled, ≥200 words, no placeholders |
| **Total** | **29** | |

**Minimum to pass: 21/29 pts (70%)**

You also receive **AI coaching feedback** on your REFLECTION.md — formative (25 pts), not counted in your automated score.

---

## How to submit

1. Make sure all your work is committed
2. Open a **Pull Request from your branch to `main`**
3. The grader runs automatically and posts a score comment on the PR
4. You need **21/29 pts (70%)** to pass
5. You can push additional commits to improve your score — the comment updates automatically

---

## Tips & Troubleshooting

**Stuck on a function?** Ask your AI: *"What should this function do based on the comment?"*

**Bug not obvious?** Ask: *"Walk me through this function step by step and tell me if anything looks wrong"*

**Tests failing?** Ask: *"Why is this test failing? Here is the error: [paste error]"*

**Run the grader locally** before opening a PR:
```bash
pytest .grader/checks/ tests/ -v
```

**Codespace takes too long to start:** Wait up to 2 minutes.

**Import errors when running tests:** Make sure `src/data_processor.py` has no syntax errors before running pytest.

**REFLECTION.md checks failing:** Replace every `...your answer here...` placeholder and write at least 200 words total.
```

- [ ] **Step 2: Delete docs/instructions.md**

```bash
cd /c/Users/gonzalo.munoz/WebstormProjects/assignment-l1-dev-ai-assisted
rm docs/instructions.md
```

- [ ] **Step 3: Verify the docs/ folder is now empty except for the superpowers dir**

```bash
ls docs/
```

Expected: only `superpowers/` (or empty if no superpowers dir)

- [ ] **Step 4: Commit**

```bash
git add README.md docs/instructions.md
git commit -m "docs: consolidate instructions into README, remove docs/instructions.md"
```

- [ ] **Step 5: Push**

```bash
git push origin main
```

---

## Task 2: Rewrite python-ai template README

**Files:**
- Modify: `codespaces-lab-boilerplate/templates/python-ai/README.md`
- Delete: `codespaces-lab-boilerplate/templates/python-ai/docs/instructions.md`

- [ ] **Step 1: Rewrite templates/python-ai/README.md**

Replace the entire file with (matches python-copilot structure + Tasks TODO):

```markdown
# [LAB TITLE] <!-- TODO: replace with lab name, e.g. "Legacy Rescue Sprint" -->

**Perficient Global AI Academy** · [PATH NAME] · Level [N] <!-- TODO: replace path and level -->

---

<!-- TODO: replace with a 1-2 sentence description of the scenario -->
> [Short scenario description — what is the student's mission?]

| | |
|---|---|
| **Estimated time** | [X–Y minutes] <!-- TODO --> |
| **Minimum passing score** | 70% |
| **Platform** | GitHub Codespaces |

---

## How to start

### 1 — Open your Codespace

Click the green **"Code"** button at the top of this page, select the **"Codespaces"** tab, then click **"Create codespace on main"**.

> The environment will take about 60 seconds to set up. Everything is pre-installed — Python and all dependencies.

### 2 — Verify your starting state

```bash
pytest .grader/checks/ tests/ -v
```

Everything will fail — that is intentional. Your goal is to reach 70% or higher.

---

## Tasks

<!--
TODO: Define each task using this format:

### Task N — [Name] (~X min)

[What the student does. 2–3 sentences describing the goal and approach.]

**What to capture in REFLECTION.md:** [What they document, or "No REFLECTION entry required for this task."]

---

Repeat for each task.
-->

---

## Grading

<!--
TODO: Fill in the grading table.

| Category | Points | What is checked |
|---|---|---|
| Structure | X | [what is validated] |
| Execution | X | [what is validated] |
| Quality | X | [what is validated] |
| StudentWork | X | [what is validated] |
| **Total** | **XX** | |

**Minimum to pass: XX/XX pts (70%)**
-->

The grader runs automatically on every push and posts a score comment with automated test results broken down by category.

If your instructor has configured AI review, you will also receive coaching feedback on your submitted artifact — what you did well, what is missing, and one specific action to improve. This feedback is formative and does not affect your automated score.

---

## How to submit

1. Make sure all your work is committed
2. Open a **Pull Request from your branch to `main`**
3. The grader runs automatically and posts a score comment on the PR
4. You can push additional commits to improve your score — the comment updates automatically

---

## Tips & Troubleshooting

<!--
TODO: Add lab-specific tips and common troubleshooting scenarios.

**[Common issue]:** [How to resolve it]
-->

**Codespace won't start:** Try refreshing the page and creating a new Codespace.

**Import errors when running tests:** Make sure your source files have no syntax errors before running pytest.

**Need help?** Contact your instructor or post in the Academy support channel. <!-- TODO: add specific contact/channel -->
```

- [ ] **Step 2: Delete templates/python-ai/docs/instructions.md**

```bash
rm /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/python-ai/docs/instructions.md
```

- [ ] **Step 3: Check if docs/ folder in python-ai is now empty**

```bash
ls /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/python-ai/docs/ 2>/dev/null || echo "empty or gone"
```

If empty, remove the folder too:
```bash
rmdir /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/python-ai/docs/
```

---

## Task 3: Update python-copilot template README

**Files:**
- Modify: `codespaces-lab-boilerplate/templates/python-copilot/README.md`
- Delete: `codespaces-lab-boilerplate/templates/python-copilot/docs/instructions.md`

The python-copilot README is already rich. Changes needed:
1. Replace the "How to start" step 2 ("Read docs/instructions.md") and step 3 ("work on solution, see docs/instructions.md") with a `## Tasks` TODO section
2. Remove the `## How to start` 4-step list structure and simplify to Codespace open + verify state (matching the new standard)

- [ ] **Step 1: Update the "How to start" section**

Find and replace in `templates/python-copilot/README.md`:

Old:
```markdown
### 2 — Read the instructions

Open `docs/instructions.md` in the Codespace for the full exercise guide with step-by-step tasks.

### 3 — Work on your solution

All your code goes in the `src/` folder. See `docs/instructions.md` for details on each task.

### 4 — Check your score

Push your changes to `main` — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

New:
```markdown
### 2 — Verify your starting state

```bash
pytest .grader/checks/ tests/ -v
```

Everything will fail — that is intentional. Your goal is to reach 70% or higher.

### 3 — Check your score after working

Push your changes — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

- [ ] **Step 2: Add Tasks section after "How to start"**

Insert after the `## How to start` section and before `## How the grader works`:

```markdown
---

## Tasks

<!--
TODO: Define each task using this format:

### Task N — [Name] (~X min)

[What the student does. 2–3 sentences describing the goal and approach.]

**What to capture in REFLECTION.md:** [What they document, or "No REFLECTION entry required for this task."]

---

Repeat for each task.
-->

```

- [ ] **Step 3: Delete docs/instructions.md**

```bash
rm /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/python-copilot/docs/instructions.md
rmdir /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/python-copilot/docs/ 2>/dev/null || true
```

---

## Task 4: Update playwright template README

**Files:**
- Modify: `codespaces-lab-boilerplate/templates/playwright/README.md`
- Delete: `codespaces-lab-boilerplate/templates/playwright/docs/instructions.md`

Same changes as Task 3, adapted for playwright (Node.js, not Python).

- [ ] **Step 1: Update the "How to start" section**

Find and replace in `templates/playwright/README.md`:

Old:
```markdown
### 2 — Read the instructions

Open `docs/instructions.md` in the Codespace for the full exercise guide with step-by-step tasks.

### 3 — Work on your solution

All your code goes in the `src/` folder. See `docs/instructions.md` for details on each task.

### 4 — Check your score

Push your changes to `main` — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

New:
```markdown
### 2 — Verify your starting state

```bash
npm test
```

Everything will fail — that is intentional. Your goal is to reach 70% or higher.

### 3 — Check your score after working

Push your changes — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

- [ ] **Step 2: Add Tasks section after "How to start"**

Same Tasks TODO block as Task 3.

- [ ] **Step 3: Delete docs/instructions.md**

```bash
rm /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/playwright/docs/instructions.md
rmdir /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/playwright/docs/ 2>/dev/null || true
```

---

## Task 5: Update java-spring template README

**Files:**
- Modify: `codespaces-lab-boilerplate/templates/java-spring/README.md`
- Delete: `codespaces-lab-boilerplate/templates/java-spring/docs/instructions.md`

Same changes as Task 3, adapted for java-spring (Maven).

- [ ] **Step 1: Update the "How to start" section**

Find and replace in `templates/java-spring/README.md`:

Old:
```markdown
### 2 — Read the instructions

Open `docs/instructions.md` in the Codespace for the full exercise guide with step-by-step tasks.

### 3 — Work on your solution

All your code goes in `src/main/java/`. See `docs/instructions.md` for details on each task.

### 4 — Check your score

Push your changes to `main` — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

New:
```markdown
### 2 — Verify your starting state

```bash
mvn test
```

Everything will fail — that is intentional. Your goal is to reach 70% or higher.

### 3 — Check your score after working

Push your changes — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.
```

- [ ] **Step 2: Add Tasks section after "How to start"**

Same Tasks TODO block as Task 3.

- [ ] **Step 3: Delete docs/instructions.md**

```bash
rm /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/java-spring/docs/instructions.md
rmdir /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate/templates/java-spring/docs/ 2>/dev/null || true
```

---

## Task 6: Update how-to-create-a-lab.md + commit boilerplate

**Files:**
- Modify: `codespaces-lab-boilerplate/docs/how-to-create-a-lab.md`

- [ ] **Step 1: Update step 2**

Find and replace:

Old:
```markdown
### 2. Define the exercise

Edit `docs/instructions.md` — describe what the student has to build, the requirements, and any useful resources.
```

New:
```markdown
### 2. Define the exercise

Edit `README.md` — fill in the `## The scenario` section and the `## Tasks` section.

Each task should follow this format:

```markdown
### Task N — [Name] (~X min)

[What the student does. 2–3 sentences.]

**What to capture in REFLECTION.md:** [What they document, or "No entry required."]
```

The `## Grading`, `## Tips & Troubleshooting` sections also need to be filled in.
`docs/instructions.md` does not exist in the template — README is the single source of truth.
```

- [ ] **Step 2: Commit all boilerplate changes**

```bash
cd /c/Users/gonzalo.munoz/WebstormProjects/codespaces-lab-boilerplate
git add templates/python-ai/README.md
git add templates/python-copilot/README.md
git add templates/playwright/README.md
git add templates/java-spring/README.md
git add templates/python-ai/docs/
git add templates/python-copilot/docs/
git add templates/playwright/docs/
git add templates/java-spring/docs/
git add docs/how-to-create-a-lab.md
git add docs/superpowers/specs/2026-03-20-readme-consolidation-design.md
git add docs/superpowers/plans/2026-03-20-readme-consolidation.md
git commit -m "docs: consolidate student instructions into README across all templates

- Rewrite python-ai README to match rich template structure
- Add ## Tasks section with instructor TODOs to all 4 templates
- Remove docs/instructions.md from all templates (README is single source of truth)
- Update how-to-create-a-lab.md: step 2 now points to README ## Tasks"
```

- [ ] **Step 3: Push boilerplate**

```bash
git push origin main
```

---

## Verification Checklist

- [ ] `assignment-l1-dev-ai-assisted/README.md` — open in browser, all 7 tasks visible without clicking any link
- [ ] `assignment-l1-dev-ai-assisted/docs/instructions.md` — file does not exist
- [ ] `templates/python-ai/README.md` — has same section structure as python-copilot
- [ ] `templates/python-copilot/README.md` — has `## Tasks` TODO block, no reference to instructions.md
- [ ] `templates/playwright/README.md` — same
- [ ] `templates/java-spring/README.md` — same
- [ ] None of the 4 templates have a `docs/instructions.md`
- [ ] `how-to-create-a-lab.md` step 2 references README, not instructions.md
- [ ] Both repos pushed to origin/main
