# Sprint 45 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | 已定义 `p1_listener` / `p2_explorer` / `p3_recommender` / `p4_interventor` 四个 phase profile |
| A2 | PASS | system prompt 已拆为“基座 + 单一 active phase block”，不会同时注入多个 phase profile |
| B1 | PASS | `active_phase` 已进入 persisted session state |
| B2 | PASS | layered context、working contract、trace 均已具备 `active_phase` 可见性 |
| C1 | PASS | 主 agent 单路径仍保持为单一 `xinque.chat()` 主循环，未拆成多 LLM 轮流接管 |

## 实际改动

- 新增 phase profile 定义模块 [phase_profiles.py](/E:/AI_XinQue_Agent/app/backend/app/agent/phase_profiles.py)，为四阶段提供最小配置合同：
  - `display_name`
  - `goal`
  - `allowed_tools`
  - `prompt_block`
- 在 [system_prompt.py](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) 中支持按 `active_phase` 只注入单一 phase block
- 在 [session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py) 中让 `active_phase` 进入 persisted session state 与 layered context
- 在 [responses_contract.py](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py) 中让 working contract 明示当前 `active_phase`
- 在 [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 中保留单主链路，同时把当前 phase 注入到 prompt 和 trace

## 验证证据

- 定向测试：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_phase_profiles.py tests/test_system_prompt_contract.py tests/test_session_context.py tests/test_responses_contract.py tests/test_xinque_trace.py
```

- 结果：已在 Sprint 45-47 联合回归中通过，整体回归结果为 `Ran 76 tests ... OK`

- 关键覆盖：
  - [test_phase_profiles.py](/E:/AI_XinQue_Agent/app/backend/tests/test_phase_profiles.py)：验证 4 个 phase profile 与最小合同字段存在
  - [test_system_prompt_contract.py](/E:/AI_XinQue_Agent/app/backend/tests/test_system_prompt_contract.py)：验证 system prompt 只注入当前 phase block
  - [test_session_context.py](/E:/AI_XinQue_Agent/app/backend/tests/test_session_context.py)：验证 `active_phase` 持久化与 context 可见
  - [test_responses_contract.py](/E:/AI_XinQue_Agent/app/backend/tests/test_responses_contract.py)：验证 working contract 可见 `active_phase`
  - [test_xinque_trace.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)：验证 trace 中记录 phase profile 选择

## 问题清单

- 本轮只完成了 profile 化和 phase 可见性，不包含自动 phase 切换逻辑
- `active_phase` 在本轮还是静态注入能力，真正由 flow state 驱动的路由放到 Sprint 46 完成

## 结论

- Sprint 45 通过。
- 心雀已从“单大 prompt 内部同时描述四阶段”收口为“主 Agent + 四阶段子 Agent profile”的最小可运行结构，但仍保持单一主 agent 架构。
