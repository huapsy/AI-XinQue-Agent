# Sprint 28 评估报告

**日期**: 2026-03-29
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| 1 | `search_memory()` 在相关性接近时优先返回较新的记忆 | ✅ | 已补时间新鲜度 tie-break 排序 |
| 2 | 多 intervention 场景下系统能识别主 follow-up 对象 | ✅ | 已新增 `time_freshness.py` 并覆盖 recent / reactivated / stale 三类情况 |
| 3 | 更早 intervention 未被重新激活时不会抢占近期主线 | ✅ | 已覆盖 stale background 测试 |
| 4 | 短时间内刚做过的同一 skill 不会继续作为首推方案 | ✅ | `match_intervention` 已加入最小冷却降权 |
| 5 | `Sprint 27` 既有 guardrail 未回归 | ✅ | `test_xinque_guardrails.py` 全部通过 |
| 6 | 后端全量回归通过 | ✅ | `unittest discover` 共 96 项通过 |

## 本 Sprint 实际产出

### 后端修改
- `app/backend/app/time_freshness.py`
- `app/backend/app/memory_helpers.py`
- `app/backend/app/agent/tools/search_memory.py`
- `app/backend/app/agent/tools/match_intervention.py`
- `app/backend/app/agent/tools/recall_context.py`
- `app/backend/app/session_context.py`
- `app/backend/app/agent/xinque.py`
- `app/backend/app/agent/system_prompt.py`

### 测试修改
- `app/backend/tests/test_search_memory.py`
- `app/backend/tests/test_time_freshness.py`
- `app/backend/tests/test_match_intervention_ranking.py`
- `app/backend/tests/test_system_prompt_contract.py`

### Harness 文档
- `specs/sprint-28-时间新鲜度排序与多干预优先级治理.md`
- `contracts/sprint-28-contract.md`

## 当前验证证据

- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_search_memory.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_time_freshness.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_match_intervention_ranking.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_xinque_guardrails.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_system_prompt_contract.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe -m unittest discover -s app\\backend\\tests -p "test_*.py"`

## 当前结论

`Sprint 28` 已把“时间新鲜度”从单个 recent intervention guardrail，推进到了更系统的一层：

- `search_memory()` 在相关性接近时，较新的记忆会排在前面
- 多 intervention 场景下，系统会先识别一个主 follow-up 对象，而不是平均对待全部历史
- 旧 intervention 默认降到背景层，只有被用户重新激活时才重新进入主线
- 刚做过的同一 skill 即使允许继续推荐，也不会再机械地排成第一推荐

本轮仍未扩展的内容包括：

- 基于主题连续性的更强 re-ranker
- 前端 / 管理端对“当前主 follow-up 对象”的显式展示
- 更复杂的跨 skill 冷却与替代策略
