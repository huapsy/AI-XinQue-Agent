# Sprint 11 Trace Observability Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a minimal per-turn trace system so XinQue chat handling can be diagnosed through stored input safety, LLM, tool, output safety, and latency data.

**Architecture:** Introduce a `TraceRecord` persistence model plus a lightweight trace helper module for building redacted trace payloads. First implementation records one trace per `POST /api/chat` request and exposes a simple `GET /api/sessions/{session_id}/traces` query endpoint. Tool-level detail is captured from the agent loop through an optional trace collector passed into `xinque.chat()`.

**Tech Stack:** Python, FastAPI, SQLAlchemy async ORM, Alembic, unittest

---

### Task 1: Add failing tests for trace payload shaping

**Files:**
- Create: `app/backend/tests/test_trace_helpers.py`
- Create: `app/backend/tests/test_trace_api.py`

**Step 1: Write failing tests**

- verify long text is redacted/truncated
- verify tool call trace entries include tool name, success, and latency
- verify trace query endpoint returns session traces in order

**Step 2: Run tests to verify they fail**

Expected: FAIL because trace helper/model/endpoint do not exist yet

### Task 2: Implement trace model and helper module

**Files:**
- Modify: `app/backend/app/models/tables.py`
- Create: `app/backend/app/trace_helpers.py`
- Create: `app/backend/alembic/versions/<new>_add_traces_table.py`

**Step 1: Add `TraceRecord` model**

- session_id
- turn_number
- input_safety
- llm_call
- output_safety
- total_latency_ms
- created_at

**Step 2: Add helper functions**

- text redaction/truncation
- tool trace entry shaping
- final trace payload assembly

### Task 3: Capture traces in main chat flow

**Files:**
- Modify: `app/backend/app/main.py`
- Modify: `app/backend/app/agent/xinque.py`

**Step 1: Add trace collector path**

- pass collector into `xinque.chat()`
- collect tool call metadata there

**Step 2: Persist one trace per request**

- normal chat trace
- crisis short-circuit trace

### Task 4: Add query endpoint

**Files:**
- Modify: `app/backend/app/main.py`

**Step 1: Add `GET /api/sessions/{session_id}/traces`**

- return trace list for diagnostics

### Task 5: Verify Sprint 11 slice

**Files:**
- modify only if verification exposes regressions

**Step 1: Run tests**

```bash
cd app/backend
<python> -m unittest discover -s tests -p 'test_*.py'
```

**Step 2: Run syntax verification**

```bash
cd app/backend
<python> -m py_compile app/trace_helpers.py app/main.py app/agent/xinque.py app/models/tables.py
```

**Step 3: Summarize remaining gaps**

- note that full observability dashboards remain deferred
