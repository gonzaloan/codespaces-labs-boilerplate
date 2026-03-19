"""
Reads .grader/SPEC.md (rubric) and the student artifact.
Calls Claude Haiku via Portkey.
Writes ai-feedback.json with structured coaching feedback.
"""
import json
import os
import re
from pathlib import Path

import frontmatter


# ---------------------------------------------------------------------------
# SPEC parsing
# ---------------------------------------------------------------------------

def parse_spec(spec_path: Path) -> dict:
    """Parse SPEC.md frontmatter and ## Criterion (max: N) headings."""
    post = frontmatter.loads(spec_path.read_text(encoding="utf-8"))

    criteria = []
    pattern = r"^## (.+?) \(max: (\d+)\)\n(.*?)(?=^## |\Z)"
    for m in re.finditer(pattern, post.content, re.MULTILINE | re.DOTALL):
        criteria.append(
            {
                "name": m.group(1).strip(),
                "max": int(m.group(2)),
                "description": m.group(3).strip(),
            }
        )

    return {
        "artifact": str(post["artifact"]),
        "artifact_type": str(post["artifact_type"]),
        "max_score": int(post["max_score"]),
        "criteria": criteria,
    }


# ---------------------------------------------------------------------------
# Artifact reading
# ---------------------------------------------------------------------------

def read_artifact(artifact_path: Path, artifact_type: str) -> str:
    """Read student artifact. For Jupyter notebooks, extract cell sources only."""
    if artifact_type == "jupyter":
        nb = json.loads(artifact_path.read_text(encoding="utf-8"))
        parts = []
        for cell in nb.get("cells", []):
            if cell.get("cell_type") not in ("markdown", "code"):
                continue
            source = "".join(cell.get("source", []))
            if source.strip():
                parts.append(f"[{cell['cell_type'].upper()} CELL]\n{source}")
        return "\n\n".join(parts)
    else:
        return artifact_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def build_prompt(artifact_content: str, artifact_type: str, criteria: list) -> str:
    rubric_text = "\n\n".join(
        f"## {c['name']} (max: {c['max']})\n{c['description']}" for c in criteria
    )
    return f"""You are an expert technical coach reviewing a consultant's work at Perficient.
Your goal is to give feedback that is specific, actionable, and encouraging.

## Artifact to evaluate
Type: {artifact_type}
Content:
{artifact_content}

## Rubric
{rubric_text}

## Instructions
For each criterion:
1. Identify what the consultant did well (be specific — quote or reference their work).
2. Identify what is missing or imprecise (be concrete, not vague).
3. Give one specific action they can take to improve this criterion.

Score each criterion from 0 to its max (floats allowed, 1 decimal).
Do not round up — partial credit only when the criterion is partially met.
The "name" field in your JSON MUST exactly match the criterion names from the rubric above.

Return ONLY valid JSON matching this schema:
{{
  "criteria": [
    {{
      "name": "...",
      "score": N.N,
      "max": N,
      "strength": "What they did well",
      "gap": "What is missing or imprecise",
      "action": "One specific thing to improve"
    }}
  ],
  "summary": "2-3 sentence coaching summary. Start with a genuine strength, then the most impactful improvement."
}}"""


# ---------------------------------------------------------------------------
# Score validation
# ---------------------------------------------------------------------------

def clamp_scores(criteria_result: list, criteria_spec: list) -> list:
    """Clamp model-returned scores to their criterion max. Round to 1 decimal.

    Modifies criteria_result dicts in place and returns the same list.
    Callers must not rely on the original values after this call.
    """
    spec_map = {c["name"]: c["max"] for c in criteria_spec}
    for c in criteria_result:
        max_val = spec_map.get(c["name"], c.get("max", 10))
        c["score"] = round(min(float(c["score"]), float(max_val)), 1)
        c["max"] = max_val
    return criteria_result


# ---------------------------------------------------------------------------
# Portkey API call
# ---------------------------------------------------------------------------

def call_portkey(prompt: str, api_key: str) -> dict:
    """Call Claude Haiku via Portkey. Returns parsed JSON dict."""
    from portkey_ai import Portkey  # noqa: PLC0415  imported here to allow mocking

    client = Portkey(api_key=api_key)
    response = client.chat.completions.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Error output helper
# ---------------------------------------------------------------------------

def _write_error(reason: str) -> None:
    Path("ai-feedback.json").write_text(
        json.dumps({"evaluated": False, "reason": reason}, indent=2), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        _write_error("AI Review: not configured — set PORTKEY_API_KEY to enable.")
        print("PORTKEY_API_KEY not set — skipping AI evaluation")
        return

    spec_path = Path(".grader") / "SPEC.md"
    spec = parse_spec(spec_path)

    artifact_path = Path(spec["artifact"])
    if not artifact_path.exists():
        _write_error(f"AI Review: artifact not found at `{spec['artifact']}`.")
        print(f"Artifact not found: {spec['artifact']}")
        return

    artifact_content = read_artifact(artifact_path, spec["artifact_type"])
    prompt = build_prompt(artifact_content, spec["artifact_type"], spec["criteria"])

    raw_result = None
    for attempt in range(2):
        try:
            raw_result = call_portkey(prompt, api_key)
            break
        except json.JSONDecodeError:
            if attempt == 1:
                _write_error("AI Review: evaluation failed (invalid response). Score not affected.")
                return
        except Exception as exc:
            print(f"Portkey API error: {type(exc).__name__}: {exc}")
            _write_error("AI Review: evaluation failed (API error). Score not affected.")
            return

    if "criteria" not in raw_result:
        _write_error("AI Review: evaluation failed (invalid response). Score not affected.")
        return
    criteria_result = clamp_scores(raw_result["criteria"], spec["criteria"])
    total_score = round(sum(c["score"] for c in criteria_result), 1)

    output = {
        "evaluated": True,
        "artifact": spec["artifact"],
        "total_score": total_score,
        "max_score": spec["max_score"],
        "criteria": criteria_result,
        "summary": raw_result.get("summary", ""),
    }
    Path("ai-feedback.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"ai-feedback.json written ({total_score}/{spec['max_score']})")


if __name__ == "__main__":
    main()
