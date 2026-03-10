"""
Reads grader-results-raw.json (pytest-json-report format)
Writes grader-results.json  (boilerplate standard format)
Writes grader-report.md     (PR comment)
"""

import json
import os
import sys

ROOT         = os.getcwd()
RAW_FILE     = os.path.join(ROOT, "grader-results-raw.json")
OUT_JSON     = os.path.join(ROOT, "grader-results.json")
OUT_MD       = os.path.join(ROOT, "grader-report.md")

# ---------------------------------------------------------------------------
# Read raw results
# ---------------------------------------------------------------------------

try:
    with open(RAW_FILE, "r") as f:
        raw = json.load(f)
except Exception as e:
    print(f"Could not read grader-results-raw.json: {e}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Parse pytest-json-report format
# Each test has a nodeid like "checks/test_structure.py::ClassName::test_name"
# We group by the describe (class) name to mirror the playwright template.
# ---------------------------------------------------------------------------

categories: dict[str, dict] = {}

for test in raw.get("tests", []):
    node   = test["nodeid"]                         # e.g. checks/test_structure.py::Structure::has_src_dir
    parts  = node.split("::")
    group  = parts[1] if len(parts) >= 3 else parts[0]   # class or file name
    name   = parts[-1].replace("_", " ").capitalize()
    passed = test["outcome"] == "passed"

    hint = None
    if not passed:
        msg = (test.get("call") or {}).get("longrepr", "")
        if msg:
            hint = " · ".join(
                line.strip() for line in str(msg).splitlines()
                if line.strip()
            )[:200]

    if group not in categories:
        categories[group] = {"name": group, "score": 0, "total": 0, "checks": []}

    categories[group]["checks"].append({"name": name, "passed": passed, "hint": hint})
    categories[group]["total"] += 1
    if passed:
        categories[group]["score"] += 1

cats        = list(categories.values())
total_score = sum(c["score"] for c in cats)
total_checks = sum(c["total"] for c in cats)
lab_name    = os.path.basename(ROOT)

# ---------------------------------------------------------------------------
# Write grader-results.json
# ---------------------------------------------------------------------------

results = {
    "lab":        lab_name,
    "score":      total_score,
    "total":      total_checks,
    "duration":   raw.get("duration", 0),
    "categories": cats,
}

with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)
print(f"grader-results.json written ({total_score}/{total_checks})")

# ---------------------------------------------------------------------------
# Write grader-report.md
# ---------------------------------------------------------------------------

pct = round((total_score / total_checks) * 100) if total_checks > 0 else 0

def progress_bar(passed: int, total: int) -> str:
    if total == 0:
        return "`░░░░░░░░░░`"
    filled = round((passed / total) * 10)
    return "`" + "█" * filled + "░" * (10 - filled) + "`"

def status_message(p: int) -> str:
    if p == 100: return "Perfect score! Excellent work!"
    if p >= 80:  return "Almost there — just a few more to fix!"
    if p >= 50:  return "Good progress, keep going!"
    if p >= 20:  return "You've started! Keep building."
    return "Time to write some code!"

def has_student_code() -> bool:
    src = os.path.join(ROOT, "src")
    if not os.path.isdir(src):
        return False
    for root, _, files in os.walk(src):
        for f in files:
            if not f.endswith(".gitkeep"):
                return True
    return False

md  = "## Lab Grader Results\n\n"
md += f"> **Score: {total_score} / {total_checks} checks passed ({pct}%)** — {status_message(pct)}\n"
md += f"> {progress_bar(total_score, total_checks)}\n\n"
md += "---\n\n"

if not has_student_code():
    md += "### Getting Started\n\n"
    md += "*It looks like you haven't added any code yet — here's where to begin:*\n\n"
    md += "1. Read `docs/instructions.md` for the full exercise description\n"
    md += "2. Add your code inside the `src/` directory\n"
    md += "3. Run `pytest` locally to verify before pushing\n\n"
    md += "---\n\n"

for cat in cats:
    icon = "✅" if cat["score"] == cat["total"] else ("❌" if cat["score"] == 0 else "⚠️")
    md += "<details>\n"
    md += f"<summary>{icon} {cat['name']} — {cat['score']}/{cat['total']} passed</summary>\n\n"
    md += "| Check | | Hint |\n"
    md += "|---|---|---|\n"
    for check in cat["checks"]:
        icon2 = "✅" if check["passed"] else "❌"
        md += f"| {check['name']} | {icon2} | {check['hint'] or ''} |\n"
    md += "\n</details>\n\n"

md += "---\n\n"
md += "### Resources\n\n"
md += "- [GitHub Copilot docs](https://docs.github.com/en/copilot)\n"
md += "- [Python pytest docs](https://docs.pytest.org/)\n"
md += "- Lab instructions: `docs/instructions.md`\n"

with open(OUT_MD, "w") as f:
    f.write(md)
print("grader-report.md written")
