"""
Reads grader-results-raw.json (pytest-json-report format)
Reads ai-feedback.json (from ai_evaluator.py)
Writes grader-results.json (boilerplate standard format)
Writes grader-report.md (PR comment)
"""
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Rubric — points per category.
# These values MUST match the per-file point totals in GitHub Classroom.
# Modify these per lab to match the actual point distribution.
# ---------------------------------------------------------------------------
CATEGORY_POINTS = {
    "Structure": 6,
    "Execution": 15,
    "Quality": 8,
}

TOTAL_POINTS = sum(CATEGORY_POINTS.values())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_pytest_results(raw: dict) -> list:
    """Parse pytest-json-report output into category dicts."""
    categories: dict = {}
    for test in raw.get("tests", []):
        nodeid = test.get("nodeid", "")
        parts = nodeid.split("::")
        if len(parts) < 3:
            continue
        class_name = parts[-2]
        method_name = parts[-1]
        check_name = (
            method_name.replace("test_", "", 1).replace("_", " ").strip().capitalize()
        )
        passed = test.get("outcome") == "passed"
        hint = None
        if not passed:
            longrepr = test.get("call", {}).get("longrepr", "")
            # longrepr can be a dict for structured pytest failures; only use string form
            if isinstance(longrepr, str) and longrepr:
                first_line = next((l for l in longrepr.splitlines() if l.strip()), "")
                hint = first_line[:400] or None

        categories.setdefault(class_name, []).append(
            {"name": check_name, "passed": passed, "hint": hint}
        )

    result = []
    for name, checks in categories.items():
        score = sum(1 for c in checks if c["passed"])
        total = len(checks)
        max_pts = CATEGORY_POINTS.get(name, 0)
        points = round((score / total) * max_pts, 1) if total > 0 and max_pts > 0 else 0.0
        result.append(
            {
                "name": name,
                "score": score,
                "total": total,
                "points": points,
                "maxPoints": max_pts,
                "checks": checks,
            }
        )
    return result


def progress_bar(score: float, total: float) -> str:
    if total == 0:
        return "`░░░░░░░░░░`"
    filled = round((score / total) * 10)
    return "`" + "█" * filled + "░" * (10 - filled) + "`"


def status_message(pct: int) -> str:
    if pct == 100:
        return "Perfect score! Excellent work!"
    if pct >= 80:
        return "Almost there — just a few more to fix!"
    if pct >= 50:
        return "Good progress, keep going!"
    if pct >= 20:
        return "You've started! Keep building."
    return "Time to write some code!"


def cat_icon(cat: dict) -> str:
    if cat["score"] == cat["total"]:
        return "✅"
    if cat["score"] == 0:
        return "❌"
    return "⚠️"


def render_ai_section(ai: dict) -> str:
    """Render the AI Review section of the PR comment."""
    if not ai.get("evaluated"):
        reason = ai.get("reason", "AI Review: not configured.")
        return f"\n---\n\n> {reason}\n\n"

    artifact = ai.get("artifact", "")
    total = ai.get("total_score", 0)
    max_s = ai.get("max_score", 0)
    artifact_label = Path(artifact).name if artifact else "artifact"

    md = f"\n---\n\n### 🤖 AI Review — {artifact_label}   {total} / {max_s}\n\n"
    md += "> *Coaching feedback — not included in your automated score.*\n\n"
    summary = ai.get("summary", "")
    if summary:
        md += f"> 💬 **Overall:** {summary}\n\n"
    for i, criterion in enumerate(ai.get("criteria", [])):
        open_attr = " open" if i == 0 else ""
        md += f"<details{open_attr}>\n"
        md += (
            f"<summary><b>{criterion['name']}</b>"
            f" — {criterion['score']} / {criterion['max']}</summary>\n\n"
        )
        md += f"✅ **Strength:** {criterion.get('strength', '')}\n\n"
        md += f"⚠️ **Gap:** {criterion.get('gap', '')}\n\n"
        md += f"💡 **Action:** {criterion.get('action', '')}\n\n"
        md += "</details>\n\n"

    return md


def build_report(categories: list, ai: dict, lab_name: str, duration: float = 0) -> tuple:
    """Return (grader-report.md content, grader-results dict)."""
    earned = round(sum(c["points"] for c in categories), 1)
    pct = round(earned / TOTAL_POINTS * 100) if TOTAL_POINTS > 0 else 0

    md = "## Lab Grader Results\n\n"
    md += f"> **Score: {earned} / {TOTAL_POINTS} pts ({pct}%)** — {status_message(pct)}\n"
    md += f"> {progress_bar(earned, TOTAL_POINTS)}\n\n"
    md += "---\n\n"
    md += "### Score Breakdown\n\n"
    md += "| | Category | Points | Checks |\n"
    md += "|---|---|---|---|\n"
    for cat in categories:
        icon = cat_icon(cat)
        chk = f"{cat['score']}/{cat['total']}" if cat["score"] < cat["total"] else "all passing"
        md += f"| {icon} | **{cat['name']}** | {cat['points']} / {cat['maxPoints']} | {chk} |\n"
    md += "\n---\n\n"
    md += "### Details\n\n"
    for cat in categories:
        icon = cat_icon(cat)
        pts = f"{cat['points']} / {cat['maxPoints']} pts"
        chk = f"{cat['score']}/{cat['total']} checks"
        failing = [c for c in cat["checks"] if not c["passed"]]
        md += "<details>\n"
        md += f"<summary>{icon} <b>{cat['name']}</b> — {pts} — {chk}</summary>\n\n"
        md += "| Check | Status | Hint |\n|---|---|---|\n"
        for check in cat["checks"]:
            status = "✅ Pass" if check["passed"] else "❌ Fail"
            hint = check.get("hint") or ""
            md += f"| {check['name']} | {status} | {hint} |\n"
        if failing:
            md += "\n**What to fix:**\n"
            for check in failing:
                suffix = f" — {check['hint']}" if check.get("hint") else ""
                md += f"- `{check['name']}`{suffix}\n"
        md += "\n</details>\n\n"

    md += render_ai_section(ai)

    results = {
        "lab": lab_name,
        "score": earned,
        "total": TOTAL_POINTS,
        "duration": duration,
        "categories": categories,
    }
    return md, results


def main():
    root = Path.cwd()
    raw_file = root / "grader-results-raw.json"
    ai_file = root / "ai-feedback.json"
    out_json = root / "grader-results.json"
    out_md = root / "grader-report.md"

    raw = json.loads(raw_file.read_text()) if raw_file.exists() else {"tests": [], "duration": 0}
    ai = (
        json.loads(ai_file.read_text())
        if ai_file.exists()
        else {"evaluated": False, "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable."}
    )
    categories = parse_pytest_results(raw)
    lab_name = root.name
    duration = raw.get("duration", 0)
    md, results = build_report(categories, ai, lab_name, duration)
    out_json.write_text(json.dumps(results, indent=2))
    out_md.write_text(md)
    print(f"grader-results.json written ({results['score']}/{results['total']} pts)")
    print("grader-report.md written")


if __name__ == "__main__":
    main()
