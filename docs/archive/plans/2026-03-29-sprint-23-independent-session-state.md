# Sprint 23 Independent Session State Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move long-session persisted state out of `TraceRecord.llm_call` into a dedicated session-state model while preserving trace fallback compatibility.

**Architecture:** Add a small `SessionState` ORM model keyed by `session_id`, then switch recovery to prefer it over trace state. Keep `persisted_session_state` in trace as a compatibility copy while layered-context assembly and runtime behavior continue unchanged.

**Tech Stack:** Python, FastAPI backend, SQLAlchemy async ORM, unittest

---

### Task 1: Define state-model expectations

**Files:**
- Create: `app/backend/tests/test_session_state_store.py`
- Modify: `app/backend/tests/test_response_state.py`

**Step 1: Write the failing tests**

- Add tests for loading the current session state from a dedicated model.
- Add tests proving trace is only used as fallback when dedicated state is missing.

**Step 2: Run tests to verify they fail**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_store.py; & .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_response_state.py`

Expected: FAIL because the dedicated model and new load path do not exist yet.

### Task 2: Add the dedicated session-state model

**Files:**
- Modify: `app/backend/app/models/tables.py`
- Create: `app/backend/app/session_state_store.py`
- Test: `app/backend/tests/test_session_state_store.py`

**Step 1: Implement minimal ORM model and helpers**

- Add `SessionState` keyed by `session_id`.
- Store `current_focus`, `semantic_summary`, `stable_state`, and timestamps.
- Add minimal `load` / `save` helper functions.

**Step 2: Run targeted tests**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_store.py`

Expected: PASS.

### Task 3: Switch recovery and write paths

**Files:**
- Modify: `app/backend/app/main.py`
- Modify: `app/backend/app/agent/xinque.py`
- Modify: `app/backend/tests/test_xinque_trace.py`
- Modify: `app/backend/tests/test_response_state.py`

**Step 1: Write the failing tests**

- Assert `_load_previous_session_state(...)` prefers dedicated state and falls back to trace.
- Assert chat flow still emits a compatibility copy into trace.

**Step 2: Implement**

- Update load path to prefer `SessionState`.
- Save dedicated state after each successful chat turn.
- Keep trace copy for backward compatibility.

**Step 3: Verify**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_response_state.py; & .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_trace.py`

Expected: PASS.

### Task 4: Full regression and docs

**Files:**
- Modify: `evaluations/sprint-23-eval.md`
- Modify: `docs/design/product-plan-v2-implementation-status.md`

**Step 1: Run backend regression**

Run: `& .\app\backend\.venv\Scripts\python.exe -m unittest discover -s app\backend\tests -p "test_*.py"`

Expected: PASS.

**Step 2: Update evaluation and status docs**

- Record dedicated-state model, fallback behavior, and any intentionally deferred items.
