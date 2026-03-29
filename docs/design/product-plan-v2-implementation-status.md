# AI心雀 Plan v2 落地总览

**更新时间**: 2026-03-29
**基线文档**: [product-plan-v2.md](/E:/AI_XinQue_Agent/docs/design/product-plan-v2.md)
**当前结论**: `Sprint 01-18` 已完成；`Sprint 19` 已完成 GPT-5.4 Prompt Contract 与运行时 guardrail 的主线收口；`Sprint 20` 已完成 Responses API 核心迁移；`Sprint 21` 已完成长会话语义压缩与状态治理的首轮落地；`Sprint 22` 已完成语义摘要持久化与 phase/state timeline 的最小持久化版本；`Sprint 23` 已完成独立会话状态模型；`Sprint 24` 已完成会话状态版本历史与摘要演进治理的首轮落地；`Sprint 25` 已完成状态读取接口与时间线查询；`Sprint 26` 已完成时间感知上下文的最小运行时版本；`Sprint 27` 已完成时间新鲜度驱动的最小 prompt / Tool 路由规则；`Sprint 28` 已完成时间新鲜度排序与多干预优先级治理；`Sprint 29` 已完成全面审查后的架构收口与主路径重构；`Sprint 30` 已完成 Responses API 链路与守门补强；`Sprint 31` 已完成原生 Structured Outputs 第一轮收口，覆盖 Judge、Summary 与 Formulation 主对象；`Sprint 32` 已完成 Skill manifest v2 与 registry 的首轮落地；`Sprint 33` 已完成 Tool 运行时平台化与契约统一；`Sprint 34` 已完成 Responses-first 会话状态与官方 Skills 对齐；`Sprint 35` 已完成心雀 Prompt 指南落地。`plan-v2` 的主线能力已落地，剩余差距主要集中在更高阶的生产运营与企业化能力。

## 一句话判断

- `Phase 1` 已完成
- `Phase 2` 已完成
- `Phase 3` 已完成
- `Phase 4` 已完成主要能力，但仍保留少量生产级进阶项
- `Sprint 18` 已完成，已修复安全默认值、正向对齐、会话结束语义和前端路由问题
- `Sprint 19` 已基本完成，已完成 Prompt 参考规则、Prompt 分层契约、高影响动作 guardrail、空检索恢复和最小长会话治理
- `Sprint 20` 已完成主线迁移，Responses API 与跨轮 `previous_response_id` 已贯通
- `Sprint 21` 已完成首轮长会话语义压缩与状态分层治理
- `Sprint 22` 已完成语义摘要持久化与最小 `phase/state timeline` 记录
- `Sprint 23` 已完成独立会话状态模型与恢复优先级切换
- `Sprint 24` 已完成状态历史版本与摘要演进治理的最小实现
- `Sprint 25` 已完成状态读取接口与时间线查询
- `Sprint 26` 已完成时间感知上下文的最小运行时版本
- `Sprint 27` 已完成时间新鲜度驱动的最小 prompt / Tool 路由规则
- `Sprint 28` 已完成时间新鲜度排序与多干预优先级治理
- `Sprint 29` 已完成迁移链收口、Tool schema 源头统一、环境化配置和前端三入口壳层
- `Sprint 30` 已完成跨轮最小契约注入、同回合工具状态守门、Judge 解析增强与 `store` 配置化
- `Sprint 31` 已完成 Judge、会话摘要、Formulation 主对象的结构化结果收口
- `Sprint 32` 已完成 skill manifest v2、skill registry、registry-first 的 `load_skill()` 与 `match_intervention()` 首轮改造
- `Sprint 33` 已完成 tool registry、tool runtime、tool envelope 与主链路解耦
- `Sprint 34` 已完成 Responses-first 分层、stateful/stateless 说明与官方 Skills 对齐文档
- `Sprint 35` 已完成 Prompt 指南到运行时 prompt、Responses contract 与手测检查项的闭环

## Sprint 总表

