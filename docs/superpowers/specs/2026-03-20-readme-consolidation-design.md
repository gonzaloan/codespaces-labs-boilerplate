# README Consolidation Design
**Date:** 2026-03-20
**Project:** Perficient AI Academy — Boilerplate + L1 Assignment
**Status:** Approved

---

## Problem

Students land on the repo page and see a README that immediately says "read docs/instructions.md first." This adds unnecessary friction before they can start working. The `docs/instructions.md` file is a second document to maintain, and its existence creates confusion about which file is the source of truth.

---

## Decision

**README is the single source of truth for student-facing content.** All task instructions move inline into the README. `docs/instructions.md` is eliminated from all student repos and all boilerplate templates.

---

## Scope

### assignment-l1-dev-ai-assisted (student repo)
- **README.md** — rewritten: full scenario, tasks 1–7 inline, grading table, how to submit, tips + troubleshooting unified
- **docs/instructions.md** — deleted

### codespaces-lab-boilerplate (4 templates)
- **templates/python-ai/README.md** — rewritten to match the rich python-copilot structure + `## Tasks` section with TODOs
- **templates/python-copilot/README.md** — "Step 2: Read instructions.md" replaced with `## Tasks` TODO section
- **templates/playwright/README.md** — same
- **templates/java-spring/README.md** — same
- **templates/*/docs/instructions.md** — deleted from all 4 templates
- **docs/how-to-create-a-lab.md** — step 2 updated: "edit README.md → ## Tasks section"

---

## README Structure (all templates + L1 repo)

```
# [Lab Title]
[Academy · Path · Level · Time badge row]

## The scenario
[2–3 sentence narrative. Client, context, student's mission.]

## Before you start
[FIXED across all labs — how to open Codespace + verify starting state]

## Tasks
[Each task: ### Task N — Title (~X min) + what to do + REFLECTION.md capture]

## Grading
[Table: categories, points, what is checked. Minimum to pass.]

## How to submit
[FIXED — PR to main, grader runs automatically, can push multiple times]

## Tips & Troubleshooting
[Lab-specific tips + common error resolutions]
```

### Fixed vs. TODO sections

| Section | In template | In student repo |
|---|---|---|
| The scenario | `<!-- TODO: Write scenario -->` | Filled |
| Before you start | Fixed content | Identical to template |
| Tasks | `<!-- TODO: Define tasks -->` | Filled with all tasks |
| Grading | `<!-- TODO: Fill table -->` | Filled |
| How to submit | Fixed content | Identical to template |
| Tips & Troubleshooting | `<!-- TODO: Lab-specific tips -->` | Filled |

---

## Template TODO format (Tasks section)

```markdown
## Tasks

<!--
TODO: Define each task using this format:

### Task N — [Name] (~X min)

[What the student does. 2–3 sentences.]

**What to capture in REFLECTION.md:** [What they document, or "No REFLECTION entry required."]

---
-->
```

---

## how-to-create-a-lab.md change

Step 2 currently reads:
> "Edit `docs/instructions.md` — describe what the student has to build..."

New text:
> "Edit `README.md` — fill in the `## The scenario` and `## Tasks` sections. Each task should describe what the student builds, how they approach it, and what to capture in REFLECTION.md."

---

## Success Criteria

- [ ] Student opening L1 repo sees a complete README — no need to navigate elsewhere
- [ ] `docs/instructions.md` deleted from L1 repo and all 4 boilerplate templates
- [ ] All 4 template READMEs follow identical section structure
- [ ] `python-ai` README matches richness of `python-copilot`/`playwright`/`java-spring`
- [ ] `how-to-create-a-lab.md` step 2 points to README, not instructions.md
- [ ] Changes committed in both repos
