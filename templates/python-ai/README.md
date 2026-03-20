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

Run the grader to see your starting score:

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

**Codespace won't start:** Try refreshing the page and creating a new Codespace. If the issue persists, contact your instructor.

**Import errors when running tests:** Make sure your source files have no syntax errors before running pytest.

**Need help?** Contact your instructor or post in the Academy support channel. <!-- TODO: add specific contact/channel -->
