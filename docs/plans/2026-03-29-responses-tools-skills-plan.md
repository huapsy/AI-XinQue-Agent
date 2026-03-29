# Responses / Tools / Skills Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将心雀当前“已迁移到 Responses API，但仍混有文本 JSON、松散 tool state、自定义 skill 文档”的实现，升级成以 Responses 为中心、以严格 tools 为基础、以版本化 skills 为载体的长期架构。

**Architecture:** 这次重构不再做单点补丁，而是沿着三条主线连续收口。第一条线是输出协议，优先把 judge、summary、analysis 等关键链路迁到 Responses 原生 structured outputs。第二条线是能力载体，把当前 `.skill.md` 升级成可版本化、可索引、可校验的 manifest v2 + registry。第三条线是运行时，把 tool registry、tool state、phase timeline、stateful/stateless 策略统一成 Responses-first 的执行模型，并为将来接入官方 Skills 形态预留边界。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, React, Vite, TypeScript, Azure OpenAI Responses API, JSON Schema

## Current Progress

- `Sprint 31`：已完成
- `Sprint 32`：已完成
- `Sprint 33`：已完成
- `Sprint 34`：已完成

---

## Scope

这份计划覆盖 4 个连续 sprint：

1. `Sprint 31`：原生 Structured Outputs 与分析链路收口
2. `Sprint 32`：Skill manifest v2 与注册表
3. `Sprint 33`：Tool 运行时平台化与契约统一
4. `Sprint 34`：Responses-first 会话状态与官方 Skills 对齐

## Non-Goals

- 本轮不引入真人咨询师工作台改版
- 不切换数据库到 PostgreSQL
- 不直接接入官方 hosted Skills 作为生产依赖
- 不重写前端对话体验

## Success Criteria

- 关键分析输出不再依赖“文本 JSON + 本地清洗”
- 所有 tool 都有统一严格 schema、统一注册入口、统一执行状态
- skills 从纯 Markdown 说明文档升级成带 manifest/version/index/validator 的系统
- Responses 的 `instructions / working_contract / working_context / tool_state / store` 分层清晰
- 文档、测试、迁移和运行配置同步完成

## Sprint 31: 原生 Structured Outputs 与分析链路收口

**目标**

把 judge、summary、必要的分析输出从“文本 JSON 解析”迁到 Responses 原生结构化输出，减少解析脆弱性并与官方迁移指南一致。

**重点文件**

- Modify: `app/backend/app/evaluation_helpers.py`
- Modify: `app/backend/app/main.py`
- Modify: `app/backend/app/responses_helpers.py`
- Modify: `app/backend/app/agent/tools/formulate.py`
- Modify: `app/backend/tests/test_judge_evaluation.py`
- Modify: `app/backend/tests/test_summary_generation.py` 或同类测试
- Add/Modify: `app/backend/tests/test_structured_outputs.py`

**关键动作**

1. 梳理当前仍使用 `json.loads(raw_text)` 的链路。
2. 设计统一的 structured output helper，支持 `text.format` schema。
3. 优先迁移：
   - judge output
   - session summary output
   - formulation output（至少主对象）
4. 失败时保留降级路径，但必须能观测到“structured output failed / fallback used”。
5. 更新测试，覆盖 schema 成功、schema 失败、fallback。

## Sprint 32: Skill manifest v2 与注册表

**目标**

把当前 `app/skills/**/*.skill.md` 从“可被读取的干预说明文档”升级成“带清晰元数据和版本约束的 skill 包”。

**重点文件**

- Modify: `app/backend/app/agent/tools/load_skill.py`
- Modify: `app/backend/app/agent/tools/match_intervention.py`
- Add: `app/backend/app/skill_registry.py`
- Add: `app/backend/app/skill_manifest.py`
- Add: `app/backend/tests/test_skill_registry.py`
- Add: `app/backend/tests/test_skill_manifest_validation.py`
- Modify: `app/skills/**/*.skill.md`
- Add: `docs/design/runtime-variable-reference-v2.md` 或 skill 设计文档

**关键动作**

1. 定义 skill manifest v2 字段集：
   - identity: `name`, `version`, `display_name`, `category`
   - routing: `trigger`, `contraindications`, `cooldown_hours`
   - runtime: `output_type`, `card_template`, `estimated_turns`
   - guidance: `follow_up_rules`, `completion_signals`
