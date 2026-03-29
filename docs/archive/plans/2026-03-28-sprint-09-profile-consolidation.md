# Sprint 09 Profile Consolidation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Consolidate profile writes so user profile data remains stable across alignment, safety, formulation, and recall flows.

**Architecture:** Introduce a small backend profile helper module that owns merge/update behavior for `UserProfile` JSON fields. Keep clinical and alliance aggregation code-driven, add a limited `update_profile` tool only for explicit user preference capture, and reshape `recall_context` output without broad frontend changes.

**Tech Stack:** Python, FastAPI, SQLAlchemy async ORM, Alembic, unittest

---

### Task 1: Add failing tests for profile merge behavior

**Files:**
- Create: `app/backend/tests/test_profile_helpers.py`
- Create: `app/backend/tests/test_recall_context.py`

**Step 1: Write the failing tests**

- Verify alliance updates do not overwrite existing `preferences`
- Verify clinical profile aggregation merges new formulate output incrementally
- Verify `recall_context()` returns `profile_snapshot`, `last_session_summary`, `pending_homework`, `recent_interventions`

**Step 2: Run tests to verify they fail**

Run:

```bash
cd app/backend
<python> -m unittest tests.test_profile_helpers tests.test_recall_context
```

Expected: FAIL because helper module and new recall shape do not exist yet

### Task 2: Implement profile helper module

**Files:**
- Create: `app/backend/app/profile_helpers.py`
- Modify: `app/backend/app/models/tables.py`

**Step 1: Add minimal helper API**

- `merge_profile_json()`
- `build_clinical_profile_patch_from_formulation()`
- `apply_profile_patch()`

**Step 2: Add schema support**

- Add `clinical_profile` JSON field to `UserProfile`
- Create Alembic migration for the new column

**Step 3: Re-run helper tests**

Expected: helper tests move closer to green; recall tests still fail

### Task 3: Integrate formulate and recall_context with profile consolidation

**Files:**
- Modify: `app/backend/app/agent/tools/formulate.py`
- Modify: `app/backend/app/agent/tools/recall_context.py`

**Step 1: Update formulate flow**

- After formulation merge, derive clinical profile patch and apply it to `UserProfile`

**Step 2: Reshape recall_context output**

- Return stable structure using `profile_snapshot`, `last_session_summary`, `pending_homework`, `recent_interventions`

**Step 3: Re-run tests**

Expected: helper and recall tests pass

### Task 4: Add limited update_profile tool for explicit user preferences

**Files:**
- Create: `app/backend/app/agent/tools/update_profile.py`
- Modify: `app/backend/app/agent/tools/__init__.py`
- Modify: `app/backend/app/agent/xinque.py`
- Modify: `app/backend/app/agent/system_prompt.py`
- Create: `app/backend/tests/test_update_profile.py`

**Step 1: Write the failing test**

- Verify explicit preference updates persist to `preferences`
- Verify unsupported fields are rejected

**Step 2: Run test to verify it fails**

**Step 3: Implement minimal tool**

- Only allow a limited `preferences` patch surface

**Step 4: Run tests**

Expected: new tests pass without breaking earlier ones

### Task 5: Verify Sprint 09 target slice

**Files:**
- Modify as needed based on verification only

**Step 1: Run targeted backend test suite**

Run:

```bash
cd app/backend
<python> -m unittest tests.test_profile_helpers tests.test_recall_context tests.test_update_profile tests.test_referral
```

**Step 2: Run Python syntax verification**

Run:

```bash
cd app/backend
<python> -m py_compile app/main.py app/agent/xinque.py app/agent/tools/recall_context.py app/agent/tools/formulate.py app/agent/tools/update_profile.py app/profile_helpers.py
```

**Step 3: Summarize remaining Sprint 09 gaps**

- Call out any contract items intentionally deferred inside Sprint 09 scope
