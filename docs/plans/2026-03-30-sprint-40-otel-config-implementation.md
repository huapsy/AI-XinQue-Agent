# Sprint 40 OTel Config Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为当前 OTel 导出增加显式启停和 collector endpoint 配置，同时保留本地 JSONL 回退路径。

**Architecture:** 本轮不接真实 collector SDK，只先把配置边界补齐。`settings.py` 提供 OTel 开关和 endpoint 读取；`otel_helpers.py` 根据配置决定是否导出，并把 endpoint 等最小资源信息写入记录，默认仍支持本地 JSONL。测试覆盖启用 / 禁用与 endpoint 配置。

**Tech Stack:** Python, unittest

---

### Task 1: 新增 OTel 配置读取

**Files:**
- Modify: `app/backend/app/settings.py`
- Test: `app/backend/tests/test_settings.py`

**Step 1: Write the failing test**

新增测试，断言：
- `XINQUE_OTEL_ENABLED`
- `OTEL_EXPORTER_OTLP_ENDPOINT`

可被正确读取。

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_settings.py`

**Step 3: Write minimal implementation**

在 `settings.py` 增加最小 getter。

**Step 4: Run test to verify it passes**

Run the settings test file again and confirm PASS.

### Task 2: 让 OTel helper 受配置控制

**Files:**
- Modify: `app/backend/app/otel_helpers.py`
- Test: `app/backend/tests/test_otel_helpers.py`

**Step 1: Write the failing test**

新增测试，断言：
- 禁用时不写文件
- 启用时写文件
- endpoint 配置会进入记录

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_otel_helpers.py`

**Step 3: Write minimal implementation**

只补最小逻辑，不引入真实外部依赖。

**Step 4: Run test to verify it passes**

Run the helper test file again and confirm PASS.

### Task 3: 回填评估证据

**Files:**
- Modify: `evaluations/sprint-40-eval.md`

**Step 1: Run targeted verification**

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_settings.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_otel_helpers.py
```

**Step 2: Record evidence**

更新 `evaluations/sprint-40-eval.md`。

