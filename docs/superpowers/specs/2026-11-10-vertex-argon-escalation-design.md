# Design Document: Vertex AI Gemini 4 Argon Escalation Gate for Superpowers

**Date:** 2026-11-10  
**Scope:** Small Change / Workflow Skill  
**Target:** Antigravity Global Customizations (`~/.gemini/config/skills/vertex/`) & Superpowers Lifecycle Integration  

---

## 1. Intent & The Why
User possesses over 8,000,000 VND in Google Cloud Platform billing credits and wants to leverage Gemini 4 Argon (with Extended Thinking / Deep Reasoning) directly within Antigravity, while preserving default free inference for standard work. The user frequently uses the **Superpowers** suite (`brainstorming`, `writing-plans`, `systematic-debugging`, `test-driven-development`) and requires an intelligent, automated escalation mechanism with a short confirmation prompt to control credit expenditure.

---

## 2. Goals, Non-Goals, & Anti-Goals

### Goals
- Create a global Antigravity skill `vertex` (`SKILL.md` + execution script) invocable via `/vertex` or autonomous model detection.
- Seamlessly hook into Superpowers workflows when encountering heavy algorithmic tasks, combinatorial optimization, or cryptic concurrency/race-condition bugs.
- Implement an explicit **short confirmation gate** before any Vertex AI API call is dispatched, preventing unintended credit consumption.
- Utilize the user's active Google Cloud configuration: Project ID `project-b637a764-1cbb-4743-a3a`, location `us-central1`, and Application Default Credentials (ADC).

### Non-Goals
- Modifying Antigravity's closed internal UI dropdown (Model Selection button).
- Replacing standard fast responses for everyday CRUD, UI styling, or boilerplate code.

### Anti-Goals
- Calling Vertex AI silently in the background without user consent (would violate credit control).
- Disrupting or blocking standard Superpowers execution if the user declines the Vertex AI escalation.

---

## 3. Constraints
- **Billing / Credits:** Calls must use the configured project `project-b637a764-1cbb-4743-a3a` to debit from the billing account credits.
- **Latency:** Extended Thinking models take ~15-30 seconds to deliberate; user expectation must be calibrated in the prompt.
- **Environment:** Windows PowerShell, Python 3.11 with `google-genai` installed.

---

## 4. Approaches Considered

1. **Integrated Escalation Gate across Superpowers (Selected):**
   - *Description:* Skill `vertex` acts as an on-demand and autonomously triggered thinking tier. When a Superpowers phase reaches high-complexity limits, Agent pauses and asks 1 short confirmation question before delegating to Gemini 4 Argon.
   - *Trade-offs:* Optimal balance between convenience, intelligence, and credit safety. Chosen by user.

2. **Dedicated Plan Subagent (`vertex-argon-agent`):**
   - *Description:* Tasks tagged in implementation plans are dispatched to a specialized subagent.
   - *Trade-offs:* Clean separation, but rigid and only useful during multi-step plan execution.

3. **Strict Manual Invocation (`/vertex` only):**
   - *Description:* Only runs when explicitly typed by user.
   - *Trade-offs:* Safe, but requires the user to constantly judge problem difficulty manually.

---

## 5. Technical Specification

### A. Skill Structure (`~/.gemini/config/skills/vertex/`)
```text
~/.gemini/config/skills/vertex/
├── SKILL.md            # Frontmatter trigger rules & execution protocol
└── scripts/
    └── run_argon.py    # Python worker calling Gemini 4 Argon with thinking config
```

### B. Trigger & Confirmation Protocol
When any Superpowers workflow or general query meets one of these criteria:
- High-order algorithmic problem (dynamic programming, graph theory, NP-hard problems).
- Mathematical proofs or formal invariant verification.
- Root-cause analysis of deep, elusive bugs after standard systematic debugging.

**Mandatory Gate:**
Agent outputs:
> *"Tác vụ này có độ phức tạp thuật toán cao. Bạn có muốn kích hoạt Gemini 4 Argon (Vertex AI Extended Thinking, ước tính ~25s, trừ vào credits) không? [Có/Không]"*

- **If User Approves:** Agent invokes `run_argon.py` with the context/prompt, presents the reasoning steps and synthesized solution, then resumes the Superpowers workflow.
- **If User Declines:** Agent continues immediately using the standard free model (`Gemini 3.8 Flash High`).

### C. Runner Script Specification (`run_argon.py`)
- Python 3.11 with `google.genai.Client(vertexai=True)`.
- Model: `gemini-4-argon` (with fallback to `gemini-2.5-pro` if Argon publisher model is regionalized).
- Thinking config: Enable thinking budget / extended reasoning.
- Output: Returns structured thinking summary and solution code.

---

## 6. What's Left to the Builder
- Write `SKILL.md` in `~/.gemini/config/skills/vertex/SKILL.md`.
- Implement `run_argon.py` in `~/.gemini/config/skills/vertex/scripts/run_argon.py`.
- Run an end-to-end verification test to ensure the confirmation gate works and execution returns clean output.
