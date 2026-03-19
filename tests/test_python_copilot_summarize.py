import importlib.util
from pathlib import Path

# Load python-copilot summarize under a unique module name to avoid sys.path conflicts
_spec = importlib.util.spec_from_file_location(
    "python_copilot_summarize",
    Path(__file__).parent.parent / "templates" / "python-copilot" / ".grader" / "summarize.py",
)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
render_ai_section = _module.render_ai_section

SAMPLE_AI = {
    "evaluated": True,
    "artifact": "src/solution.py",
    "total_score": 8.0,
    "max_score": 10,
    "criteria": [
        {
            "name": "Code Quality",
            "score": 4.0,
            "max": 5,
            "strength": "Good variable names.",
            "gap": "Missing docstrings.",
            "action": "Add a docstring to each function.",
        },
        {
            "name": "Copilot Usage",
            "score": 4.0,
            "max": 5,
            "strength": "Evidence of Copilot in comments.",
            "gap": "No prompt engineering shown.",
            "action": "Include one example of a Copilot prompt you refined.",
        },
    ],
    "summary": "Strong start. Focus on documentation next.",
}


def test_render_ai_section_shows_score():
    result = render_ai_section(SAMPLE_AI)
    assert "8.0 / 10" in result


def test_render_ai_section_has_disclaimer():
    result = render_ai_section(SAMPLE_AI)
    assert "not included in your automated score" in result


def test_render_ai_section_summary_before_criteria():
    result = render_ai_section(SAMPLE_AI)
    summary_pos = result.index("Strong start")
    details_pos = result.index("<details")
    assert summary_pos < details_pos, "Summary must appear before criteria details"


def test_render_ai_section_first_criterion_open():
    result = render_ai_section(SAMPLE_AI)
    assert "<details open>" in result


def test_render_ai_section_not_configured():
    result = render_ai_section({"evaluated": False, "reason": "AI Review: not configured."})
    assert "not configured" in result
    assert "<details" not in result
