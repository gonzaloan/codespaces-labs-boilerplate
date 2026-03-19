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
