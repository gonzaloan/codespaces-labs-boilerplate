# python-copilot template

Template for Python labs that run on GitHub Codespaces with GitHub Copilot enabled.

## What's included

| File | Purpose |
|---|---|
| `.devcontainer/devcontainer.json` | Python 3.11 + Copilot + Black formatter |
| `.github/workflows/grade.yml` | Auto-grades every PR and posts score as a comment |
| `.grader/summarize.py` | Converts pytest output to `grader-results.json` + PR comment |
| `.grader/checks/test_structure.py` | Validates that expected files exist in `src/` |
| `.grader/checks/test_execution.py` | Validates that functions exist and return correct results |
| `.grader/checks/test_quality.py` | Validates docstrings and type hints |
| `src/` | Where the student writes their solution |
| `docs/instructions.md` | Lab instructions shown to the student |
| `requirements.txt` | Runtime dependencies for the lab |
| `requirements-dev.txt` | Grader dependencies — do not modify |

## How to create a lab from this template

1. Copy this directory into a new repo
2. Edit `docs/instructions.md` with your exercise description
3. Add any runtime packages to `requirements.txt`
4. Replace the placeholder in `.grader/checks/test_execution.py` with your actual checks
5. Add starter code or empty stubs in `src/` if needed

## How grading works

On every pull request to `main`:

1. GitHub Actions installs dependencies and runs `pytest .grader/checks/`
2. `summarize.py` reads the pytest JSON report and generates:
   - `grader-results.json` — machine-readable score
   - `grader-report.md` — human-readable PR comment with progress bar and hints
3. The comment is posted (or updated) on the PR via `sticky-pull-request-comment`

## Running the grader locally

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest .grader/checks/ --json-report --json-report-file=grader-results-raw.json -v
python .grader/summarize.py
cat grader-report.md
```
