# Sprint 31 - 原生 Structured Outputs 与分析链路收口

## 背景

当前系统已迁移到 Responses API，但多个关键链路仍依赖“模型返回 JSON 文本，再由本地做 `json.loads` 或清洗”的旧模式。这种实现能工作，但脆弱、难观测，也不符合 OpenAI 关于 Responses 结构化输出迁移的官方建议。

这轮 sprint 的目标，是优先把高价值、低歧义的结构化输出改成 Responses 原生 structured outputs，让输出契约成为运行时的一部分，而不是后处理补丁。

## 目标

本轮只做分析与评估相关的结构化输出收口，不碰 skill registry 和 tool 平台化。

完成后应达到：

- `judge` 不再以文本 JSON 作为主协议
- `session summary` 有明确 schema 和降级策略
- `formulate` 至少主对象部分转为 schema 化输出
- 失败时能显式标记 fallback，而不是静默走文本解析

## 范围

### 1. Judge 结构化输出

将当前 `run_llm_judge()` 从“请求文本 → 提取 fenced json → `json.loads`”迁移到 Responses 原生 structured outputs。

要求：

- 定义明确的 judge schema
- 统一 helper 封装
- 如果结构化输出失败，返回带 `error.type=judge_parse_error` 的结构化错误对象

### 2. Session Summary 结构化输出

将会话摘要生成链路改成 schema 化请求，避免靠自由文本再截断/清洗。

要求：

- 摘要仍保留人类可读文本字段
- 同时保留最小结构字段，如主题、开放问题、建议 follow-up
- 若失败，继续保留现有降级策略

### 3. Formulation 主对象结构化输出

将 `formulate()` 中最稳定的对象部分迁到 schema 化返回，至少包括：

- `primary_issue`
- `readiness`
- `mechanism`
- `missing`
- `context/themes`

允许保留部分自由文本说明，但主对象必须是 schema 化结构。

### 4. 统一 Structured Output Helper

新增或重构统一 helper，负责：

- 构造 `text.format`
- 执行请求
- 读取结构化结果
- 失败时返回带上下文的错误对象

## 非目标

- 不在本轮改 skill 文件结构
- 不在本轮重写 tool registry
- 不在本轮改前端

## 验收结果

如果本轮完成，系统会从“Responses API + 文本 JSON 混用”推进到“Responses API + 原生结构化输出作为主路径”，为后续 tool/skill 系统彻底收口打基础。
