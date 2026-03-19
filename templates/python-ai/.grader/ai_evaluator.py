"""
Reads .grader/SPEC.md (rubric) and the student artifact.
Calls Claude Haiku via Portkey.
Writes ai-feedback.json with structured coaching feedback.
"""
import json
import os  # used in main() — Task 4
import re
import sys  # used in main() — Task 4
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
