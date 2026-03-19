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

## Deploying a lab to GitHub Classroom

### 1. Push the lab repo to GitHub and mark it as a template

In the repo settings → check **"Template repository"**.

### 2. Create the assignment in GitHub Classroom

- Starter code: select your lab repo
- Repository visibility: **Private**
- Grant admin access: **No**
- Copy default branch only: **Yes**
- Editor: **GitHub Codespaces**
- Feedback pull requests: **Enable** (students push to `main` — grader runs automatically via feedback PR, no manual PR creation needed)

### 3. Add autograding tests (manual — UI does not auto-import from repo)

Add one test of type **"Run command"** per category. Example for `python-ai` labs:

| Name | Setup | Run | Points | Timeout |
|---|---|---|---|---|
| `Structure` | `pip install -r requirements.txt` | `pytest .grader/checks/test_structure.py` | 6 | 10 |
| `Execution` | `pip install -r requirements.txt` | `pytest .grader/checks/test_execution.py` | 15 | 10 |
| `Quality` | `pip install -r requirements.txt` | `pytest .grader/checks/test_quality.py` | 4 | 10 |
| `StudentWork` | `pip install -r requirements.txt` | `pytest .grader/checks/test_student_work.py` | 4 | 10 |

For `playwright` and `java-spring` labs, see the `autograding.json` in `.github/classroom/` of the respective template for the exact commands and point values.

> Classroom autograding is binary per category (all-or-nothing per file). The PR comment from `grade.yml` shows proportional partial credit. Both run — they serve different purposes: Classroom = CSV metrics dashboard, `grade.yml` = student feedback.

### 4. Set PORTKEY_API_KEY as an organization secret

Required for AI coaching feedback:

- GitHub org → **Settings → Secrets and variables → Actions → New organization secret**
- Name: `PORTKEY_API_KEY`
- Access: All repositories (or scoped to classroom repos)

If not set, grading continues normally — PR comment shows "AI Review: not configured."

### 5. Add protected file paths (recommended)

In Classroom assignment settings:
```
.github/**/*
.grader/**/*
```

### 6. CSV export

Once students submit, download results from:
**GitHub Classroom dashboard → your assignment → Download grades (CSV)**

Each row = one student. Columns: GitHub username + one column per autograding test (pts earned).

---

## Documentation

| Document | Audience | Content |
|---|---|---|
| `docs/how-to-create-a-lab.md` | Instructors | Step-by-step lab creation guide |
| `docs/grader-guide.md` | Instructors | Writing checks, configuring AI review, GitHub Classroom setup |
| `docs/template-differences.md` | Instructors | Per-template technical reference |
