# Sprint 46 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | 已定义最小 flow state variables，包含 `active_phase`、`intent`、`explore`、`asking`、`formulation_confirmed`、`needs_more_exploration`、`chosen_intervention`、`intervention_complete`、`active_skill` |
| A2 | PASS | 已新增独立 phase router，可输出下一 `active_phase` 与 `transition_reason` |
| B1 | PASS | `intent=True` 时可直达 `p4_interventor` |
| B2 | PASS | `explore=True` 时可从 `p1_listener` 推进到 `p2_explorer` |
| B3 | PASS | `active_skill` 存在时默认保持 `p4_interventor` |
| C1 | PASS | 已接入现有主链路，不绕过 Responses + tool loop 和既有 guardrail |

## 实际改动

- 新增最小 flow state 定义 [phase_state.py](/E:/AI_XinQue_Agent/app/backend/app/agent/phase_state.py)
- 新增 phase 路由器 [phase_router.py](/E:/AI_XinQue_Agent/app/backend/app/agent/phase_router.py)
- 在 [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 中：
  - 基于用户输入、formulation 和 `active_skill` 构造最小 phase state
  - 调用 router 决定下一 `active_phase`
  - 将 `phase_transition_reason` 写回 stable state 与 trace
- 在 [session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py) 中持久化 `phase_transition_reason`

## 验证证据

- 定向测试：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_phase_state.py tests/test_phase_router.py tests/test_xinque_trace.py tests/test_session_context.py
```

- 结果：已在 Sprint 45-47 联合回归中通过，整体回归结果为 `Ran 76 tests ... OK`

- 关键覆盖：
  - [test_phase_state.py](/E:/AI_XinQue_Agent/app/backend/tests/test_phase_state.py)：验证默认 phase state 结构
  - [test_phase_router.py](/E:/AI_XinQue_Agent/app/backend/tests/test_phase_router.py)：验证 `intent`、`explore`、`active_skill` 等核心路由分支
  - [test_xinque_trace.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)：验证 `phase_routing` 与 `phase_profile_selected` 已进入 trace
  - [test_session_context.py](/E:/AI_XinQue_Agent/app/backend/tests/test_session_context.py)：验证 `phase_transition_reason` 的持久化与渲染

## 问题清单

- 当前 router 仍是最小版，只覆盖最关键的分流条件
- `asking`、`needs_more_exploration`、`chosen_intervention` 目前主要是为后续扩展保留，尚未形成更细粒度的阶段模板控制

## 结论

- Sprint 46 通过。
- 心雀已具备最小 flow state 驱动的 phase 路由能力，阶段推进不再只靠 prompt 文字说明。
