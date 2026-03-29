# Sprint 25 State Read Models Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add read-side helpers and API endpoints for current session state, session state history, and session phase timelines.

**Architecture:** Reuse `SessionState`, `SessionStateHistory`, and trace `phase_timeline` as existing write sources. Add lightweight read helpers and API endpoints in `main.py`, keeping chat writes unchanged.

**Tech Stack:** Python, FastAPI backend, SQLAlchemy async ORM, unittest

---

### Task 1: Define read-side expectations

**Files:**
- Modify: `app/backend/tests/test_session_state_store.py`
- Modify: `app/backend/tests/test_trace_api.py`
- Create: `app/backend/tests/test_session_state_api.py`

**Step 1: Write the failing tests**

- Add tests for current-state reads, history reads, and phase timeline serialization.

**Step 2: Run tests to verify they fail**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_store.py; & .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py; & .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`

Expected: FAIL because read helpers and endpoints do not exist yet.

### Task 2: Implement read helpers and serializers

**Files:**
- Modify: `app/backend/app/session_state_store.py`
- Modify: `app/backend/app/trace_helpers.py`

**Step 1: Implement**

- Add current-state and history serializers/readers.
- Add helper to flatten phase timelines from trace records.

**Step 2: Verify**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_store.py; & .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py`

Expected: PASS.

### Task 3: Add API endpoints

**Files:**
- Modify: `app/backend/app/main.py`
- Test: `app/backend/tests/test_session_state_api.py`

**Step 1: Implement**

- Add endpoint for current state.
- Add endpoint for state history.
- Add endpoint for session timeline.

**Step 2: Verify**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`

Expected: PASS.

### Task 4: Full regression and docs

**Files:**
- Modify: `evaluations/sprint-25-eval.md`
- Modify: `docs/design/product-plan-v2-implementation-status.md`

**Step 1: Run regression**

Run: `& .\app\backend\.venv\Scripts\python.exe -m unittest discover -s app\backend\tests -p "test_*.py"`

Expected: PASS.

**Step 2: Update docs**

- Record new read-side endpoints and remaining gaps.
