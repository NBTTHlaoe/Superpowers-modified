# Vertex AI Gemini 4 Argon Escalation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and register a global Antigravity skill (`vertex`) powered by Gemini 4 Argon (with Extended Thinking) on GCP Vertex AI, featuring an explicit short confirmation gate integrated with the Superpowers lifecycle.

**Architecture:** A lightweight Python runner script (`run_argon.py`) connects to Vertex AI using `google-genai` and ADC under GCP project `project-b637a764-1cbb-4743-a3a`. An Antigravity skill (`SKILL.md`) defines semantic trigger conditions (algorithmic complexity, formal logic, cryptic bugs) and mandates a short confirmation prompt before invoking the runner, returning deep reasoning steps and the synthesized solution.

**Tech Stack:** Python 3.11, `google-genai`, Google Cloud Vertex AI, Antigravity Customizations (`~/.gemini/config/skills/vertex/`).

**Spec:** [docs/superpowers/specs/2026-11-10-vertex-argon-escalation-design.md](file:///C:/Dev/Cloud/docs/superpowers/specs/2026-11-10-vertex-argon-escalation-design.md)

## Global Constraints

- **Active GCP Project:** `project-b637a764-1cbb-4743-a3a`
- **Default Location:** `us-central1`
- **Primary Model:** `gemini-4-argon` (with automatic fallback to `gemini-2.5-pro` if Argon region is unavailable)
- **Mandatory Confirmation Copy:** *"Tác vụ này có độ phức tạp thuật toán cao. Bạn có muốn kích hoạt Gemini 4 Argon (Vertex AI Extended Thinking, ước tính ~25s, trừ vào credits) không? [Có/Không]"*
- **Skill Path:** `C:\Users\Admin\.gemini\config\skills\vertex\`
- **Encoding:** UTF-8 throughout for all prompts, scripts, and Markdown files.

## Review Focus

1. **Model Regional Availability:** If `gemini-4-argon` returns 404 in `us-central1`, the runner must automatically fallback to `gemini-2.5-pro` without crashing.
2. **User Denial Handling:** If the user declines ("Không"), the Agent must seamlessly continue with the free session model without breaking the Superpowers chain.
3. **Unicode / Vietnamese Encoding:** Full UTF-8 support on Windows PowerShell without mojibake.
4. **Network / Timeout Resilience:** Timeout during extended thinking (>60s) must produce a clean message rather than an unhandled stack trace.
5. **No Undue Escalation:** Standard CRUD, syntax fixes, and boilerplate must never trigger the confirmation prompt.

---

### Task 1: Implement the Vertex AI Argon Runner Script

**Files:**
- Create: `C:\Users\Admin\.gemini\config\skills\vertex\scripts\run_argon.py`
- Create: `C:\Dev\Cloud\tests\test_run_argon.py`

**Interfaces:**
- Produces: CLI interface `python run_argon.py --prompt "..." [--context "..." / --context-file "..."] [--model "..."]` returning formatted Markdown output with reasoning summary and solution.
- Function: `execute_deep_thinking(prompt: str, context: Optional[str] = None, model: str = "gemini-4-argon") -> Dict[str, Any]`

- [ ] **Step 1: Write the failing unit test for `run_argon.py`**

```python
# C:\Dev\Cloud\tests\test_run_argon.py
import pytest
import sys
from pathlib import Path

# Add skill script directory to sys.path
sys.path.insert(0, str(Path("C:/Users/Admin/.gemini/config/skills/vertex/scripts")))

def test_imports_and_client_initialization():
    from run_argon import get_vertex_client, PROJECT_ID
    assert PROJECT_ID == "project-b637a764-1cbb-4743-a3a"
    client = get_vertex_client()
    assert client is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest C:\Dev\Cloud\tests\test_run_argon.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'run_argon'`

- [ ] **Step 3: Implement `run_argon.py` in `C:\Users\Admin\.gemini\config\skills\vertex\scripts\run_argon.py`**

Implement `get_vertex_client()`, `execute_deep_thinking(prompt, context, model)` with fallback from `gemini-4-argon` to `gemini-2.5-pro`, and CLI argument parsing (`--prompt`, `--context`, `--model`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest C:\Dev\Cloud\tests\test_run_argon.py -v`  
Expected: PASS

- [ ] **Step 5: Commit task 1 files**

```bash
git add tests/test_run_argon.py
git commit -m "feat(vertex): implement Vertex AI Argon runner script with fallback"
```

---

### Task 2: Author the Global `vertex` Skill for Antigravity & Superpowers

**Files:**
- Create: `C:\Users\Admin\.gemini\config\skills\vertex\SKILL.md`

**Interfaces:**
- Produces: Antigravity Skill metadata with triggers and execution instructions.
- Consumes: `C:\Users\Admin\.gemini\config\skills\vertex\scripts\run_argon.py`

- [x] **Step 1: Draft the SKILL.md specification with YAML frontmatter**

Write `C:\Users\Admin\.gemini\config\skills\vertex\SKILL.md`:
- `name: vertex`
- `description`: "Escalates complex algorithmic problems, NP-hard challenges, deep mathematical proofs, or cryptic elusive bugs to Gemini 4 Argon on Vertex AI with Extended Thinking. Triggers manually via /vertex or autonomously when problem complexity exceeds standard limits. Always requires a short confirmation before proceeding."
- Include exact instructions for the confirmation prompt, execution command, and handling of user response.

- [x] **Step 2: Verify skill validation and syntax**

Verify that `SKILL.md` adheres to Antigravity skill structure (YAML frontmatter with valid `name` and `description`, markdown body linking to `scripts/run_argon.py`).

- [x] **Step 3: Commit task 2**

```bash
git commit --allow-empty -m "feat(vertex): author global vertex skill specification"
```

---

### Task 3: End-to-End Verification and Simulation

**Files:**
- Create: `C:\Dev\Cloud\tests\test_vertex_escalation_flow.py`

**Interfaces:**
- Verifies the full pipeline: prompt intake -> confirmation gate -> model runner execution -> output formatting.

- [ ] **Step 1: Write integration verification test**

Verify that running `python run_argon.py --prompt "Test prompt" --dry-run` or against Vertex AI produces structured output without unhandled exceptions.

- [ ] **Step 2: Execute end-to-end dry run**

Run: `python C:\Users\Admin\.gemini\config\skills\vertex\scripts\run_argon.py --prompt "Kiểm tra kết nối" --dry-run`  
Expected: Clean status message confirming configuration and ready state.

- [ ] **Step 3: Final commit**

```bash
git add tests/test_vertex_escalation_flow.py
git commit -m "test(vertex): verify end-to-end escalation flow"
```
