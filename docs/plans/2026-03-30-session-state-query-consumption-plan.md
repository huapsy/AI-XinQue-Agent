# Session State Query Consumption Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为会话状态历史与 phase timeline 读取接口补齐分页、过滤和运营消费友好的返回元信息。

**Architecture:** 继续沿用当前 `SessionStateHistory + TraceRecord` 的最小模型，不扩数据库结构，优先在读取层增加稳定查询参数和序列化元信息。后端 API 负责把“全量技术数据”收敛成“可分页、可筛选、可继续拉取”的消费接口，避免前端和运营侧自己做二次裁剪。

**Tech Stack:** FastAPI, SQLAlchemy, Python unittest

---

### Task 1: 定义 state-history 查询契约

**Files:**
- Modify: `app/backend/app/session_state_store.py`
- Modify: `app/backend/app/main.py`
- Test: `app/backend/tests/test_session_state_api.py`

**Step 1: Write the failing test**

```python
payload = asyncio.run(
    get_session_state_history(
        "session-1",
        db,
        limit=1,
        before_version=3,
        change_reason="semantic_summary_changed",
    )
)
assert payload["history"][0]["version"] == 2
assert payload["meta"]["has_more"] is False
```

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`
Expected: FAIL because the API/store layer does not yet accept filtering arguments or return pagination metadata.

**Step 3: Write minimal implementation**

实现 `load_session_state_history()` 的可选参数：
- `limit`
- `before_version`
- `change_reason`

并让 `/api/sessions/{session_id}/state-history` 返回：
- `history`
- `meta.returned`
- `meta.limit`
- `meta.has_more`
- `meta.next_before_version`

**Step 4: Run test to verify it passes**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`
Expected: PASS

### Task 2: 定义 timeline 查询契约

**Files:**
- Modify: `app/backend/app/main.py`
- Modify: `app/backend/app/trace_helpers.py`
- Test: `app/backend/tests/test_session_state_api.py`
- Test: `app/backend/tests/test_trace_api.py`

**Step 1: Write the failing test**

```python
payload = asyncio.run(
    get_session_timeline(
        "session-1",
        db,
        limit=1,
        before_turn=3,
        phase="tool_call",
    )
)
assert payload["timeline"][0]["turn_number"] == 2
assert payload["meta"]["has_more"] is False
```

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`
Expected: FAIL because timeline currently only returns full raw history with no filter or pagination metadata.

**Step 3: Write minimal implementation**

让 `/api/sessions/{session_id}/timeline` 支持：
- `limit`
- `before_turn`
- `phase`

并返回：
- `timeline`
- `meta.returned`
- `meta.limit`
- `meta.has_more`
- `meta.next_before_turn`
- `meta.phase`

**Step 4: Run tests to verify they pass**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`
Expected: PASS

### Task 3: 回归与状态文档同步

**Files:**
- Modify: `docs/design/product-plan-v2-implementation-status.md`

**Step 1: Run targeted regression**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`

**Step 2: Run serializer regression**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py`

**Step 3: Update status doc**

把“状态查询的分页/过滤与运营消费层”从未完成描述更新为已实现当前最小版本。

