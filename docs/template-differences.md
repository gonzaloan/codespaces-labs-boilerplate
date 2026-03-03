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
