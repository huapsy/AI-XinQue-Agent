# Sprint 47 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | phase -> `allowed_tools` 已接入 runtime preflight |
| A2 | PASS | 非法 tool 调用会返回结构化 blocked payload，包含 `status=blocked`、`reason=phase_tool_not_allowed`、`active_phase` 等字段 |
| B1 | PASS | `p1_listener` 下 `match_intervention()` 会被阻止，`load_skill()` 也不在允许集合内 |
| B2 | PASS | `p2_explorer` 下 `formulate()` 仍可正常调用 |
| B3 | PASS | `p4_interventor` 下保留 `load_skill()` / `record_outcome()` 主路径，并优先继续当前 skill |
| C1 | PASS | `active_skill` 与 `active_phase` 已形成最小收口，存在执行中 skill 时会优先转到 `p4_interventor` |

## 实际改动

- 在 [tool_runtime.py](/E:/AI_XinQue_Agent/app/backend/app/tool_runtime.py) 中把 `active_phase` 接入 preflight，按 phase profile 的 `allowed_tools` 执行守门
- 非法工具调用统一返回结构化 blocked payload，而不是仅靠模型自觉
- 在 [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 中：
  - tool preflight 会带上 `active_phase`
  - 当前轮已成功 `match_intervention` / `load_skill` 的情况下，补齐 `p4_interventor` 的有效 phase 解析
  - phase 阻止事件会写入 trace 的 `tool_blocked_by_phase`

## 验证证据

- 定向测试：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_xinque_guardrails.py tests/test_xinque_trace.py tests/test_phase_profiles.py
```

- 结果：已在 Sprint 45-47 联合回归中通过，整体回归结果为 `Ran 76 tests ... OK`

- 关键覆盖：
  - [test_xinque_guardrails.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_guardrails.py)：验证 `p1_listener` 阻止 `match_intervention()`、`p2_explorer` 放行 `formulate()`、`p4_interventor` 下允许 `record_outcome()`
  - [test_phase_profiles.py](/E:/AI_XinQue_Agent/app/backend/tests/test_phase_profiles.py)：验证 `p4_interventor` 的 `allowed_tools` 包含 `load_skill` / `record_outcome`，且不包含 `match_intervention`
  - [test_xinque_trace.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)：验证被 phase 阻止的 tool 会进入 trace

## 问题清单

- 当前 phase-aware tool guardrail 是最小版，还不是完整 phase policy engine
- `p3_recommender` 的“用户接受后才能进入 `load_skill()`”仍主要依赖既有 acceptance guardrail 与同回合 tool state，而不是独立的 phase policy 状态机

## 结论

- Sprint 47 通过。
- phase 选择已经开始真实影响 tool runtime，心雀具备了最小的 phase-aware guardrail 闭环。
