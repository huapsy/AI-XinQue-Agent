# 变更记录

## 2026-03-28 至 2026-03-29

### 总览

本条目汇总最近两天已完成、但尚未推送到 GitHub 的主要本地改动。

### 1. Prompt 与对话风格

- 新增并持续完善 [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md)，作为心雀项目级 Prompt 写作规范。
- 更新 [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)，使其更贴合指南要求：
  - 默认自然 prose
  - 抑制条列化倾向
  - 短句、低认知负担
  - 探索驱动的负向 flow
  - 心理理解使用“工作性假设”表达
- 补充并加强以下测试：
  - [`test_system_prompt_contract.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_system_prompt_contract.py)
  - [`test_responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_responses_contract.py)

### 2. Responses / tools / skills 架构重构

- 本地已完成 `Sprint 31-34` 主线工作：
  - Judge / Summary / Formulation 的 structured outputs 收口
  - skill manifest v2 与 registry
  - tool runtime 平台化
  - Responses-first 运行时契约
- 新增核心后端模块：
  - [`responses_helpers.py`](/E:/AI_XinQue_Agent/app/backend/app/responses_helpers.py)
  - [`responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py)
  - [`skill_manifest.py`](/E:/AI_XinQue_Agent/app/backend/app/skill_manifest.py)
  - [`skill_registry.py`](/E:/AI_XinQue_Agent/app/backend/app/skill_registry.py)
  - [`tool_registry.py`](/E:/AI_XinQue_Agent/app/backend/app/tool_registry.py)
  - [`tool_runtime.py`](/E:/AI_XinQue_Agent/app/backend/app/tool_runtime.py)
  - [`tool_contracts.py`](/E:/AI_XinQue_Agent/app/backend/app/tool_contracts.py)
- 新增相关架构文档与说明：
  - [`responses-tools-skills-architecture.md`](/E:/AI_XinQue_Agent/docs/design/responses-tools-skills-architecture.md)
  - [`app/backend/README.md`](/E:/AI_XinQue_Agent/app/backend/README.md)

### 3. 长会话状态、时间感知与连续性

- 新增并接入：
  - [`session_context.py`](/E:/AI_XinQue_Agent/app/backend/app/session_context.py)
  - [`session_state_store.py`](/E:/AI_XinQue_Agent/app/backend/app/session_state_store.py)
  - [`time_context.py`](/E:/AI_XinQue_Agent/app/backend/app/time_context.py)
  - [`time_freshness.py`](/E:/AI_XinQue_Agent/app/backend/app/time_freshness.py)
- 本地工作区已包含 `Sprint 21-28` 的长会话治理、时间感知上下文、时间新鲜度排序、多干预优先级等实现与文档。

### 4. 前端壳层与配置

- 新增环境化前端配置：
  - [`config.ts`](/E:/AI_XinQue_Agent/app/frontend/src/config.ts)
- 新增应用导航与页面结构相关文件：
  - [`navigation.ts`](/E:/AI_XinQue_Agent/app/frontend/src/navigation.ts)
  - [`pages/`](/E:/AI_XinQue_Agent/app/frontend/src/pages)
- 更新：
  - [`App.tsx`](/E:/AI_XinQue_Agent/app/frontend/src/App.tsx)
  - [`ChatWindow.tsx`](/E:/AI_XinQue_Agent/app/frontend/src/components/chat/ChatWindow.tsx)
  - [`AdminDashboard.tsx`](/E:/AI_XinQue_Agent/app/frontend/src/components/admin/AdminDashboard.tsx)

### 5. 文档治理与 Sprint 产物整理

- 重写并明确了文档目录治理规则，落点在：
  - [`AGENTS.md`](/E:/AI_XinQue_Agent/AGENTS.md)
  - [`CLAUDE.md`](/E:/AI_XinQue_Agent/CLAUDE.md)
- 明确了以下目录职责：
  - `docs/design`
  - `docs/plans`
  - `specs`
  - `contracts`
  - `evaluations`
  - `docs/testing`
- 补齐并整理了 `Sprint 19-35` 的 spec / contract / eval。
- 新增：
  - [`runtime-variable-reference-v1.md`](/E:/AI_XinQue_Agent/docs/design/runtime-variable-reference-v1.md)
  - [`manual-test-checklist-v1.md`](/E:/AI_XinQue_Agent/docs/testing/manual-test-checklist-v1.md)
- 调整并整理：
  - [`docs/plans/`](/E:/AI_XinQue_Agent/docs/plans)
  - [`docs/archive/`](/E:/AI_XinQue_Agent/docs/archive)

### 6. 手测中实际修掉的问题

- 修复了 Responses API 输入使用非法 `phase` 的问题：
  - 发给 OpenAI 的辅助 assistant message 现在使用合法 phase
  - 内部 trace 语义仍保留 `working_contract / working_context`
- 修复了 [`tool_runtime.py`](/E:/AI_XinQue_Agent/app/backend/app/tool_runtime.py) 中 `load_recent_interventions()` 的结果处理问题：
  - 不再在读取多行结果前提前关闭 SQLAlchemy `Result`
  - 不再把非 intervention 的 fallback 对象误当作 intervention
- 相关测试已更新：
  - [`test_xinque_trace.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)
  - [`test_tool_runtime.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_tool_runtime.py)
  - [`test_xinque_guardrails.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_guardrails.py)

