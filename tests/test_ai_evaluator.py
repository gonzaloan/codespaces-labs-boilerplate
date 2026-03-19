import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_evaluator import parse_spec, read_artifact, build_prompt, clamp_scores

SAMPLE_SPEC = """\
---
artifact: notebook/walkthrough.ipynb
artifact_type: jupyter
max_score: 20
---

# AI Evaluation Rubric

## MCP Explanation (max: 5)
Must mention: server, client, stdio.

## ASCII Diagram (max: 5)
Must include 3 or more nodes.
"""

SAMPLE_NOTEBOOK = {
    "cells": [
        {"cell_type": "markdown", "source": ["# Walkthrough\n", "Some text."]},
        {"cell_type": "code", "source": ["print('hello')"]},
        {"cell_type": "raw", "source": ["ignored"]},
    ]
}


def test_parse_spec_frontmatter(tmp_path):
    spec_file = tmp_path / "SPEC.md"
    spec_file.write_text(SAMPLE_SPEC)
    spec = parse_spec(spec_file)
    assert spec["artifact"] == "notebook/walkthrough.ipynb"
    assert spec["artifact_type"] == "jupyter"
    assert spec["max_score"] == 20


def test_parse_spec_criteria(tmp_path):
    spec_file = tmp_path / "SPEC.md"
    spec_file.write_text(SAMPLE_SPEC)
    spec = parse_spec(spec_file)
    assert len(spec["criteria"]) == 2
    assert spec["criteria"][0]["name"] == "MCP Explanation"
    assert spec["criteria"][0]["max"] == 5
    assert "server" in spec["criteria"][0]["description"]


def test_read_artifact_jupyter(tmp_path):
    nb_file = tmp_path / "notebook.ipynb"
    nb_file.write_text(json.dumps(SAMPLE_NOTEBOOK))
    content = read_artifact(nb_file, "jupyter")
    assert "[MARKDOWN CELL]" in content
    assert "Some text." in content
    assert "[CODE CELL]" in content
    assert "print('hello')" in content
    # raw cells are excluded
    assert "ignored" not in content


def test_read_artifact_markdown(tmp_path):
    md_file = tmp_path / "ADR.md"
    md_file.write_text("# Decision\n\nWe chose X.")
    content = read_artifact(md_file, "markdown")
    assert content == "# Decision\n\nWe chose X."


def test_read_artifact_jupyter_excludes_empty_cells(tmp_path):
    nb = {"cells": [{"cell_type": "markdown", "source": ["   "]}, {"cell_type": "code", "source": ["x = 1"]}]}
    nb_file = tmp_path / "nb.ipynb"
    nb_file.write_text(json.dumps(nb))
    content = read_artifact(nb_file, "jupyter")
    # empty markdown cell excluded
    assert content.count("[MARKDOWN CELL]") == 0
    assert "x = 1" in content


def test_clamp_scores():
    criteria_result = [{"name": "A", "score": 7.0, "max": 5}]
    criteria_spec = [{"name": "A", "max": 5}]
    result = clamp_scores(criteria_result, criteria_spec)
    assert result[0]["score"] == 5.0


def test_clamp_scores_no_clamp_needed():
    criteria_result = [{"name": "A", "score": 3.5, "max": 5}]
    criteria_spec = [{"name": "A", "max": 5}]
    result = clamp_scores(criteria_result, criteria_spec)
    assert result[0]["score"] == 3.5


def test_build_prompt_contains_criterion_name():
    criteria = [{"name": "MCP Explanation", "max": 5, "description": "Must mention server."}]
    prompt = build_prompt("artifact text", "markdown", criteria)
    assert "MCP Explanation" in prompt
    assert "Must mention server." in prompt


def test_build_prompt_contains_artifact_content():
    criteria = [{"name": "A", "max": 5, "description": "desc"}]
    prompt = build_prompt("my artifact content", "markdown", criteria)
    assert "my artifact content" in prompt
    assert "markdown" in prompt


# ---------------------------------------------------------------------------
# Task 4: call_portkey and main
# ---------------------------------------------------------------------------

from ai_evaluator import call_portkey, main


def test_call_portkey_returns_parsed_json():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = json.dumps({
        "criteria": [{"name": "A", "score": 4.0, "max": 5, "strength": "s", "gap": "g", "action": "a"}],
        "summary": "Good work."
    })
    # Portkey is imported inside call_portkey() — patch it in portkey_ai's namespace
    with patch("portkey_ai.Portkey") as MockPortkey:
        MockPortkey.return_value.chat.completions.create.return_value = mock_response
        result = call_portkey("some prompt", "fake-key")
    assert result["criteria"][0]["name"] == "A"
    assert result["summary"] == "Good work."


def test_main_no_api_key_writes_not_configured(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PORTKEY_API_KEY", raising=False)
    (tmp_path / ".grader").mkdir()
    (tmp_path / ".grader" / "SPEC.md").write_text(
        "---\nartifact: x.md\nartifact_type: markdown\nmax_score: 10\n---\n## C (max: 10)\nDesc\n"
    )
    main()
    feedback = json.loads((tmp_path / "ai-feedback.json").read_text())
    assert feedback["evaluated"] is False
    assert "PORTKEY_API_KEY" in feedback["reason"]


def test_main_artifact_not_found_writes_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PORTKEY_API_KEY", "fake-key")
    (tmp_path / ".grader").mkdir()
    (tmp_path / ".grader" / "SPEC.md").write_text(
        "---\nartifact: missing/file.md\nartifact_type: markdown\nmax_score: 10\n---\n## C (max: 10)\nDesc\n"
    )
    main()
    feedback = json.loads((tmp_path / "ai-feedback.json").read_text())
    assert feedback["evaluated"] is False
    assert "artifact not found" in feedback["reason"]
