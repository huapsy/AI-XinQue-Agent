# Sprint 10 Episodic Memory Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add minimal episodic memory capture and retrieval so XinQue can recall specific past events beyond last-session summary.

**Architecture:** Introduce an `EpisodicMemory` model plus a lightweight memory helper module. First implementation uses deterministic token-based similarity and JSON embeddings so the storage and retrieval contracts are in place without blocking on external embedding services. Register `search_memory()` as a tool and keep `recall_context()` focused on stable context only.

**Tech Stack:** Python, SQLAlchemy async ORM, Alembic, unittest

---

### Task 1: Add failing tests for memory capture and retrieval

**Files:**
- Create: `app/backend/tests/test_memory_helpers.py`
- Create: `app/backend/tests/test_search_memory.py`

**Step 1: Write the failing tests**

- Verify important event messages produce a memory candidate
- Verify low-information messages do not
- Verify similar queries retrieve the expected memory first
- Verify duplicate events are not stored repeatedly

**Step 2: Run tests to verify they fail**

Run:

```bash
cd app/backend
<python> -m unittest discover -s tests -p 'test_*.py'
```

Expected: FAIL because memory helpers, model, and tool do not exist yet

### Task 2: Implement episodic memory model and helpers

**Files:**
- Modify: `app/backend/app/models/tables.py`
- Create: `app/backend/app/memory_helpers.py`
- Create: `app/backend/alembic/versions/<new>_add_episodic_memories_table.py`

**Step 1: Add model**

- `EpisodicMemory` table with user/session/content/topic/emotions/embedding/created_at

**Step 2: Add helper functions**

- candidate extraction from user message + optional formulation context
- deterministic embedding/tokenization
- similarity scoring
- duplicate suppression

**Step 3: Re-run tests**

Expected: helper tests pass; tool tests still fail

### Task 3: Implement search_memory tool

**Files:**
- Create: `app/backend/app/agent/tools/search_memory.py`
- Modify: `app/backend/app/agent/xinque.py`
- Modify: `app/backend/app/agent/system_prompt.py`

**Step 1: Add failing tool test if needed**

- retrieval returns top matches with content, topic, emotions, and created date

**Step 2: Implement minimal tool**

- accept `query`, optional `top_k`, optional `topic`
- use helper similarity scoring

**Step 3: Register tool**

- add to tool registry and prompt guidance

### Task 4: Add memory capture path

**Files:**
- Modify: `app/backend/app/main.py`

**Step 1: Capture episodic memory after normal chat persistence**

- only from user message
- only when candidate extraction passes threshold

**Step 2: Ensure duplicates are suppressed**

- avoid repeated storage of near-identical event text for same user

### Task 5: Verify Sprint 10 slice

**Files:**
- Modify as needed only if verification reveals regressions

**Step 1: Run backend tests**

```bash
cd app/backend
<python> -m unittest discover -s tests -p 'test_*.py'
```

**Step 2: Run syntax verification**

```bash
cd app/backend
<python> -m py_compile app/memory_helpers.py app/agent/tools/search_memory.py app/main.py app/models/tables.py
```

**Step 3: Summarize remaining Sprint 10 gaps**

- note that production embedding service integration can remain deferred if contract is satisfied by deterministic similarity
