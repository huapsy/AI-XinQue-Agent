# AI心雀 Plan v2 落地总览

**更新时间**: 2026-03-28
**基线文档**: [product-plan-v2.md](/E:/AI_XinQue_Agent/docs/design/product-plan-v2.md)
**当前结论**: `Sprint 01-18` 已完成，`Sprint 18` 已收口 `Sprint 13-17` 复审中发现的关键问题；`plan-v2` 的主线能力现已落地，剩余差距主要集中在生产级进阶项。

## 一句话判断

- `Phase 1` 已完成
- `Phase 2` 已完成
- `Phase 3` 已完成
- `Phase 4` 已完成主要能力，但仍保留少量生产级进阶项
- `Sprint 18` 已完成，已修复安全默认值、正向对齐、会话结束语义和前端路由问题

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

## 仍然未完成或只完成最小版的项

| 能力 | 状态 | 说明 |
|---|---|---|
| 完整 OTel / Dashboard 部署 | 部分实现 | 已有 exporter，但无完整外部观测平台 |
| 外部向量数据库 / ANN 索引 | 部分实现 | 当前为本地稳定 embedding + 混合检索 |
| 企业级 KMS / 密钥轮换 | 未实现 | 当前是应用层对称加密 |
| 多租户与企业权限 | 未实现 | 仍未落地 |
| 更多 Skill 扩展 | 部分实现 | Skill 主链路已通，库仍可继续补 |

## 当前应如何理解“完成度”

如果以 `plan-v2` 的“能否支撑 MVP 主线”为标准，当前已经完成。

如果以 `plan-v2` 的“目标态生产系统”为标准，当前仍有少量进阶项未做，主要集中在：

1. 完整 observability 平台
2. 更强的外部向量检索
3. 企业级密钥与权限体系
4. 更丰富的 Skill 和运营能力

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

### 复审结论

这次 Claude Code 复审的判断和本文件主结论一致：

- 当前实现整体质量高
- 架构基本遵循 `plan-v2`
- 安全层和可观测性完成度较高
- 现在最值得优先补的是生产级观测平台和企业级安全体系

如果后续要继续开新 sprint，建议优先级如下：

1. 接完整外部 OTel / Dashboard
2. 升级到独立向量数据库
3. 引入企业级密钥管理与权限体系
4. 继续扩 Skill 与运营能力

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
