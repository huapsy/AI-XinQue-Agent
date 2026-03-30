# Sprint 36 Prompt Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 把心雀 Prompt 体系从首轮 contract 升级为更强的运行时 Prompt 架构，并让 evaluator 能直接消费关键 Prompt 审查信号。

**Architecture:** 本轮只做最小闭环，不重写整个对话系统。第一条线补强 `system_prompt.py` 与 `responses_contract.py` 中仍偏弱的契约，包括 `phase` 纪律、工具空结果恢复、完成与验证闸门。第二条线扩展 `evaluation_helpers.py` 的 judge schema，让 Prompt 审查项以结构化字段输出，而不只停留在人工阅读。第三条线用定向测试锁住 contract 与 evaluator 行为。

**Tech Stack:** Python, FastAPI helper modules, Azure OpenAI Responses API, unittest

---

### Task 1: 补强运行时 Prompt 契约

**Files:**
- Modify: `app/backend/app/agent/system_prompt.py`
- Modify: `app/backend/app/responses_contract.py`
- Test: `app/backend/tests/test_system_prompt_contract.py`
- Test: `app/backend/tests/test_responses_contract.py`

**Step 1: Write the failing test**

在 `test_system_prompt_contract.py` 增加测试，断言系统 Prompt 明确包含：

- `phase` 的中间 commentary / tool 过渡 / final answer 纪律
- 空结果或低置信度结果时先恢复，而不是直接下结论
- 输出前验证闸门

在 `test_responses_contract.py` 增加测试，断言跨轮 working contract 也带有：

- `phase` 语义
- 完成 / 验证闸门

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py`

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_responses_contract.py`

Expected: FAIL because current contract text does not yet cover all required rules.

**Step 3: Write minimal implementation**

更新 `system_prompt.py` 和 `responses_contract.py`，仅补最小必需规则：

- `phase` 纪律
- 空结果恢复
- 完成闸门
- 验证闸门

**Step 4: Run tests to verify they pass**

Run the two test files above and confirm PASS.

### Task 2: 让 evaluator 直接消费 Prompt 审查信号

**Files:**
- Modify: `app/backend/app/evaluation_helpers.py`
- Test: `app/backend/tests/test_judge_evaluation.py`

**Step 1: Write the failing test**

在 `test_judge_evaluation.py` 增加测试，断言 judge 结构化输出新增 `prompt_review`，至少包含：

- `premature_advice`
- `format_heaviness`
- `assumption_as_fact`
- `tool_discipline`

并且 `run_llm_judge()` 会把这些字段标准化后放进结果 payload。

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_judge_evaluation.py`

Expected: FAIL because the current judge schema has no prompt-review fields.

**Step 3: Write minimal implementation**

扩展 judge schema、解析与返回结构：

- 让 Responses judge 输出 `prompt_review`
- 为各字段做最小规范化
- 保持旧分数字段兼容

**Step 4: Run test to verify it passes**

Run the judge test file and confirm PASS.

### Task 3: 定向回归并同步 Sprint 36 评估证据

**Files:**
- Modify: `evaluations/sprint-36-eval.md`

**Step 1: Run targeted verification**

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_responses_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_judge_evaluation.py
```

**Step 2: Record evidence**

把通过的命令、关键变更文件和残余风险补进 `evaluations/sprint-36-eval.md`。

**Step 3: Optional broader verification**

If time permits, run:

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_trace.py
```

If not run, explicitly note the gap in the evaluation report.

