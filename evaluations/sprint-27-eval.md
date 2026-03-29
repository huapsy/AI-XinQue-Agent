# Sprint 27 评估报告

**日期**: 2026-03-29
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| 1 | recent intervention 在 48 小时内且未收口时，`match_intervention` 会被阻止 | ✅ | 返回 `reason="recent_intervention_needs_follow_up"` |
| 2 | 同一 skill 在 48 小时内刚做过时，`load_skill` 会被阻止 | ✅ | 仅在用户未明确要求重做时阻止 |
| 3 | 用户明确要求换方法或重做时，上述阻止规则放行 | ✅ | 已覆盖“换方法”和“再做一次”两类信号 |
| 4 | `system_prompt.py` 已包含时间新鲜度驱动的 follow-up 契约 | ✅ | 已补 `match_intervention` / `load_skill` / 长会话契约 |
| 5 | 自动化测试先失败后通过，并通过全量回归 | ✅ | 定向测试红转绿，后端全量 `90` 项通过 |

## 本 Sprint 实际产出

### 后端修改
- `app/backend/app/agent/xinque.py`
- `app/backend/app/agent/system_prompt.py`

### 测试修改
- `app/backend/tests/test_xinque_guardrails.py`
- `app/backend/tests/test_system_prompt_contract.py`

### Harness 文档
- `specs/sprint-27-时间新鲜度驱动推理与Tool路由.md`
- `contracts/sprint-27-contract.md`

## 当前验证证据

- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_xinque_guardrails.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_system_prompt_contract.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe -m unittest discover -s app\\backend\\tests -p "test_*.py"`

## 当前结论

`Sprint 27` 已把“时间新鲜度”从上下文元数据推进成最小运行时规则：

- 最近 48 小时内有未收口 intervention 时，系统优先要求 follow-up
- 不再默认机械重复推荐昨天刚做过的方案
- 只有用户明确要求换方法、说明旧方法无效，或主动要求重做时，才放行推荐/重做路径

本轮仍未扩展的内容包括：

- `search_memory()` 结果的时间新鲜度排序
- 多个历史 intervention 的全局冷却或优先级策略
- 前端 / 管理端对 recent follow-up 建议的显式展示
