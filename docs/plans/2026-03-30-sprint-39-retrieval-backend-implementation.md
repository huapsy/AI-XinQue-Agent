# Sprint 39 Retrieval Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 把 `search_memory` 从具体本地检索函数中解耦出来，建立最小 retrieval backend 抽象，并保留 local backend 作为默认和回退路径。

**Architecture:** 本轮只做 backend 抽象，不接真实外部向量服务。新增一个 retrieval backend 模块，提供 local backend 与统一入口；`search_memory` 改为通过该入口检索。原有 embedding、排序和时间新鲜度逻辑继续复用，确保行为不退化。

**Tech Stack:** Python, unittest

---

### Task 1: 建立 retrieval backend 抽象

**Files:**
- Add: `app/backend/app/memory_retrieval.py`
- Modify: `app/backend/app/agent/tools/search_memory.py`
- Test: `app/backend/tests/test_search_memory.py`

**Step 1: Write the failing test**

新增测试，断言 `search_memory` 通过统一 retrieval backend 调用，而不是直接依赖 `score_memories_by_query`。

**Step 2: Run test to verify it fails**

Run: `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_search_memory.py`
Expected: FAIL because the abstraction does not exist yet.

**Step 3: Write minimal implementation**

新增 retrieval backend 模块，包含：
- local backend
- 统一的 `retrieve_memories()` 入口

并让 `search_memory` 走该入口。

**Step 4: Run test to verify it passes**

Run the search-memory test file and confirm PASS.

### Task 2: 保护原有检索质量样本

**Files:**
- Test: `app/backend/tests/test_memory_vectorization.py`
- Test: `app/backend/tests/test_search_memory.py`

**Step 1: Run regression tests**

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_search_memory.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_memory_vectorization.py
```

**Step 2: Confirm behavior stays green**

如有退化，只修正最小实现，不扩大范围。

### Task 3: 回填评估证据

**Files:**
- Modify: `evaluations/sprint-39-eval.md`

**Step 1: Record evidence**

把实际运行命令、修改文件与残余风险补进 `evaluations/sprint-39-eval.md`。

