# Sprint 44 Evaluation

状态：PASS

## 验收结果

| 项 | 结果 | 说明 |
|---|---|---|
| A1 | PASS | `load_skill()` 成功后，`active_skill` 会被写入持久化 session state，并至少保留 `skill_name`；`build_persisted_session_state()` 已覆盖该字段透传 |
| A2 | PASS | layered context 与 working contract 都会显式带出当前 `active_skill`，提示未完成前优先继续当前 skill |
| B1 | PASS | 当 `active_skill` 存在且用户未明确要求换方法时，`match_intervention()` 会返回结构化 blocked payload，`reason=active_skill_in_progress` |
| B2 | PASS | 当 `active_skill` 存在且请求切换到其他 skill 时，新的 `load_skill()` 会返回结构化 blocked payload，`reason=active_skill_in_progress` |
| C1 | PASS | 当用户明确表达“这个方法不适合我”“换一个吧”等切换信号时，guardrail 放行，允许退出当前 skill 并回到重新探索 / 推荐 |
| C2 | PASS | `record_outcome()` 成功记录当前 skill 结果后，`resolve_active_skill_state()` 会清空 `active_skill` |

## 实际改动

- 在 `tool_runtime.py` 中引入 `resolve_active_skill_state()`，基于上一轮状态、本轮 tool 结果和当前用户消息推导新的 `active_skill`
- 在 `tool_runtime.py` 的 `preflight_tool_call()` 中加入 active skill 守门逻辑：
  - skill 执行中阻止 `match_intervention()`
  - skill 执行中阻止切换到新的 `load_skill()`
  - 对外统一返回结构化 blocked payload
- 在 `session_context.py` 中把 `active_skill` 纳入持久化 session state，并在 layered context 渲染中显式输出 `active_skill=...`
- 在 `responses_contract.py` 中把 active skill 锁定规则加入 working contract，要求未完成前优先继续当前 skill
- 补充定向测试，覆盖：
  - `active_skill` 持久化与上下文可见性
  - active skill 存在时的 tool guardrail
  - 用户明确要求切换方法时的放行
  - `record_outcome()` 后清空 active skill

## 验证证据

- 代码核对：
  - `app/backend/app/tool_runtime.py`
  - `app/backend/app/session_context.py`
  - `app/backend/app/responses_contract.py`
- 定向测试：
  - `app/backend/tests/test_session_context.py`
  - `app/backend/tests/test_responses_contract.py`
  - `app/backend/tests/test_xinque_guardrails.py`
- 实际执行命令：
```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_session_context.py tests/test_responses_contract.py tests/test_xinque_guardrails.py
```
- 实际结果：
```text
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.121s

OK
```

## 问题清单

- 本轮 contract 要求的最小 `active_skill` 锁定能力已满足，未发现阻断验收的问题
- 仍存在设计边界但不属于本轮未通过项：
  - 尚未实现 step-level workflow engine，仅保持 skill 级锁定
  - 是否“继续当前 skill”的自然语言质量仍部分依赖模型表现，但运行时已提供明确状态与 guardrail

## 结论

- Sprint 44 通过验收
- 本轮已把“skill 一旦开始执行，就应跨轮持续推进直到完成、用户明确拒绝/换方法、或被危机打断”从 prompt 约束提升为运行时可见、可持久化、可验证的契约
- `active_skill` 已进入 session state、working contract、layered context 与 tool guardrail 链路，满足本轮目标与 contract 要求
