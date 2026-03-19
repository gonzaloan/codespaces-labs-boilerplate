# Template Differences

## What's the same across all templates

- `grade.yml` pattern: checkout → setup → grade → generate report → post comment → upload artifact
- PR comment format: progress bar, collapsible sections per category, hints on failure
- `grader-results.json` standard format
- `scripts/new-lab.sh` to generate new labs
- `docs/instructions.md` as a blank template for the professor

## playwright

| | |
|---|---|
| Language | TypeScript |
| Runner | Playwright Test |
| Grade command | `npm run grade` |
| Checks location | `.grader/checks/*.test.ts` |
| Report input | `.grader/grader-results-raw.json` (Playwright JSON reporter) |
| Report script | `.grader/summarize.js` |
| Category = | `test.describe()` block |
| Check = | `test()` inside a describe |
| Hint = | assertion message |

## java-spring

| | |
|---|---|
| Language | Java 21 |
| Runner | JUnit 5 via Maven |
| Grade command | `mvn test -f .grader/pom.xml` |
| Checks location | `.grader/src/test/java/grader/*.java` |
| Report input | `.grader/target/surefire-reports/*.xml` |
| Report script | `.grader/summarize.js` |
| Category = | Class name without `Test` suffix |
| Check = | `@Test` method |
| Hint = | assertion message |

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

**pytest class discovery:** The template's `pytest.ini` lists category class names in `python_classes`.
If you add a new category (e.g. `class Security:`), add it to `python_classes` AND to `CATEGORY_POINTS`
in `.grader/summarize.py`.
