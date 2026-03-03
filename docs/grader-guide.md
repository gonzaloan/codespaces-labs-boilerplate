# Grader Guide

## How it works

Every lab has a `.github/workflows/grade.yml` that runs on every Pull Request:

1. Runs the grader (Playwright or Maven)
2. Parses results and generates `grader-results.json` and `grader-report.md`
3. Posts a score comment on the PR
4. Uploads `grader-results.json` as an artifact

## grader-results.json format

All templates produce this standard JSON:

```json
{
  "lab": "lab-name",
  "score": 8,
  "total": 10,
  "duration": 4500,
  "categories": [
    {
      "name": "Structure",
      "score": 3,
      "total": 3,
      "checks": [
        { "name": "check description", "passed": true, "hint": null },
        { "name": "other check", "passed": false, "hint": "hint for the student" }
      ]
    }
  ]
}
```

## Writing checks — Playwright (TypeScript)

Checks live in `.grader/checks/`. Each file is a category, each `test()` is a check.

```typescript
import { test, expect } from '@playwright/test';

test.describe('My Category', () => {

    test('my check description', () => {
        // The assertion message becomes the hint shown to the student on failure
        expect(someCondition, 'Hint: do X to fix this').toBe(true);
    });

});
```

**Tips:**
- Use descriptive test names — they appear as-is in the PR comment
- Put the hint inside the assertion message: `expect(x, 'your hint here').toBe(true)`
- Use `Structure`, `Quality`, `Execution` as category names by convention

## Writing checks — Java Spring (JUnit 5)

Checks live in `.grader/src/test/java/grader/`. Each class is a category.

```java
class StructureTest {

    @Test
    void testSrcHasJavaFiles() throws IOException {
        // Method name becomes the check label (camelCase → readable)
        // Assertion message becomes the hint shown to the student
        assertFalse(files.isEmpty(), "Add .java files to src/main/java/");
    }

}
```

**Tips:**
- Class name without `Test` suffix → category name (`StructureTest` → `Structure`)
- Method name → check label (`testSrcHasJavaFiles` → `src has Java files`)
- Assertion message → hint shown on failure

## Recommended category structure

| Category | What to check |
|---|---|
| Structure | Required files and directories exist |
| Quality | Code patterns, annotations, style rules |
| Execution | Code runs and produces correct output |
