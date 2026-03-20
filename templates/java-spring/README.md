# [LAB NAME] <!-- TODO: replace with lab name, e.g. "Spring Boot API Sprint" -->

**Perficient Global AI Academy** · [PATH NAME] · Level [N] <!-- TODO: replace path and level -->

---

<!-- TODO: replace with a 1-2 sentence description of the scenario -->
> [Short scenario description — what is the student's mission?]

![Lab overview](docs/images/lab-overview.png) <!-- TODO: add screenshot of the Codespace with the lab open -->

| | |
|---|---|
| **Estimated time** | [X–Y minutes] |
| **Minimum passing score** | 70% |
| **Platform** | GitHub Codespaces + GitHub Copilot |

---

## How to start

### 1 — Open your Codespace

Click the green **"Code"** button at the top of this page, select the **"Codespaces"** tab, then click **"Create codespace on main"**.

![Open Codespace](docs/images/open-codespace.png) <!-- TODO: add screenshot -->

> The environment will take about 60 seconds to set up. Everything is pre-installed — JDK 21, Maven, and GitHub Copilot.

### 2 — Verify your starting state

```bash
mvn test
```

Everything will fail — that is intentional. Your goal is to reach 70% or higher.

### 3 — Check your score after working

Push your changes — the grader runs automatically and posts your score as a comment on the **Feedback pull request** in this repo.

![Score comment](docs/images/score-comment.png) <!-- TODO: add screenshot of the PR comment with score -->

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

## How the grader works

Every time you push to `main`, GitHub Actions runs a series of automated checks and posts an updated score on the Feedback PR.

```
You push to main
    → GitHub Actions runs JUnit 5 tests via Maven on .grader/src/test/
    → Score is calculated
    → Result posted as a comment on the Feedback PR
```

You can push as many times as you want — the score updates each time.

If your instructor has configured AI review, you will also receive coaching feedback on your submitted artifact — what you did well, what is missing, and one specific action to improve. This feedback is formative and does not affect your automated score.

---

## Rules

<!-- TODO: customize rules per lab -->
- Use GitHub Copilot for all code — do not write logic manually
- Commit frequently so your workflow is visible in the commit history
- Fill in `REFLECTION.md` before your final submission

---

## Troubleshooting

**Codespace won't start**
Try refreshing the page and creating a new Codespace. If the issue persists, contact your instructor.

**Copilot suggestions not appearing**
Make sure you are signed in to GitHub in VS Code. Click the Copilot icon in the bottom status bar and follow the sign-in flow.

**Maven build fails with "cannot find symbol"**
Check that your class names and package declarations match what the grader expects. See the Tasks section above for the required class structure.

**Tests failing locally but passing in Actions (or vice versa)**
Run `mvn dependency:resolve` in the terminal to ensure all dependencies are downloaded.

**I accidentally pushed to the wrong branch**
That's fine — only pushes to `main` trigger the grader.

---

## Need help?

Contact your instructor or post in the Academy support channel. <!-- TODO: add specific contact/channel -->
