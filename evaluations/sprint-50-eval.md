# Sprint 50 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | assistant 最终回合已支持结构化输出 `reply + phase_fields` |
| A2 | PASS | `Flow Controller` 已优先消费 assistant 显式字段；缺失时回退到 runtime fallback |
| A3 | PASS | `asking`、`chosen_intervention`、`intervention_complete` 已进入 `flow_state` / persisted state / trace |
| A4 | PASS | 已有多轮脚本级验证覆盖 `P1 -> P2 -> P3 -> P4 -> P1` |
| A5 | PASS | `spec`、`contract`、`evaluation` 与定向测试证据齐备 |

## 实际改动

- assistant 显式阶段字段输出：
  - 在 [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 中新增 `assistant_phase_turn` 的 structured output schema
  - 最终 assistant 回合优先解析 `output_parsed.reply` 与 `output_parsed.phase_fields`
- `Flow Controller` 消费显式字段：
  - `xinque.chat()` 在最终回合基于 assistant 输出的 `phase_fields` 再次运行 `Flow Controller`
  - 当 assistant 未返回结构化字段时，回退到 runtime 推导
- evaluator 脚本级验证：
  - 在 [test_xinque_phase_fields.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_phase_fields.py) 中新增多轮脚本样本
  - 验证 `P1 -> P2 -> P3 -> P4 -> P1` 的连续阶段流转

## 验证证据

- 定向验证一：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_xinque_phase_fields.py tests/test_responses_contract.py
```

- 结果：`Ran 13 tests ... OK`

- 定向验证二：

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_flow_controller.py tests/test_phase_state.py tests/test_phase_router.py tests/test_xinque_phase_fields.py tests/test_xinque_trace.py tests/test_responses_contract.py tests/test_system_prompt_contract.py tests/test_session_context.py tests/test_tool_runtime.py tests/test_xinque_guardrails.py
```

- 结果：`Ran 88 tests ... OK`

## 关键测试覆盖

- [test_xinque_phase_fields.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_phase_fields.py)
  - 验证 assistant 结构化 phase fields 被 `Flow Controller` 消费
  - 验证多轮脚本流转 `P1 -> P2 -> P3 -> P4 -> P1`
- [test_xinque_trace.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)
  - 验证 persisted state 与 trace 不因 structured output 接入而回退
- [test_responses_contract.py](/E:/AI_XinQue_Agent/app/backend/tests/test_responses_contract.py)
  - 验证 working contract 可见阶段字段语义

## 问题清单

- 当前 structured output 主要覆盖最终 assistant 回合；tool call 中间轮次仍以现有 Responses tool loop 为主
- evaluator 多轮验证目前仍是测试脚本，不是独立外部驱动的真实运行时评估器
- assistant 结构化字段虽已显式输出，但仍需继续观察真实对话里字段稳定性与缺失率

## 结论

- Sprint 50 通过。
- `06-Flow模块与阶段子Agent架构-v1.md` 中“阶段输出契约”和“评估闭环”已进一步落地：assistant 不再只输出自然语言，已经能够显式回填最小阶段字段，并通过多轮脚本验证核心阶段流转。