| Sprint | 主题 | 评估状态 | 对应 plan-v2 主能力 |
|---|---|---|---|
| 01 | 项目骨架 | ✅ 通过 | 前后端骨架、基础会话流 |
| 02 | 核心 Agent 与数据基础 | ✅ PASSED | 单一 LLM + Tool Use、数据模型基础 |
| 03 | 安全层与用户上下文 | ✅ PASSED | 输入/输出安全层、`recall_context()` |
| 04 | 探索与个案概念化 | ✅ PASSED | `formulate()`、渐进式 case formulation |
| 05 | 推荐与干预 | ✅ PASSED | `match_intervention()`、`load_skill()`、`record_outcome()`、卡片干预 |
| 06 | 跨会话连续性 | ✅ PASSED | 会话摘要、作业跟进、历史关联 |
| 07 | 对齐兜底与转介 | ✅ PASSED | alignment score、`referral()`、风险兜底 |
| 08 | 前端体验与历史对话 | ✅ PASSED | 历史会话、情绪签到、前端交互完善 |
| 09 | 用户画像完善与 Profile 收口 | ✅ PASSED | `clinical_profile`、`update_profile()`、画像收口 |
| 10 | 情景记忆与 `search_memory` | ✅ PASSED | `episodic_memories`、记忆检索 |
| 11 | 可观测性与 Trace | ✅ PASSED | `traces`、Tool trace、查询接口、trace sink 抽象 |
| 12 | 评估、安全收口与产品化补完 | ✅ PASSED | LLM-as-Judge、red team、脱敏边界、情绪趋势 |
| 13 | 对齐正反馈与会话控制 Tool 化 | ✅ PASSED | `record_outcome +5`、`save_session()` |
| 14 | 卡片渲染解耦与多形态 Skill | ✅ PASSED | `render_card()`、通用 card renderer |
| 15 | 向量记忆升级与趋势深化 | ✅ PASSED | 稳定 embedding、趋势方向/波动 |
| 16 | 观测产品化与匿名统计 | ✅ PASSED | 匿名统计页、OTel 兼容 exporter |
| 17 | 数据安全加固与企业准备 | ✅ PASSED | 应用层字段加密、加密链路贯通 |
| 18 | 审查问题收口与契约纠偏 | ✅ PASSED | 加密默认值、正向对齐、`save_session()`、管理页路由、文档纠偏 |
| 19 | GPT-5.4 提示工程与运行契约升级 | ✅ SUBSTANTIALLY COMPLETE | Prompt Contract、Tool Contract、Completion / Verification Loop、最小长会话治理 |
| 20 | Responses API 与 Phase 感知迁移 | ✅ SUBSTANTIALLY COMPLETE | Responses API、跨轮 `previous_response_id`、phase-aware 协议流 |
| 21 | 长会话语义压缩与状态治理 | ✅ PASSED | 分层上下文、语义摘要、当前目标优先、检索边界治理 |
| 22 | 语义摘要持久化与 Phase 状态时间线 | ✅ PASSED | `persisted_session_state`、恢复优先级、`phase_timeline` |
| 23 | 独立会话状态模型 | ✅ PASSED | `SessionState`、主写状态模型、trace 回退兼容 |
| 24 | 会话状态版本历史与摘要演进治理 | ✅ PASSED | `SessionStateHistory`、最小版本规则、`change_reason/change_summary` |
| 25 | 会话状态读取接口与时间线查询 | ✅ PASSED | `state` / `state-history` / `timeline` 读取接口 |
| 26 | 时间感知上下文 | ✅ PASSED | `runtime_time_context`、相对时间、核心上下文透传 |
| 27 | 时间新鲜度驱动推理与 Tool 路由 | ✅ PASSED | recent intervention follow-up guardrail、prompt freshness contract |
| 28 | 时间新鲜度排序与多干预优先级治理 | ✅ PASSED | memory freshness ranking、primary follow-up selection、minimal cooling |
| 29 | 全面审查收口与架构重构 | ✅ PASSED | Alembic 收口、Responses-native tool schema、环境化配置、前端入口壳层、职责下沉 |
| 30 | Responses API 链路与守门补强 | ✅ PASSED | 跨轮最小契约、同回合 tool state 守门、judge 健壮性、store 配置化 |
| 31 | 原生 Structured Outputs 与分析链路收口 | ✅ PASSED | Judge、Summary、Formulation 主对象结构化协议 |
| 32 | Skill manifest v2 与注册表 | ✅ PASSED | manifest v2、skill registry、registry-first load/match |
| 33 | Tool 运行时平台化与契约统一 | ✅ PASSED | tool registry、tool runtime、统一 envelope、同回合 runtime state |
| 34 | Responses-first 会话状态与官方 Skills 对齐 | ✅ PASSED | runtime contract、stateful/stateless、技能架构对齐 |
| 35 | 心雀 Prompt 指南落地 | ✅ PASSED | Prompt 指南 -> 运行时 Prompt -> 测试 / 手测检查项闭环 |

