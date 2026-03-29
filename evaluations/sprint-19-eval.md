# Sprint 19 评估报告

**日期**: 2026-03-29
**结果**: ⏳ **PARTIAL**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| 1 | `AGENTS.md` 与 `CLAUDE.md` 明确要求写 Prompt 时参考 GPT-5.4 文档 | ✅ | 已写入规则并落到仓库根文档 |
| 2 | `system_prompt.py` 具备输出契约、工具契约、完成契约、验证契约等分层结构 | ✅ | 已重构为 contract-style 分层 Prompt |
| 3 | 首轮与低上下文阶段的 Tool 路由纪律更清晰 | ✅ | 已对 `match_intervention` 增加 formulation gating，并在 Prompt 中强化首轮纪律 |
| 4 | 检索为空或依赖不足时，不会草率结束或过早推进 | ✅ | `search_memory` 已支持 topic 过滤过窄时的 fallback，关键高影响 Tool 已具备依赖检查 |
| 5 | `referral`、`save_session`、`record_outcome` 等高影响动作具备轻量 verification loop | ✅ | 已增加 `referral` / `save_session` / `load_skill` / `record_outcome` guardrail |
| 6 | 长会话一致性治理有明确设计或最小实现 | ✅ | 已补充 long-session contract，并在运行时加入最小历史压缩策略 |
| 7 | Prompt 已完成“持久人格”与“回合级写作控制”的分层 | ✅ | 已在 `system_prompt.py` 中显式拆分 |
| 8 | 存在自动化测试、可重复验证流程或文档化检查点 | ✅ | 已新增并运行 Prompt / guardrail / long-session / search-memory 测试，且后端 `unittest discover` 63 个测试通过 |

## 本 Sprint 预期产出

### 规则文件修改
- `AGENTS.md`
- `CLAUDE.md`

### 后端修改
- `app/backend/app/agent/system_prompt.py`
- `app/backend/app/agent/xinque.py`
- 如有需要，相关 Tool 模块

### 测试修改
- 与 Prompt contract、Tool guardrails、长会话治理相关的后端测试

### 文档修改
- `specs/sprint-19-GPT-5.4提示工程与运行契约升级.md`
- `contracts/sprint-19-contract.md`

## 本 Sprint 实际产出

### 已观察到的修改
- `AGENTS.md`
- `CLAUDE.md`
- `app/backend/app/agent/system_prompt.py`
- `app/backend/app/agent/xinque.py`
- `app/backend/tests/test_system_prompt_contract.py`
- `app/backend/tests/test_xinque_guardrails.py`
- `app/backend/tests/test_xinque_long_session.py`
- `app/backend/tests/test_search_memory.py`
- `docs/design/product-plan-v2-implementation-status.md`

## 建议验证步骤

### Prompt 与规则检查
- 检查 `AGENTS.md` / `CLAUDE.md` 是否明确写入 GPT-5.4 Prompt 参考规则
- 检查 `system_prompt.py` 是否按契约分层，而不是继续维持单一大段说明

### 运行时检查
- 构造首轮对话，确认 Prompt 明确要求优先 `recall_context`
- 构造 `formulation.readiness=exploring` 场景，确认 `match_intervention` 不会直接执行
- 构造未出现结束意图的普通对话，确认 `save_session` 会被阻止
- 构造缺少 `urgency` 的 `referral` 调用，确认会被阻止

### 自动化验证
- 已运行 `app/backend/tests/test_system_prompt_contract.py`
- 已运行 `app/backend/tests/test_xinque_guardrails.py`
- 已运行 `app/backend/tests/test_xinque_long_session.py`
- 已运行 `app/backend/tests/test_search_memory.py`
- 已运行后端 `unittest discover` 全量测试

## 当前验证证据

- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_system_prompt_contract.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_xinque_guardrails.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_xinque_long_session.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe app\\backend\\tests\\test_search_memory.py`
- `& .\\app\\backend\\.venv\\Scripts\\python.exe -m unittest discover -s app\\backend\\tests -p "test_*.py"`

## 当前结论

`Sprint 19` 的第一阶段目标已经落地：

- Prompt 参考规则已上升为项目级约束
- Prompt 已从单段说明重构为 contract-style 分层结构
- 高影响 Tool 的前置 guardrail 已覆盖 `match_intervention`、`save_session`、`referral`、`load_skill`、`record_outcome`

当前仍未完全收口的部分：

- 长会话治理仍处于“最小实现 + 迁移占位”阶段，尚未迁移到 Responses API / phase-aware 全链路
- 当前历史压缩是最小规则实现，还不是更丰富的语义 compaction

## 注意事项

- 如果本地环境缺少测试依赖，需要在评估中明确记录“环境阻塞”和“已完成的最小验证范围”
- 对心理支持场景，应优先确认安全边界和阶段纪律没有因 Prompt 重构而退化
