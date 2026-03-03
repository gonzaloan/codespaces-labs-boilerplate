# How to Create a Lab

## Prerequisites

- Git installed
- Access to this boilerplate repository

## Steps

### 1. Generate the lab

```bash
bash scripts/new-lab.sh
```

Follow the prompts:
- **Template:** `playwright` or `java-spring`
- **Lab name:** e.g. `lab-02-api-testing`
- **Output directory:** where the new repo will be created (default: `../`)

### 2. Define the exercise

Edit `docs/instructions.md` — describe what the student has to build, the requirements, and any useful resources.

### 3. Write the grading criteria

Edit the checks inside `.grader/checks/` (Playwright) or `.grader/src/test/java/grader/` (Java Spring).

Each check is a test that validates one specific requirement. See `grader-guide.md` for details.

### 4. Add starter code (optional)

Put any base code the student should start from inside `src/`. Leave it empty if you want students to build from scratch.

### 5. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_ORG/YOUR_LAB.git
git push -u origin main
```

Enable GitHub Actions in the repository settings if it's not already enabled.

### 6. Share with students

Students fork or clone the repo, open it in GitHub Codespaces, and submit their work via Pull Request.
