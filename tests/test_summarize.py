from summarize import parse_pytest_results, progress_bar, render_ai_section

SAMPLE_RAW = {
    "duration": 0.5,
    "tests": [
        {
            "nodeid": ".grader/checks/test_structure.py::Structure::test_file_exists",
            "outcome": "passed",
            "call": {"duration": 0.001, "outcome": "passed"},
        },
        {
            "nodeid": ".grader/checks/test_execution.py::Execution::test_output_correct",
            "outcome": "failed",
            "call": {
                "duration": 0.001,
                "outcome": "failed",
                "longrepr": "AssertionError: output should be 42\nassert 0 == 42",
            },
        },
    ],
}


def test_parse_extracts_categories():
    cats = parse_pytest_results(SAMPLE_RAW)
    names = [c["name"] for c in cats]
    assert "Structure" in names
    assert "Execution" in names


def test_parse_passed_check():
    cats = parse_pytest_results(SAMPLE_RAW)
    structure = next(c for c in cats if c["name"] == "Structure")
    assert structure["score"] == 1
    assert structure["total"] == 1
    assert structure["checks"][0]["passed"] is True
    assert structure["checks"][0]["hint"] is None


def test_parse_failed_check_has_hint():
    cats = parse_pytest_results(SAMPLE_RAW)
    execution = next(c for c in cats if c["name"] == "Execution")
    assert execution["score"] == 0
    check = execution["checks"][0]
    assert check["passed"] is False
    assert "output should be 42" in check["hint"]


def test_parse_check_name_formatted():
    cats = parse_pytest_results(SAMPLE_RAW)
    execution = next(c for c in cats if c["name"] == "Execution")
    # "test_output_correct" -> "Output correct"
    assert execution["checks"][0]["name"] == "Output correct"


def test_progress_bar_full():
    assert "██████████" in progress_bar(10, 10)


def test_progress_bar_empty():
    assert "░░░░░░░░░░" in progress_bar(0, 10)


def test_progress_bar_half():
    bar = progress_bar(5, 10)
    assert "█████░░░░░" in bar


SAMPLE_AI_FEEDBACK = {
    "evaluated": True,
    "artifact": "notebook/walkthrough.ipynb",
    "total_score": 14.5,
    "max_score": 20,
    "criteria": [
        {
            "name": "MCP Explanation",
            "score": 4.0,
            "max": 5,
            "strength": "Explains server-client well.",
            "gap": "Missing subprocess detail.",
            "action": "Add a sentence about stdin/stdout pipes.",
        },
        {
            "name": "ASCII Diagram",
            "score": 3.0,
            "max": 5,
            "strength": "Has 3 nodes.",
            "gap": "Arrows not labeled.",
            "action": "Add --[tool_call]--> labels.",
        },
    ],
    "summary": "Good architectural understanding.",
}

SAMPLE_AI_NOT_CONFIGURED = {
    "evaluated": False,
    "reason": "AI Review: not configured — set PORTKEY_API_KEY to enable.",
}


def test_render_ai_section_shows_score():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "14.5 / 20" in md


def test_render_ai_section_first_criterion_open():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "<details open>" in md


def test_render_ai_section_second_criterion_collapsed():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "<details>" in md


def test_render_ai_section_has_strength_gap_action():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "Strength" in md
    assert "Gap" in md
    assert "Action" in md
    assert "Explains server-client well." in md


def test_render_ai_section_has_summary():
    md = render_ai_section(SAMPLE_AI_FEEDBACK)
    assert "Good architectural understanding." in md


def test_render_ai_section_not_configured():
    md = render_ai_section(SAMPLE_AI_NOT_CONFIGURED)
    assert "PORTKEY_API_KEY" in md
    assert "<details" not in md
