# Sprint 34 - Responses-first 会话状态与官方 Skills 对齐

## 背景

系统当前已经使用 Responses API，并具备 `previous_response_id`、`working_contract`、`working_context`、`store` 开关等能力，但整体仍是“从 Chat Completions 迁移而来”的心智模型。

同时，项目内部的 intervention skills 与 OpenAI 官方 Skills 文档在概念上接近，但实现层并未明确区分“产品技能”与“平台技能”。

## 目标

这轮 sprint 的目标，是明确建立 Responses-first 运行时分层，并给 skill 系统补上与官方 Skills 的对齐设计边界。

完成后应达到：

- `instructions / working_contract / working_context / previous_response_id / store` 的职责清楚
- stateful / stateless 两种模式的行为有文档和代码约束
- 项目内部 skills 与官方 Skills 的映射关系被正式定义

## 范围

### 1. Responses-first Runtime Contract

统一定义：

- `instructions`：当前请求级高优先级行为约束
- `working_contract`：跨轮必须可见的最小行为契约
- `working_context`：分层会话状态与历史摘要
- `previous_response_id`：服务端上下文串接
- `store`：是否使用 stateful Responses

### 2. Stateful / Stateless 策略

定义并实现：

- `store=true` 的默认状态链路
- `store=false` 时的降级或受限行为
- 若将来需要 ZDR，对 encrypted reasoning items 预留设计说明

### 3. 官方 Skills 对齐层

新增设计文档，明确：

- 当前心雀 skill 属于产品层能力包
- 未来若使用官方 Skills，哪些 metadata 可以直接映射
- 哪些执行协议仍应留在产品层，不直接依赖平台 Skills

## 非目标

- 本轮不直接接入 hosted Skills
- 不要求前端展示官方 Skills 元数据

## 验收结果

如果本轮完成，心雀的 Responses 架构将从“迁移完成”推进到“概念清晰、运行分层稳定、可对接官方能力模型”。