## 与 plan-v2 的能力对齐

| plan-v2 能力 | 当前状态 | 主要落点 |
|---|---|---|
| Web 前端对话界面 | 已实现 | [ChatWindow.tsx](/E:/AI_XinQue_Agent/app/frontend/src/components/chat/ChatWindow.tsx) |
| 单一核心 Agent + Tool Use 循环 | 已实现 | [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) |
| 输入安全层 | 已实现 | [input_guard.py](/E:/AI_XinQue_Agent/app/backend/app/safety/input_guard.py) |
| 输出安全层 | 已实现 | [output_guard.py](/E:/AI_XinQue_Agent/app/backend/app/safety/output_guard.py) |
| `recall_context()` | 已实现 | [recall_context.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/recall_context.py) |
| `formulate()` | 已实现 | [formulate.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/formulate.py) |
| `match_intervention()` | 已实现 | [match_intervention.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/match_intervention.py) |
| `load_skill()` | 已实现 | [load_skill.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/load_skill.py) |
| `record_outcome()` | 已实现 | [record_outcome.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/record_outcome.py) |
| `update_profile()` | 已实现 | [update_profile.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/update_profile.py) |
| `search_memory()` | 已实现 | [search_memory.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/search_memory.py) |
| `referral()` | 已实现 | [referral.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/referral.py) |
| `save_session()` | 已实现 | [save_session.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/save_session.py) |
| `render_card()` | 已实现 | [render_card.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/render_card.py) |
| 用户画像结构化读写 | 已实现 | [profile_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/profile_helpers.py)、[tables.py](/E:/AI_XinQue_Agent/app/backend/app/models/tables.py) |
| 情景记忆 | 已实现，带稳定本地 embedding | [memory_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/memory_helpers.py) |
| Trace 与可观测性 | 已实现并产品化到匿名统计层 | [trace_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/trace_helpers.py)、[trace_sink.py](/E:/AI_XinQue_Agent/app/backend/app/trace_sink.py)、[otel_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/otel_helpers.py) |
| 自动评估 | 已实现 | [evaluation_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/evaluation_helpers.py) |
| Red Team 回归 | 已实现 | [red_team_runner.py](/E:/AI_XinQue_Agent/app/backend/app/red_team_runner.py) |
| 用户侧情绪趋势 | 已实现增强版 | [mood_trend_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/mood_trend_helpers.py)、[moodTrend.ts](/E:/AI_XinQue_Agent/app/frontend/src/components/chat/moodTrend.ts) |
| 管理侧匿名统计 | 已实现最小版 | [admin_metrics_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/admin_metrics_helpers.py)、[AdminDashboard.tsx](/E:/AI_XinQue_Agent/app/frontend/src/components/admin/AdminDashboard.tsx) |
| 应用层字段加密 | 已实现 | [encryption_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/encryption_helpers.py) |
| GPT-5.4 Prompt 约束治理 | 已部分实现 | [AGENTS.md](/E:/AI_XinQue_Agent/AGENTS.md)、[CLAUDE.md](/E:/AI_XinQue_Agent/CLAUDE.md)、[system_prompt.py](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) |
| Tool 前置约束与高影响动作 guardrail | 已部分实现 | [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)、[test_xinque_guardrails.py](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_guardrails.py) |
| Responses API 协议层 | 已部分实现 | [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)、[responses_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/responses_helpers.py) |
| 长会话语义压缩与状态分层 | 已实现首轮版本 | [session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py)、[xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)、[recall_context.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/recall_context.py) |
| 长会话状态持久化与 Phase 时间线 | 已实现最小版本 | [session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py)、[main.py](/E:/AI_XinQue_Agent/app/backend/app/main.py)、[xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) |
| 独立会话状态模型 | 已实现 | [tables.py](/E:/AI_XinQue_Agent/app/backend/app/models/tables.py)、[session_state_store.py](/E:/AI_XinQue_Agent/app/backend/app/session_state_store.py)、[main.py](/E:/AI_XinQue_Agent/app/backend/app/main.py) |
| 会话状态版本历史 | 已实现首轮版本 | [tables.py](/E:/AI_XinQue_Agent/app/backend/app/models/tables.py)、[session_state_store.py](/E:/AI_XinQue_Agent/app/backend/app/session_state_store.py) |
| 会话状态读取接口 | 已实现 | [main.py](/E:/AI_XinQue_Agent/app/backend/app/main.py)、[session_state_store.py](/E:/AI_XinQue_Agent/app/backend/app/session_state_store.py)、[trace_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/trace_helpers.py) |
| 时间感知上下文 | 已实现最小版本 | [time_context.py](/E:/AI_XinQue_Agent/app/backend/app/time_context.py)、[recall_context.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/recall_context.py)、[session_context.py](/E:/AI_XinQue_Agent/app/backend/app/session_context.py) |
| 时间新鲜度驱动的 prompt / Tool 路由 | 已实现最小版本 | [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)、[system_prompt.py](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) |
| 时间新鲜度排序与多干预优先级 | 已实现最小版本 | [time_freshness.py](/E:/AI_XinQue_Agent/app/backend/app/time_freshness.py)、[search_memory.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/search_memory.py)、[match_intervention.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/match_intervention.py) |
| 迁移链与配置收口 | 已实现首轮版本 | [f4c8e2b7a9d1_merge_heads_add_session_state_tables.py](/E:/AI_XinQue_Agent/app/backend/alembic/versions/f4c8e2b7a9d1_merge_heads_add_session_state_tables.py)、[settings.py](/E:/AI_XinQue_Agent/app/backend/app/settings.py)、[config.ts](/E:/AI_XinQue_Agent/app/frontend/src/config.ts) |
| 前端多入口应用壳层 | 已实现最小版本 | [App.tsx](/E:/AI_XinQue_Agent/app/frontend/src/App.tsx)、[HistoryPage.tsx](/E:/AI_XinQue_Agent/app/frontend/src/pages/HistoryPage.tsx)、[ChatWindow.tsx](/E:/AI_XinQue_Agent/app/frontend/src/components/chat/ChatWindow.tsx) |
| Responses 协议守门一致性 | 已实现增强版本 | [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)、[responses_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/responses_helpers.py)、[evaluation_helpers.py](/E:/AI_XinQue_Agent/app/backend/app/evaluation_helpers.py)、[settings.py](/E:/AI_XinQue_Agent/app/backend/app/settings.py) |
| Skill manifest v2 与注册表 | 已实现首轮版本 | [skill_manifest.py](/E:/AI_XinQue_Agent/app/backend/app/skill_manifest.py)、[skill_registry.py](/E:/AI_XinQue_Agent/app/backend/app/skill_registry.py)、[load_skill.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/load_skill.py)、[match_intervention.py](/E:/AI_XinQue_Agent/app/backend/app/agent/tools/match_intervention.py) |
| Tool 运行时平台化 | 已实现首轮版本 | [tool_registry.py](/E:/AI_XinQue_Agent/app/backend/app/tool_registry.py)、[tool_runtime.py](/E:/AI_XinQue_Agent/app/backend/app/tool_runtime.py)、[tool_contracts.py](/E:/AI_XinQue_Agent/app/backend/app/tool_contracts.py)、[xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) |
| Responses-first 会话契约与 Skills 对齐 | 已实现首轮版本 | [responses_contract.py](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py)、[responses-tools-skills-architecture.md](/E:/AI_XinQue_Agent/docs/design/responses-tools-skills-architecture.md)、[README.md](/E:/AI_XinQue_Agent/app/backend/README.md)、[xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) |
| Prompt 指南到运行时闭环 | 已实现首轮版本 | [05-心雀Prompt撰写指南-v1.md](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md)、[system_prompt.py](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)、[responses_contract.py](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py)、[manual-test-checklist-v1.md](/E:/AI_XinQue_Agent/docs/testing/manual-test-checklist-v1.md) |

