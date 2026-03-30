# Sprint 38 Continuity Cooling Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 强化 `match_intervention` 的近期 follow-up 优先和跨 skill 冷却治理，并输出最小解释字段。

**Architecture:** 本轮不改 Agent 主循环，先在 `match_intervention` 的匹配层收口规则。通过 recent interventions 的状态、类别和用户反馈做降权，并把冷却理由写进返回结果，形成最小解释性。测试只覆盖排序和输出字段，不扩前端。

**Tech Stack:** Python, unittest

---

### Task 1: 给冷却治理补解释字段

**Files:**
- Modify: `app/backend/app/agent/tools/match_intervention.py`
- Test: `app/backend/tests/test_match_intervention_ranking.py`

**Step 1: Write the failing test**

新增测试，断言匹配结果中带有：
- `continuity_reason`
- `cooling_applied`
- `cooling_reasons`

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_match_intervention_ranking.py`
Expected: FAIL because current output has no explanation fields.

**Step 3: Write minimal implementation**

在匹配与 plan 构建阶段加入最小解释字段，不重构整体架构。

**Step 4: Run test to verify it passes**

Run the ranking test file again and confirm PASS.

### Task 2: 对近期无帮助 / 不喜欢的 skill 做明确降权

**Files:**
- Modify: `app/backend/app/agent/tools/match_intervention.py`
- Test: `app/backend/tests/test_match_intervention_ranking.py`

**Step 1: Write the failing test**

新增测试，断言：
- 用户最近明确给出 `unhelpful` 反馈的同 skill 被明显降权
- 同类别 skill 也受到较轻降权

**Step 2: Run test to verify it fails**

Run the same ranking test file and confirm FAIL.

**Step 3: Write minimal implementation**

在 freshness / cooling 逻辑中把负反馈纳入降权。

**Step 4: Run test to verify it passes**

Run the ranking test file again and confirm PASS.

### Task 3: 回填评估证据

**Files:**
- Modify: `evaluations/sprint-38-eval.md`

**Step 1: Run targeted verification**

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_match_intervention_ranking.py
```

**Step 2: Record evidence**

更新 `evaluations/sprint-38-eval.md`，记录通过项与残余风险。

