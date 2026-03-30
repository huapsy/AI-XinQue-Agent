# Sprint 49 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | 后端已新增 `Flow Controller` 控制平面，并由 `xinque.chat()` 调用，不再只依赖零散 phase 条件拼接 |
| A2 | PASS | `flow_state` 已稳定包含 `active_phase`、`phase_transition_reason`、`intent`、`explore`、`asking`、`formulation_confirmed`、`needs_more_exploration`、`chosen_intervention`、`intervention_complete`、`active_skill` |
| A3 | PASS | `P1 -> P3` 与 `P1 -> P4` 被区分：`intent=true` 且无进行中 `active_skill` 时进入 `P3`，存在 `active_skill` 时优先 `P4` |
| A4 | PASS | trace 中可见 `phase_fields_raw`、`phase_fields_normalized`、`phase_routing` 与 `phase_transition_reason` |
| A5 | PASS | `working_contract`、system prompt、persisted session state 与 trace 已对齐 Flow Controller 语义 |

## 实际改动

- 新增 Flow Controller 控制平面：
  - 在 [flow_controller.py](/E:/AI_XinQue_Agent/app/backend/app/agent/flow_controller.py) 中实现最小字段默认值、normalization 与 phase routing
- 兼容旧入口并收口 runtime：
  - 在 [phase_state.py](/E:/AI_XinQue_Agent/app/backend/app/agent/phase_state.py) 中让默认 phase state 复用 controller 的最小字段集
  - 在 [phase_router.py](/E:/AI_XinQue_Agent/app/backend/app/agent/phase_router.py) 中让旧 router 成为 controller 的兼容包装层
  - 在 [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 中接入 controller，并把 raw / normalized fields 与 routing 结果写入 `phase_timeline`
- 收口跨轮可见语义：
  - 在 [session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py) 中持久化并渲染完整最小 `flow_state`
  - 在 [responses_contract.py](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py) 中加入 Flow Controller 字段语义
  - 在 [system_prompt.py](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) 中明确阶段字段纪律
- harness 文档补齐：
  - 新增 [sprint-49-Flow-Controller与阶段输出契约闭环.md](/E:/AI_XinQue_Agent/specs/sprint-49-Flow-Controller与阶段输出契约闭环.md)
  - 新增 [sprint-49-contract.md](/E:/AI_XinQue_Agent/contracts/sprint-49-contract.md)

## 验证证据

- 定向回归一：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_phase_state.py tests/test_phase_router.py tests/test_flow_controller.py tests/test_xinque_trace.py
```

- 结果：`Ran 25 tests ... OK`

- 定向回归二：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_phase_state.py tests/test_phase_router.py tests/test_flow_controller.py tests/test_xinque_trace.py tests/test_session_context.py tests/test_responses_contract.py tests/test_system_prompt_contract.py
```

- 结果：`Ran 60 tests ... OK`

- 定向回归三：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_tool_runtime.py tests/test_xinque_guardrails.py
```

- 结果：`Ran 26 tests ... OK`

## 关键测试覆盖

- [test_flow_controller.py](/E:/AI_XinQue_Agent/app/backend/tests/test_flow_controller.py)
  - 验证字段 normalization
  - 验证 `P1 -> P3`、`P3 -> P4`、`P4 -> P1`
- [test_phase_router.py](/E:/AI_XinQue_Agent/app/backend/tests/test_phase_router.py)
  - 验证旧 router 已对齐新 controller 语义
- [test_xinque_trace.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)
  - 验证 `phase_fields_normalized`
  - 验证 direct intent 不再无条件进入 `P4`
- [test_session_context.py](/E:/AI_XinQue_Agent/app/backend/tests/test_session_context.py)
  - 验证跨轮持久化和上下文渲染没有丢失 phase 状态

## 问题清单

- 当前 assistant 还没有强制输出严格结构化 phase fields；本轮主要是 runtime controller 收口，不是 structured output 强绑定
- `asking`、`chosen_intervention`、`intervention_complete` 目前仍主要依赖 runtime 与 tool 事实推导，尚未形成更丰富的模型显式回填
- 目前 evaluation 仍以单元测试和 trace 结构验证为主，尚未加入新的多轮对话脚本级 evaluator 样本

## 结论

- Sprint 49 通过。
- 心雀的四阶段推进已从“最小 phase router”提升到“最小 Flow Controller 闭环”，可以作为下一轮继续加强 assistant 阶段输出契约和 evaluator 对话脚本验证的稳定基线。