## 当前代码与 plan-v2 的主要偏差

### 1. 情景记忆仍不是外部向量数据库版

当前已经是稳定 embedding + 混合检索，但仍不是独立向量服务或专门 ANN 索引。

### 2. 可观测性已能导出，但不是完整第三方 OTel 部署

当前已经有 OTel 兼容 exporter 与匿名统计页，但仍未接完整 collector / Grafana / Jaeger。

### 3. 隐私与安全已进入加密阶段，但不是企业级密钥体系

当前已经有：

- trace 脱敏
- summary 脱敏
- episodic memory 脱敏
- 评估 sample 脱敏
- 消息 / summary / memory 应用层加密

仍未完成：

- 企业级 KMS / 密钥轮换
- 企业权限系统
- 多租户隔离

### 4. GPT-5.4 风格运行契约已开始落地，但尚未完全收口

当前已经有：

- `AGENTS.md` / `CLAUDE.md` 中对 GPT-5.4 Prompt 参考文件的明确要求
- `system_prompt.py` 的分层契约化重构
- 对 `match_intervention`、`save_session`、`referral`、`load_skill`、`record_outcome` 的最小运行时 guardrail
- `search_memory` 的空结果 fallback
- 长会话的最小历史压缩策略
- 长会话的分层上下文与首轮语义压缩治理

