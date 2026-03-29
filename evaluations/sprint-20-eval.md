# Sprint 20 评估报告

**日期**: 2026-03-29
**结果**: ⏳ **PARTIAL**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| 1 | 核心对话循环已从 Chat Completions 迁移到 Responses API | ✅ | `xinque.py` 已改用 `client.responses.create(...)` |
| 2 | 运行时能够显式区分中间工作态、工具调用态和最终答复态 | ✅ | 已基于 Responses output 区分 `function_call` 与 assistant `message.phase` |
| 3 | 历史重放或对话延续时，assistant 的 `phase` 语义不会丢失 | ◑ | 跨轮已通过 trace 恢复 `previous_response_id`，assistant 历史默认保留 `final_answer`；更完整的 conversation/store 策略仍未引入 |
| 4 | `/api/chat` 对前端的返回协议保持兼容 | ✅ | `reply` / `session_id` / `card_data` 结构保持不变 |
| 5 | trace 中能够观察到 phase-aware 的协议流 | ✅ | `llm_trace` 已记录 `endpoint`、`final_phase`、`response_ids` |
| 6 | 至少存在自动化测试或可重复验证覆盖本次迁移 | ✅ | 定向测试通过，后端 `unittest discover` 67 个测试通过 |

## 本 Sprint 实际产出

### 后端修改
- `app/backend/app/agent/xinque.py`
- `app/backend/app/main.py`
- `app/backend/app/evaluation_helpers.py`
- `app/backend/app/responses_helpers.py`
- `app/backend/tests/test_response_state.py`

### 测试修改
- `app/backend/tests/test_xinque_trace.py`
- `app/backend/tests/test_judge_evaluation.py`

## 当前验证证据

- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_xinque_trace.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_judge_evaluation.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_response_state.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe -m unittest discover -s app\\backend\\tests -p "test_*.py"`

## 当前结论

`Sprint 20` 的第一阶段已经完成：

- 核心 Agent 主循环已迁移到 Responses API
- 当前回合内与跨轮延续都已使用 `previous_response_id`
- trace 已可记录 phase-aware 相关信息
- 评估助手与会话摘要生成也已改用 Responses API

当前仍未完全收口的部分：

- 跨轮延续还没有使用更完整的 Responses conversation / stored response 策略
- `phase` 目前主要覆盖 `final_answer`，还未引入更丰富的跨轮 assistant 状态持久化
