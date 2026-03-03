# codespaces-lab-boilerplate

Boilerplate for creating educational labs that run on GitHub Codespaces.

## What's included

| Template | Language | Grader |
|---|---|---|
| `playwright` | TypeScript | Playwright Test |
| `python-ai` | Python 3.12 | pytest |

## Create a new lab

```bash
bash scripts/new-lab.sh
```

This copies a template into a new directory and initializes a git repo.

## Repository structure

```
templates/
├── playwright/    ← TypeScript + Playwright labs
└── python-ai/     ← Python AI labs (LangChain, OpenAI, Anthropic)
scripts/
└── new-lab.sh     ← lab generator
docs/
├── how-to-create-a-lab.md
├── grader-guide.md
└── template-differences.md
```

## How grading works

Each lab has a `.github/workflows/grade.yml` that:
1. Runs the grader on every pull request
2. Posts a score comment on the PR (with progress bar, hints, collapsible sections)
3. Uploads `grader-results.json` as an artifact

The grader uses the native test runner for each technology (Playwright or pytest).