仍未完成：

- 更完整的长会话 phase-aware / Responses API 迁移设计
- 语义摘要的独立持久化与更细粒度状态时间线

### 5. Responses API 已迁移核心链路，并完成最小长期状态化

当前已经有：

- 核心 Agent 主循环改用 Responses API
- 评估助手与会话摘要生成改用 Responses API
- 当前回合内与跨轮都已接入 `previous_response_id`
- trace 中记录 `endpoint`、`final_phase`、`response_ids`
- 最近一轮的 `persisted_session_state` 与 `phase_timeline` 已随 trace 持久化
- 当前会话状态已抽离到独立 `SessionState` 模型，trace 只保留兼容副本

仍未完成：

- 状态版本化与历史回溯能力
- 更完整的 assistant `phase/state timeline` 查询与聚合

## 仍然未完成或只完成最小版的项

| 能力 | 状态 | 说明 |
|---|---|---|
| 完整 OTel / Dashboard 部署 | 部分实现 | 已有 exporter，但无完整外部观测平台 |
| 外部向量数据库 / ANN 索引 | 部分实现 | 当前为本地稳定 embedding + 混合检索 |
| 企业级 KMS / 密钥轮换 | 未实现 | 当前是应用层对称加密 |
| 多租户与企业权限 | 未实现 | 仍未落地 |
| 更多 Skill 扩展 | 部分实现 | Skill 主链路已通，库仍可继续补 |
| GPT-5.4 长会话运行契约 | 已实现增强版本 | 已有 Prompt Contract、局部 guardrail、分层上下文、语义摘要、独立状态模型、状态历史、读取接口与时间感知上下文 |
| Responses API 长期状态化 | 已实现增强版本 | 已完成核心迁移，具备 `SessionState + SessionStateHistory + persisted_session_state + phase_timeline + read APIs` |

## 当前应如何理解“完成度”

如果以 `plan-v2` 的“能否支撑 MVP 主线”为标准，当前已经完成。

如果以 `plan-v2` 的“目标态生产系统”为标准，当前仍有少量进阶项未做，主要集中在：

1. 完整 observability 平台
2. 更强的外部向量检索
3. 企业级密钥与权限体系
4. 状态查询的分页/过滤与运营消费层
5. 更细粒度的 phase/state timeline 查询与聚合
6. 更强的主题连续性重排与跨 skill 冷却策略

## Claude Code 复审补充

### 总体完成度

