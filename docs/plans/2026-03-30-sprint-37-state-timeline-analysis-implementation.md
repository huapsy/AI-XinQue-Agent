# Sprint 37 State Timeline Analysis Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为会话状态历史与 phase timeline 增加一个可直接消费的聚合分析载荷，让运营和评估侧不必自己遍历原始 trace。

**Architecture:** 本轮不改数据库结构，只在读取层新增聚合分析 helper 和 endpoint。输入仍来自现有 `SessionStateHistory + TraceRecord`，输出收敛成会话主线摘要、最近关键变化、phase 演进概览和最小 dashboard 字段。测试先覆盖 helper，再覆盖 API。

**Tech Stack:** Python, FastAPI, unittest

---

### Task 1: 定义聚合分析 helper 契约

**Files:**
- Modify: `app/backend/app/trace_helpers.py`
- Test: `app/backend/tests/test_trace_api.py`

**Step 1: Write the failing test**

新增测试，断言聚合 helper 能返回：
- `current_focus_summary`
- `latest_phases`
- `key_state_changes`
- `phase_counts`

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py`
Expected: FAIL because the helper does not exist yet.

**Step 3: Write minimal implementation**

在 `trace_helpers.py` 增加最小聚合函数，只聚合当前会话的：
- 最新 focus
- 最近 phase
- 关键 change reasons
- 每种 phase 出现次数

**Step 4: Run test to verify it passes**

Run the trace test file again and confirm PASS.

### Task 2: 暴露会话级分析 endpoint

**Files:**
- Modify: `app/backend/app/main.py`
- Test: `app/backend/tests/test_session_state_api.py`

**Step 1: Write the failing test**

新增 API 测试，断言 `/api/sessions/{session_id}/analysis` 对应函数返回：
- `session_id`
- `analysis.current_focus_summary`
- `analysis.phase_counts`
- `analysis.key_state_changes`

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py`
Expected: FAIL because the API does not exist yet.

**Step 3: Write minimal implementation**

在 `main.py` 新增分析 endpoint，复用现有 state / trace 读取，不重复发明存储逻辑。

**Step 4: Run test to verify it passes**

Run the session state API test file and confirm PASS.

### Task 3: 回填评估证据

**Files:**
- Modify: `evaluations/sprint-37-eval.md`

**Step 1: Run targeted verification**

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py
```

**Step 2: Record evidence**

更新 `evaluations/sprint-37-eval.md`，记录实际通过情况与残余风险。

