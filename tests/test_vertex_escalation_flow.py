"""
End-to-End Verification and Simulation Tests for Vertex AI Gemini 4 Argon Escalation.
Verifies the integration pipeline:
  1. SKILL.md existence, YAML frontmatter, and mandatory confirmation copy.
  2. Subprocess dry-run execution via Python 3.11.
  3. Prompt, context, and context-file argument formatting.
  4. End-to-end fallback handling (gemini-4-argon -> gemini-2.5-pro) and error recovery.
  5. Escalation gate decision flow simulation (Superpowers integration).
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
import yaml

# Path references
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = Path("C:/Users/Admin/.gemini/config/skills/vertex")
SKILL_FILE = SKILL_DIR / "SKILL.md"
RUN_ARGON_SCRIPT = SKILL_DIR / "scripts" / "run_argon.py"

# System Python 3.11 executable path with fallback to sys.executable
PYTHON_311 = Path(r"C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe")
PYTHON_EXE = str(PYTHON_311) if PYTHON_311.exists() else sys.executable

# Add runner script directory to sys.path for direct module import
if str(RUN_ARGON_SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(RUN_ARGON_SCRIPT.parent))

MANDATORY_CONFIRMATION_PHRASE = (
    "Tác vụ này có độ phức tạp thuật toán cao. Bạn có muốn kích hoạt Gemini 4 Argon "
    "(Vertex AI Extended Thinking, ước tính ~25s, trừ vào credits) không? [Có/Không]"
)


# ==============================================================================
# 1. SKILL.md Specification and Metadata Verification
# ==============================================================================

def test_skill_file_existence_and_yaml_frontmatter():
    """Verify that SKILL.md exists, has valid YAML frontmatter, and correct name."""
    assert SKILL_FILE.exists(), f"SKILL.md does not exist at {SKILL_FILE}"
    content = SKILL_FILE.read_text(encoding="utf-8")

    # Frontmatter must start and end with '---'
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter '---'"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md frontmatter must be enclosed in '---' delimiters"

    frontmatter_raw = parts[1]
    metadata = yaml.safe_load(frontmatter_raw)
    assert isinstance(metadata, dict), "Parsed YAML frontmatter must be a dictionary"

    # Required fields
    assert metadata.get("name") == "vertex", f"Skill name must be 'vertex', got {metadata.get('name')}"
    description = metadata.get("description", "")
    assert description, "Skill description in frontmatter must not be empty"
    assert "Gemini 4 Argon" in description or "gemini-4-argon" in description.lower()
    assert "Extended Thinking" in description or "Vertex AI" in description


def test_skill_mandatory_confirmation_copy():
    """Verify that SKILL.md contains the exact required confirmation gate phrasing."""
    content = SKILL_FILE.read_text(encoding="utf-8")
    assert MANDATORY_CONFIRMATION_PHRASE in content, (
        "SKILL.md must contain the exact mandatory confirmation copy:\n"
        f"'{MANDATORY_CONFIRMATION_PHRASE}'"
    )
    # Check that guidance covers both 'Có' (approval) and 'Không' (denial) paths
    assert "Nếu người dùng chọn \"Có\"" in content
    assert "Nếu người dùng chọn \"Không\"" in content


# ==============================================================================
# 2. CLI Dry Run Invocation via Subprocess (Python 3.11)
# ==============================================================================

def test_cli_dry_run_subprocess_invocation():
    """Verify CLI dry run execution via subprocess using Python 3.11 returns code 0 and valid markdown."""
    cmd = [
        PYTHON_EXE,
        str(RUN_ARGON_SCRIPT),
        "--prompt", "End-to-end dry run verification",
        "--dry-run"
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False
    )

    assert proc.returncode == 0, f"Subprocess failed with code {proc.returncode}. Stderr: {proc.stderr}"
    stdout = proc.stdout

    # Verify structured dry run output markers
    assert "# Vertex AI Extended Thinking Output" in stdout
    assert "Model Used:" in stdout
    assert "`gemini-4-argon`" in stdout
    assert "Dry Run Verified" in stdout
    assert "project-b637a764-1cbb-4743-a3a" in stdout
    assert "us-central1" in stdout
    assert "DRY RUN OK" in stdout


# ==============================================================================
# 3. Prompt and Context Formatting Options
# ==============================================================================

def test_cli_prompt_and_inline_context_subprocess():
    """Verify CLI handles --prompt and --context together in dry run mode."""
    prompt_text = "Find optimal TSP tour"
    context_text = "Distance matrix: [[0, 2], [2, 0]]"

    cmd = [
        PYTHON_EXE,
        str(RUN_ARGON_SCRIPT),
        "--prompt", prompt_text,
        "--context", context_text,
        "--dry-run"
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False
    )

    assert proc.returncode == 0, f"Failed with stderr: {proc.stderr}"
    assert "Dry Run Verified" in proc.stdout


def test_cli_context_file_reading_subprocess(tmp_path):
    """Verify CLI --context-file reads existing file content correctly."""
    context_file = tmp_path / "algorithm_context.py"
    context_file.write_text(
        "class Node:\n    def __init__(self, val):\n        self.val = val\n",
        encoding="utf-8"
    )

    cmd = [
        PYTHON_EXE,
        str(RUN_ARGON_SCRIPT),
        "--prompt", "Optimize tree traversal algorithm",
        "--context-file", str(context_file),
        "--dry-run"
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False
    )

    assert proc.returncode == 0, f"Context-file run failed: {proc.stderr}"
    assert "Dry Run Verified" in proc.stdout


def test_internal_prompt_and_context_assembly():
    """Verify execute_deep_thinking formats combined prompt and context correctly when calling API."""
    import run_argon

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock API response
        mock_response = MagicMock()
        mock_response.candidates = []
        mock_response.text = "Synthesized solution"
        mock_client.models.generate_content.return_value = mock_response

        # Scenario 1: With context
        run_argon.execute_deep_thinking(
            prompt="Compute convex hull",
            context="Points: [(0,0), (1,1), (2,2)]",
            model="gemini-4-argon",
            dry_run=False
        )

        call_args = mock_client.models.generate_content.call_args
        contents_arg = call_args.kwargs.get("contents")
        assert "### Context:\nPoints: [(0,0), (1,1), (2,2)]" in contents_arg
        assert "### Task / Prompt:\nCompute convex hull" in contents_arg

        # Scenario 2: Without context
        mock_client.models.generate_content.reset_mock()
        run_argon.execute_deep_thinking(
            prompt="Prove Fermat's Last Theorem for n=3",
            context=None,
            model="gemini-4-argon",
            dry_run=False
        )

        call_args2 = mock_client.models.generate_content.call_args
        contents_arg2 = call_args2.kwargs.get("contents")
        assert contents_arg2 == "Prove Fermat's Last Theorem for n=3"


# ==============================================================================
# 4. Fallback Logic and Error Handling End-to-End
# ==============================================================================

def test_runner_fallback_flow_end_to_end(capsys):
    """Verify end-to-end fallback from gemini-4-argon to gemini-2.5-pro when Argon returns 404."""
    import run_argon
    from google.genai.errors import APIError

    with patch("run_argon.get_vertex_client") as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # 404 error on primary call
        not_found_err = APIError(404, {"error": {"message": "Model gemini-4-argon not found in us-central1"}})

        # Success on fallback call
        fallback_resp = MagicMock()
        fallback_resp.candidates = []
        fallback_resp.text = "Optimized DP algorithm in O(N^2) via gemini-2.5-pro."

        mock_client.models.generate_content.side_effect = [not_found_err, fallback_resp]

        ret_code = run_argon.main(["--prompt", "Solve 3D knapsack problem"])

        assert ret_code == 0
        captured = capsys.readouterr()

        # Check that fallback message was written to stderr
        assert "Falling back to 'gemini-2.5-pro'" in captured.err
        # Check that final output reports fallback model
        assert "`gemini-2.5-pro`" in captured.out
        assert "Optimized DP algorithm in O(N^2)" in captured.out
        assert mock_client.models.generate_content.call_count == 2


def test_runner_missing_prompt_error_handling(capsys):
    """Verify error handling when --prompt is missing without --dry-run."""
    import run_argon

    with patch.object(sys.stdin, "isatty", return_value=True):
        ret_code = run_argon.main([])
        assert ret_code == 1

        captured = capsys.readouterr()
        assert "Error: --prompt is required" in captured.err


def test_runner_general_exception_handling(capsys):
    """Verify fatal/unhandled exceptions exit with code 2 and clean error message."""
    import run_argon

    with patch("run_argon.execute_deep_thinking", side_effect=ConnectionError("Vertex AI endpoint unreachable")):
        ret_code = run_argon.main(["--prompt", "Test connection crash"])
        assert ret_code == 2

        captured = capsys.readouterr()
        assert "Error executing deep thinking: Vertex AI endpoint unreachable" in captured.err


def test_cli_output_file_export(tmp_path):
    """Verify --output writes Markdown output directly to the specified file."""
    import run_argon

    output_file = tmp_path / "results" / "argon_solution.md"
    test_args = [
        "run_argon.py",
        "--prompt", "Generate solution for graph coloring",
        "--dry-run",
        "--output", str(output_file)
    ]

    with patch.object(sys, "argv", test_args):
        ret_code = run_argon.main()
        assert ret_code == 0

    assert output_file.exists(), f"Output file was not created at {output_file}"
    content = output_file.read_text(encoding="utf-8")
    assert "# Vertex AI Extended Thinking Output" in content
    assert "DRY RUN OK" in content


# ==============================================================================
# 5. Simulation of the Escalation Gate Protocol (Superpowers Lifecycle)
# ==============================================================================

def simulate_escalation_gate(
    task_description: str,
    complexity_is_high: bool,
    user_response: str,
    run_fn=None,
    base_model_fn=None
) -> dict:
    """
    Simulates the decision gate logic prescribed by SKILL.md.
    - If complexity is high, ask confirmation phrase.
    - If user approves ('có', 'yes', 'y'), dispatch to run_fn (Vertex Argon).
    - If user declines ('không', 'no', 'k'), dispatch to base_model_fn (standard free session).
    """
    if not complexity_is_high:
        return {"action": "standard_execution", "result": base_model_fn(task_description)}

    # Prompt user with mandatory phrase
    gate_prompt = MANDATORY_CONFIRMATION_PHRASE
    clean_resp = user_response.strip().lower()

    if clean_resp in {"có", "co", "yes", "y", "ok", "đồng ý"}:
        return {
            "gate_prompt": gate_prompt,
            "action": "escalated_vertex_argon",
            "result": run_fn(task_description) if run_fn else "vertex_executed"
        }
    else:
        return {
            "gate_prompt": gate_prompt,
            "action": "declined_fallback_base",
            "result": base_model_fn(task_description) if base_model_fn else "base_executed"
        }


def test_escalation_gate_user_approves_triggers_runner():
    """Verify that user approval ('Có') executes the Vertex Argon runner."""
    mock_run = MagicMock(return_value={"model": "gemini-4-argon", "solution": "O(N log N) flow"})
    mock_base = MagicMock()

    outcome = simulate_escalation_gate(
        task_description="Solve NP-hard Traveling Salesperson with 1000 nodes",
        complexity_is_high=True,
        user_response="Có",
        run_fn=mock_run,
        base_model_fn=mock_base
    )

    assert outcome["action"] == "escalated_vertex_argon"
    assert outcome["gate_prompt"] == MANDATORY_CONFIRMATION_PHRASE
    mock_run.assert_called_once()
    mock_base.assert_not_called()


def test_escalation_gate_user_declines_uses_base_model():
    """Verify that user decline ('Không') falls back cleanly to the base session model without error."""
    mock_run = MagicMock()
    mock_base = MagicMock(return_value="Standard heuristic solution")

    outcome = simulate_escalation_gate(
        task_description="Solve NP-hard Traveling Salesperson with 1000 nodes",
        complexity_is_high=True,
        user_response="Không",
        run_fn=mock_run,
        base_model_fn=mock_base
    )

    assert outcome["action"] == "declined_fallback_base"
    assert outcome["gate_prompt"] == MANDATORY_CONFIRMATION_PHRASE
    assert outcome["result"] == "Standard heuristic solution"
    mock_run.assert_not_called()
    mock_base.assert_called_once()