| Phase | 完成度 | 状态 |
|---|---|---|
| Phase 1 核心对话 | 98% | 完整 |
| Phase 2 干预能力 | 95% | 完整 |
| Phase 3 记忆与生态 | 92% | 基本完整 |
| 整体 | ~94% | 相当成熟 |

### 已完整实现

- 核心架构：单 LLM + Tool Use 循环（ReAct 模式），最多 10 次迭代
- System Prompt：7 个模块齐全，双维度响应模型（内容特征 `P0-P4` + 对齐状态），包含对齐兜底注入
- Tool 集：当前主要 Tool 已全部落地，包括 `recall_context`、`formulate`、`match_intervention`、`load_skill`、`render_card`、`record_outcome`、`update_profile`、`search_memory`、`referral`、`save_nickname`、`save_session`
- 输入/输出安全层：危机关键词、注入防护、红线过滤均为硬编码安全网，可绕过 LLM
- 数据层：核心 8 张表已落地，包含 `case_formulations`、`episodic_memories`、`traces`
- 情景记忆：自动沉淀、去重、稳定向量化、跨会话检索已成立
- 可观测性：完整 trace 主链路、OTel 兼容导出、匿名统计已具备
- 对齐机制：负向兜底与正向强化闭环均已存在
- GPT-5.4 Prompt 治理：已开始把 Prompt 从单段说明重构为分层契约，并将参考规则上升到项目约束
- Responses API 迁移：核心 Agent、评估和摘要链路已不再依赖 `chat.completions`

### 主要剩余差距

#### P1：生产级 OTel 与外部可视化仍未落地

- 当前是 OTel 兼容 exporter，不是完整外部平台部署

#### P1：向量检索仍未接独立向量服务

- 当前本地实现已经够产品使用，但仍非目标态的外部索引

#### P2：企业级安全体系仍未完成

- 已有应用层加密，但还没有 KMS、密钥轮换、多租户权限

#### Sprint 18 已收口的复审问题

- 已移除固定默认加密密钥兜底
- 已修正 `record_outcome(completed=true)` 的 alliance 加分条件
- 已让 `save_session()` 真正结束会话
- 已修正匿名统计页返回动作与 hash 路由不一致问题

#### Sprint 19 当前进展

- 已在 `AGENTS.md` / `CLAUDE.md` 中加入 GPT-5.4 Prompt 参考规则
- 已将 `system_prompt.py` 重构为更明确的 contract-style 分层结构
- 已为 `match_intervention`、`save_session`、`referral` 增加最小前置 guardrail
- 已继续为 `load_skill`、`record_outcome` 增加 guardrail，并补充相应测试
- 已为 `search_memory` 增加空结果 fallback，并补充测试
- 已增加长会话最小压缩策略，并补充测试
- 后端 `unittest discover` 已跑通 63 个测试

#### Sprint 20 当前进展

- 已将 `xinque.py` 主循环迁移到 Responses API
- 已将 `evaluation_helpers.py` 与 `main.py` 中的摘要生成迁移到 Responses API
- 当前回合内与跨轮已使用 `previous_response_id`
- trace 已记录 `endpoint`、`final_phase`、`response_ids`
- 后端 `unittest discover` 已跑通 67 个测试

#### Sprint 21 当前进展

- 已新增 `session_context.py`，明确分层上下文结构
- 已将 `xinque.py` 从简单 `history compaction` 升级为“会话状态卡片 + working memory”
- 已在跨轮 `Responses` 输入中加入工作上下文，而不是只发送新用户句子
- 已在 `recall_context.py` 中补充 `retrieval_guidance`，明确 `recall_context` / `search_memory` / 语义摘要职责边界
- 后端 `unittest discover` 已跑通 69 个测试

#### Sprint 22 当前进展

- 已把最近一轮 `semantic_summary`、`current_focus` 与关键 `stable_state` 快照写入 `persisted_session_state`
- 已支持从最近 trace 恢复持久化长会话状态
- 已让 `build_layered_context()` 复用持久化摘要，同时保持本轮 `current_focus` 覆盖旧焦点
- 已为 `llm_trace` 增加 `phase_timeline`
- 后端 `unittest discover` 已跑通 71 个测试