### 7. 当前测试状态

- 当前本地后端测试通过 `134` 项：
  - `python -m unittest discover -s app/backend/tests -p "test_*.py"`
- 仍存在一个既有 sqlite `ResourceWarning`，但不影响测试通过。

### 8. 建议的提交拆分

- 提交 1：`Sprint 19-30` 的运行时、状态与 Responses 迁移主线
- 提交 2：`Sprint 31-34` 的 structured outputs / skills / tool runtime / Responses-first 架构
- 提交 3：`Sprint 35` 的 Prompt 指南落地、手测清单与手测中修掉的运行时问题

---

## 2026-03-30（架构优化补记）

### 总览

本条目补记本次围绕 Limbic 参考材料进行的架构审核与优化落地，重点是将“可执行约束”从口头建议落到架构文档中的结构化接口与运行时规则，作为后续 `product-plan-v3` 与实现拆分的输入基线。

### 1. Limbic 交叉审核结果已沉淀为 Appendix

- 已在 [`xinque-agent-counsellor-harness-architecture-v1.md`](/E:/AI_XinQue_Agent/docs/design/xinque-agent-counsellor-harness-architecture-v1.md) 新增 **Appendix A**。
- Appendix A 汇总了基于 `docs/reference/Limbic/` 全量材料的 10 项维度审核：
  - Flow state
  - formulate 结构化输入
  - recommender 回探回路
  - 匹配强度与阈值
  - direct intent 快捷路径
  - 理解信号来源标注
  - KnowledgeBank 检索注入
  - output safety regenerate loop
  - phase schema 路由字段分类
  - 心雀正面差异保留项

### 2. FlowModule 增补全局会话状态定义

- 在文档 `§5.4.2 FlowModule` 中新增 `SessionFlowState` 草案，明确：
  - `conversation_phase`
  - `transition_reason`
  - `last_prompt_generator`
  - `formulation_readiness`
  - `structured_items`
  - `needs_more_exploration`
  - `explore_more_targets`
  - `chosen_intervention`
  - `intervention_status`
- 明确该 state 由 Harness 维护，工具返回与路由结果写入统一状态对象，不由模型直接修改。

### 3. `formulate` schema 补强（P2）

- 在 `formulate` 参数中新增可选 `structured_items`（`asking_label + user_utterance`），用于保留“标签 + 原始用户表述”。
- 在返回对象中为 `emotions`、`cognitive_patterns` 条目增加 `detection_source` 预留位：
  - `llm_extraction | classifier | rule`
- 补充约束：`structured_items` 应累积写入 `SessionFlowState`，为后续子模型接入预留兼容路径。

### 4. `match_intervention` schema 补强（P3）

- 在 plan 对象中新增 `match_strength`（`high | medium | low`）。
- 在匹配为空或候选强度过低时，新增回探信号返回：
  - `needs_more_exploration`
  - `explore_more_targets`
- 明确该信号应写入 `SessionFlowState` 并驱动 Flow 回到 P2 持续探索。

### 5. 输出安全回路增强

- 在文档 `§5.3.2 OutputSafetyModule` 中补充 `output_safety_retry` 回路：
  - 安全失败后可在上限内重试生成（建议最大 2 次）
  - 每次重试注入 `[SAFETY_FEEDBACK]`
  - 超过上限时走 fallback safe response + 审计记录 + 可选人工标记

### 6. 阶段 schema 与路由规则显式化

- 在文档 `§7.4` 对 P1-P4 schema 增加字段角色标注：
  - `routing_field`
  - `content_field`
- 每个阶段补充 Flow 路由规则，减少“字段含义靠约定”的歧义。

### 7. Direct Intent 快捷路径补齐

- 在文档 `§6.2` 与 `§5.8.1 / §7.5` 中补充 direct intent 方案：
  - 新增 `resolve_direct_intent`（建议）作为 P1 快捷路径 tool
  - 支持用户明确提出干预需求时从 P1 直接进入 P4

### 8. 对当前代码实现的含义

- 本次主要是 **架构与契约层优化落地**（文档层），用于约束后续实现，不是一次性功能代码重构。
- 对 `app/` 代码的直接影响是提供了下一步实施的明确接口目标（Flow state、P2/P3 schema、safety retry、direct intent tool）。
