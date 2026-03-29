# Sprint 21 Long Session Governance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build layered long-session context management with semantic compression and clear separation between current-turn focus and historical background.

**Architecture:** Add a small session-context layer that assembles working memory, stable state, retrieval hints, and semantic summary before `xinque.chat()` calls the model. Reuse existing profile, formulation, intervention, recall, and memory primitives; keep storage changes out of scope.

**Tech Stack:** Python, FastAPI backend, SQLAlchemy async ORM, unittest

---

### Task 1: Define context-layer expectations

**Files:**
- Create: `app/backend/tests/test_session_context.py`
- Modify: `app/backend/tests/test_xinque_long_session.py`

**Step 1: Write the failing tests**

- Add tests for a layered context builder that returns `working_memory`, `stable_state`, `retrieval_context`, `semantic_summary`, and `current_focus`.
- Add tests proving long-session compression prefers semantic sections over raw concatenation.

**Step 2: Run tests to verify they fail**

Run: `& .\app\backend\.venv\Scripts\python.exe -m unittest app.backend.tests.test_session_context app.backend.tests.test_xinque_long_session`

Expected: FAIL because the new context builder and semantic summary behavior do not exist yet.

### Task 2: Implement layered context assembly

**Files:**
- Create: `app/backend/app/session_context.py`
- Modify: `app/backend/app/agent/xinque.py`

**Step 1: Write minimal implementation**

- Add helpers to derive current focus from latest user message.
- Build stable state from profile snapshot, formulation, recent interventions, and last session summary.
- Build retrieval context as a boundary object that explains when to rely on `recall_context`, `search_memory`, and semantic summary.
- Replace `_compact_history` with context-aware working memory assembly.

**Step 2: Run targeted tests**

Run: `& .\app\backend\.venv\Scripts\python.exe -m unittest app.backend.tests.test_session_context app.backend.tests.test_xinque_long_session`

Expected: PASS.

### Task 3: Wire long-session state into recall flows

**Files:**
- Modify: `app/backend/app/agent/tools/recall_context.py`
- Modify: `app/backend/tests/test_recall_context.py`

**Step 1: Write the failing tests**

- Extend recall-context coverage for layered stable state fields and explicit retrieval boundaries.

**Step 2: Implement**

- Return a structure that can be reused as stable state input without overloading retrieval memories.

**Step 3: Verify**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_recall_context.py`

Expected: PASS.

### Task 4: Regression and docs

**Files:**
- Modify: `evaluations/sprint-21-eval.md`
- Modify: `docs/design/product-plan-v2-implementation-status.md`

**Step 1: Run backend regression**

Run: `& .\app\backend\.venv\Scripts\python.exe -m unittest discover -s app\backend\tests -p "test_*.py"`

Expected: PASS.

**Step 2: Update evaluation and status docs**

- Record what is implemented, tested, and intentionally deferred.