#### Sprint 23 当前进展

- 已新增 `SessionState` 模型，独立承载会话当前状态
- 已新增 `session_state_store.py`，提供最小读写 helper
- 已让 `_load_previous_session_state()` 优先读取独立状态模型，再回退到 trace
- 已让 `/api/chat` 成功路径主写 `SessionState`
- trace 中仍保留 `persisted_session_state` 兼容副本
- 后端 `unittest discover` 已跑通 75 个测试

#### Sprint 24 当前进展

- 已新增 `SessionStateHistory` 模型
- 已为状态保存引入最小版本判定规则
- 已为历史版本增加 `change_reason` 与 `change_summary`
- 已让状态主写路径在更新当前态的同时按需生成历史版本
- 后端 `unittest discover` 已跑通 79 个测试

#### Sprint 25 当前进展

- 已新增 `/api/sessions/{session_id}/state`
- 已新增 `/api/sessions/{session_id}/state-history`
- 已新增 `/api/sessions/{session_id}/timeline`
- 已新增 read-side helper 与 timeline serializer
- 后端 `unittest discover` 已跑通 84 个测试

#### Sprint 26 当前进展

- 已新增 `time_context.py`
- 已为 `recall_context()` 注入 `runtime_time_context`
- 已为 `pending_homework` 与 `recent_interventions` 增加绝对时间和相对时间
- 已让 `session_context.py` 的核心上下文卡片显式展示当前时间和最近干预的相对时间
- 后端 `unittest discover` 已跑通 85 个测试

#### Sprint 27 当前进展

- 已在 `xinque.py` 中为 `match_intervention` 增加 recent intervention follow-up guardrail
- 已在 `xinque.py` 中为同一 skill 的 `load_skill` 增加 recent repeat guardrail
- 已允许用户在明确要求换方法、说明旧方法无效或要求重做时跳过 follow-up 阻止规则
- 已在 `system_prompt.py` 中加入时间新鲜度驱动的 follow-up 契约
- 后端 `unittest discover` 已跑通 90 个测试

#### Sprint 28 当前进展

- 已新增 `time_freshness.py`，统一 recent follow-up 选择与时间新鲜度排序逻辑
- 已让 `search_memory()` 在相关性接近时优先返回较新的记忆
- 已让多 intervention 场景先选出一个 primary follow-up 对象
- 已在 `match_intervention.py` 中加入刚做过同一 skill 的最小冷却降权
- 已同步更新 retrieval guidance 与 prompt 契约
- 后端 `unittest discover` 已跑通 96 个测试

### 复审结论

这次 Claude Code 复审的判断和本文件主结论一致：

- 当前实现整体质量高
- 架构基本遵循 `plan-v2`
- 安全层和可观测性完成度较高
- 现在最值得优先补的是更强的主题连续性重排、状态查询的分页/过滤、timeline 聚合分析、生产级观测平台和企业级安全体系

如果后续要继续开新 sprint，建议优先级如下：

1. 启动下一轮时间治理，补主题连续性 re-ranker 与更细粒度跨 skill 冷却策略
2. 接完整外部 OTel / Dashboard
3. 升级到独立向量数据库
4. 引入企业级密钥管理与权限体系
5. 继续扩 Skill 与运营能力

## 建议的下一步文档治理

建议把这份文件作为后续总入口，并保持三个同步动作：

1. 新增或调整 sprint 时，更新这里的“能力对齐”表
2. 完成评估后，更新这里的“状态”与“偏差”
3. 若 `product-plan-v2.md` 出现架构变更，优先更新这里，再决定是否重写 sprint 文档

## 参考文件

- [product-plan-v2.md](/E:/AI_XinQue_Agent/docs/design/product-plan-v2.md)
- [main.py](/E:/AI_XinQue_Agent/app/backend/app/main.py)
- [xinque.py](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)
- [ChatWindow.tsx](/E:/AI_XinQue_Agent/app/frontend/src/components/chat/ChatWindow.tsx)
- [sprint-12-eval.md](/E:/AI_XinQue_Agent/evaluations/sprint-12-eval.md)
