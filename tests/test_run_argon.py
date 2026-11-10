"""
Unit tests for Vertex AI Argon Runner Script (run_argon.py).
Tests client initialization, thinking execution, fallback logic, CLI parsing, and dry-run mode.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Ensure skill script directory is in sys.path
SCRIPT_DIR = Path("C:/Users/Admin/.gemini/config/skills/vertex/scripts")
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def test_imports_and_constants():
    """Verify script imports and default project/location/model constants."""
    import run_argon

    assert run_argon.PROJECT_ID == "project-b637a764-1cbb-4743-a3a"
    assert run_argon.DEFAULT_LOCATION == "us-central1"
    assert run_argon.DEFAULT_MODEL == "gemini-4-argon"
    assert run_argon.FALLBACK_MODEL == "gemini-2.5-pro"


def test_get_vertex_client():
    """Verify get_vertex_client initializes genai.Client with vertexai=True."""
    import run_argon

    with patch("run_argon.genai.Client") as mock_client_cls:
        client = run_argon.get_vertex_client(project="test-proj", location="us-east1")
        mock_client_cls.assert_called_once_with(
            vertexai=True,
            project="test-proj",
            location="us-east1"
        )
        assert client == mock_client_cls.return_value


def test_execute_deep_thinking_dry_run():
    """Verify dry_run=True returns valid structured output without calling API."""
    import run_argon

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        result = run_argon.execute_deep_thinking(
            prompt="Prove that P != NP",
            model="gemini-4-argon",
            dry_run=True
        )

        assert isinstance(result, dict)
        assert "solution" in result
        assert "model_used" in result
        assert "thinking_summary" in result
        assert result["model_used"] == "gemini-4-argon"
        assert "DRY RUN" in result["solution"]
        # API should NOT have been called in dry run
        mock_client.models.generate_content.assert_not_called()


def test_execute_deep_thinking_success():
    """Verify successful execution with primary model and thought extraction."""
    import run_argon

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock candidate parts with thought and text
        mock_thought_part = MagicMock()
        mock_thought_part.thought = True
        mock_thought_part.text = "Step 1: Analyze algorithmic complexity."

        mock_answer_part = MagicMock()
        mock_answer_part.thought = False
        mock_answer_part.text = "O(N log N) solution via segment tree."

        mock_content = MagicMock()
        mock_content.parts = [mock_thought_part, mock_answer_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        mock_response.text = "O(N log N) solution via segment tree."

        mock_client.models.generate_content.return_value = mock_response

        result = run_argon.execute_deep_thinking(
            prompt="Find optimal MST",
            context="Graph has 10^5 nodes",
            model="gemini-4-argon",
            dry_run=False
        )

        assert result["model_used"] == "gemini-4-argon"
        assert "Step 1: Analyze algorithmic complexity." in result["thinking_summary"]
        assert "O(N log N) solution via segment tree." in result["solution"]
        mock_client.models.generate_content.assert_called_once()


def test_execute_deep_thinking_fallback():
    """Verify fallback from gemini-4-argon to gemini-2.5-pro on 404/NotFound."""
    import run_argon
    from google.genai.errors import APIError

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # First call fails with 404 NOT_FOUND
        not_found_err = APIError(404, {"error": {"message": "Publisher Model gemini-4-argon not found"}})

        # Second call succeeds
        mock_response = MagicMock()
        mock_response.candidates = []
        mock_response.text = "Fallback solution from 2.5 Pro"

        mock_client.models.generate_content.side_effect = [not_found_err, mock_response]

        result = run_argon.execute_deep_thinking(
            prompt="Solve NP-hard problem",
            model="gemini-4-argon",
            dry_run=False
        )

        assert mock_client.models.generate_content.call_count == 2
        # First call was gemini-4-argon, second call was gemini-2.5-pro
        call_models = [c.kwargs.get("model") for c in mock_client.models.generate_content.call_args_list]
        assert call_models == ["gemini-4-argon", "gemini-2.5-pro"]
        assert result["model_used"] == "gemini-2.5-pro"
        assert result["solution"] == "Fallback solution from 2.5 Pro"


def test_execute_deep_thinking_non_fallback_error():
    """Verify non-404 error (e.g. 403 Forbidden or 400 Bad Request) is raised and not masked."""
    import run_argon
    from google.genai.errors import APIError

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        permission_err = APIError(403, {"error": {"message": "Permission denied"}})
        mock_client.models.generate_content.side_effect = permission_err

        with pytest.raises(APIError):
            run_argon.execute_deep_thinking(
                prompt="Secret query",
                model="gemini-4-argon"
            )


def test_cli_parsing(tmp_path):
    """Verify CLI argument parser handling of prompt, context, context-file, and dry-run."""
    import run_argon

    # Test basic prompt
    args = run_argon.parse_args(["--prompt", "Calculate pi"])
    assert args.prompt == "Calculate pi"
    assert args.dry_run is False
    assert args.model == "gemini-4-argon"

    # Test context file
    ctx_file = tmp_path / "context.txt"
    ctx_file.write_text("Context information here", encoding="utf-8")

    args = run_argon.parse_args([
        "--prompt", "Review code",
        "--context-file", str(ctx_file),
        "--dry-run",
        "--model", "gemini-2.5-pro"
    ])
    assert args.prompt == "Review code"
    assert args.context_file == str(ctx_file)
    assert args.dry_run is True
    assert args.model == "gemini-2.5-pro"


def test_cli_main_dry_run(capsys):
    """Verify running CLI with --dry-run prints clean markdown status."""
    import run_argon

    test_args = ["run_argon.py", "--prompt", "Quick dry-run test", "--dry-run"]
    with patch.object(sys, "argv", test_args):
        ret_code = run_argon.main()
        assert ret_code == 0

    captured = capsys.readouterr()
    assert "Vertex AI Extended Thinking" in captured.out
    assert "DRY RUN" in captured.out