2. 构建 registry/index，启动时或按需加载，不再每次 `rglob` 全量扫描。
3. 让 `match_intervention` 基于 registry 做路由与排序。
4. 让 `load_skill` 返回标准化 skill payload，而不是裸 body + 推断。
5. 增加 skill manifest 校验测试和 fixture。

## Sprint 33: Tool 运行时平台化与契约统一

**目标**

把当前 `xinque.py` 中分散的 tool 定义、tool state、preflight、result handling 提升为独立平台层，降低主 agent 文件耦合。

**重点文件**

- Modify: `app/backend/app/agent/xinque.py`
- Add: `app/backend/app/tool_registry.py`
- Add: `app/backend/app/tool_runtime.py`
- Add: `app/backend/app/tool_contracts.py`
- Modify: `app/backend/app/responses_helpers.py`
- Modify: `app/backend/tests/test_xinque_guardrails.py`
- Add: `app/backend/tests/test_tool_runtime.py`

**关键动作**

1. 抽出统一 tool registry。
2. 抽出统一 tool state 数据结构：
   - call identity
   - tool name
   - arguments
   - parsed payload
   - phase
   - timestamps
3. 抽出 preflight runtime，使 guardrails 与真实 tool execution 完全同源。
4. 规范 tool result envelope，避免每个 tool 各说各话。
5. 让 trace / phase timeline 与 tool runtime 自动对齐。

## Sprint 34: Responses-first 会话状态与官方 Skills 对齐

**目标**

把会话链路从“已经能用 Responses”推进到“按 Responses 官方心智建模设计”，并明确与官方 Skills 的边界。

**重点文件**

- Modify: `app/backend/app/agent/system_prompt.py`
- Modify: `app/backend/app/agent/xinque.py`
- Modify: `app/backend/app/session_context.py`
- Modify: `app/backend/app/settings.py`
- Add: `app/backend/app/responses_contract.py`
- Add: `docs/design/responses-tools-skills-architecture.md`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`

**关键动作**

1. 重新定义运行时分层：
   - `instructions`
   - `working_contract`
   - `working_context`
   - `tool_state`
   - `previous_response_id`
2. 明确 stateful vs stateless 策略，以及 `store=true/false` 行为。
3. 定义“官方 Skills 对齐层”：
   - 当前产品 skill 如何映射到未来 hosted/local Skills
   - 哪些仍属于产品层，不直接迁移
4. 补完整体架构文档和操作文档。

## Cross-Cutting Testing

- 每个 sprint 都必须先写失败测试，再做最小实现，再跑定向测试，再跑全量后端回归。
- 每个 sprint 都要更新：
  - `evaluations/sprint-XX-eval.md`
  - `docs/design/product-plan-v2-implementation-status.md`
- `Sprint 32+` 起补一组 fixture-based skill validation tests。
- `Sprint 33+` 起补一组 responses/tool-state regression tests。

## Execution Order

1. 先做 `Sprint 31`，因为 structured outputs 会影响后面 tool / skill 的结果协议。
2. 再做 `Sprint 32`，把 skill 载体规范住。
3. 然后做 `Sprint 33`，把运行时工具平台化。
4. 最后做 `Sprint 34`，统一 Responses-first 会话契约和官方 Skills 对齐。

## Risks

- structured outputs 迁移过程中，Azure Responses 的部分字段支持可能与公共文档略有差异，需要以本地实测为准
- skill manifest v2 需要批量改造 skill 文件，容易出现前后兼容问题
- tool runtime 平台化会触及 `xinque.py` 主循环，测试必须先补齐
- 如果 `store=false` 路径要完全可用，可能需要额外引入 encrypted reasoning items 设计

## Done Definition

- `Sprint 31-34` 的 spec、contract、evaluation 完整存在
- 每个 sprint 都有可复现测试证据
- 新架构文档能解释 Responses / tools / skills 三层关系
- 运行时不再依赖历史遗留的“文本 JSON + 动态猜测”路径作为主路径

Plan complete and saved to `docs/plans/2026-03-29-responses-tools-skills-plan.md`. Two execution options:

1. Subagent-Driven (this session) - I dispatch fresh subagent per task, review between tasks, fast iteration

2. Parallel Session (separate) - Open new session with executing-plans, batch execution with checkpoints

Which approach?
