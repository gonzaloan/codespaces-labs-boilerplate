"""
Reads grader-results-raw.json (pytest-json-report format)
Reads ai-feedback.json (from ai_evaluator.py)
Writes grader-results.json  (boilerplate standard format)
Writes grader-report.md     (PR comment)
"""

import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def has_student_code(root: str) -> bool:
    src = os.path.join(root, "src")
    if not os.path.isdir(src):
        return False
    for r, _, files in os.walk(src):
        for f in files:
            if not f.endswith(".gitkeep"):
                return True
    return False


def render_ai_section(ai: dict) -> str:
    """Render the AI Review section of the PR comment."""
    if not ai.get("evaluated"):
        reason = ai.get("reason", "AI Review: not configured.")
        return f"\n---\n\n> {reason}\n\n"

    artifact = ai.get("artifact", "")
    artifact_label = Path(artifact).name if artifact else "artifact"
    total = ai.get("total_score", 0)
    max_s = ai.get("max_score", 0)

    md = f"\n---\n\n### AI Review — {artifact_label}   {total} / {max_s}\n\n"
    md += "> *Coaching feedback — not included in your automated score.*\n\n"
    summary = ai.get("summary", "")
    if summary:
        md += f"> **Overall:** {summary}\n\n"
    for i, criterion in enumerate(ai.get("criteria", [])):
        open_attr = " open" if i == 0 else ""
        md += f"<details{open_attr}>\n"
        md += f"<summary><b>{criterion['name']}</b> — {criterion['score']} / {criterion['max']}</summary>\n\n"
        md += f"**Strength:** {criterion.get('strength', '')}\n\n"
        md += f"**Gap:** {criterion.get('gap', '')}\n\n"
        md += f"**Action:** {criterion.get('action', '')}\n\n"
        md += "</details>\n\n"
    return md


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    root = str(Path.cwd())
    raw_file = os.path.join(root, "grader-results-raw.json")
    ai_file  = os.path.join(root, "ai-feedback.json")
    out_json = os.path.join(root, "grader-results.json")
    out_md   = os.path.join(root, "grader-report.md")

    try:
        with open(raw_file, "r") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"Could not read grader-results-raw.json: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Parse pytest-json-report format
    # -----------------------------------------------------------------------

    categories: dict[str, dict] = {}

    for test in raw.get("tests", []):
        node   = test["nodeid"]
        parts  = node.split("::")
        group  = parts[1] if len(parts) >= 3 else parts[0]
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

    cats         = list(categories.values())
    total_score  = sum(c["score"] for c in cats)
    total_checks = sum(c["total"] for c in cats)
    lab_name     = os.path.basename(root)

    # -----------------------------------------------------------------------
    # Write grader-results.json
    # -----------------------------------------------------------------------

    results = {
        "lab":        lab_name,
        "score":      total_score,
        "total":      total_checks,
        "duration":   raw.get("duration", 0),
        "categories": cats,
    }

    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"grader-results.json written ({total_score}/{total_checks})")

    # -----------------------------------------------------------------------
    # Write grader-report.md
    # -----------------------------------------------------------------------

    pct = round((total_score / total_checks) * 100) if total_checks > 0 else 0

    md  = "## Lab Grader Results\n\n"
    md += f"> **Score: {total_score} / {total_checks} checks passed ({pct}%)** — {status_message(pct)}\n"
    md += f"> {progress_bar(total_score, total_checks)}\n\n"
    md += "---\n\n"

    if not has_student_code(root):
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

    ai_data = (
        json.loads(open(ai_file).read())
        if os.path.exists(ai_file)
        else {"evaluated": False, "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable."}
    )
    md += render_ai_section(ai_data)

    with open(out_md, "w") as f:
        f.write(md)
    print("grader-report.md written")


if __name__ == "__main__":
    main()
