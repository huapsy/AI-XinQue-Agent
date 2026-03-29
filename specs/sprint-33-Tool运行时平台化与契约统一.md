# Sprint 33 - Tool 运行时平台化与契约统一

## 背景

当前系统已完成 Responses-native tool definitions 和部分 guardrails，但 tool 定义、tool state、preflight、result envelope、trace 映射仍大量耦合在 `xinque.py` 中。

这种实现适合快速迭代，但不适合长期维护，尤其在后续 skill registry、structured outputs、stateful/stateless 策略继续升级后，会进一步加重主 Agent 文件的复杂度。

## 目标

将 tool 执行链路提升为独立平台层。

完成后应达到：

- tool 定义统一注册
- tool preflight 与真实执行状态完全同源
- tool result 有统一 envelope
- trace / phase timeline 与 tool runtime 自动对齐

## 范围

### 1. Tool Registry

新增独立 tool registry，负责：

- 注册 tool definition
- 注册执行函数
- 暴露给 Responses API 的可调用工具列表

### 2. Tool Runtime State

新增统一 tool state 结构，至少包含：

- tool name
- arguments
- resolved call id
- parsed payload
- status
- timestamps
- phase

### 3. Tool Result Envelope

规范所有 tool 返回至少包含：

- `status`
- `tool`
- `payload` 或 `error`

避免当前“有的 tool 返回裸对象，有的返回 error 字段，有的返回半结构化文本”的差异。

### 4. Guardrail Runtime

将 `load_skill` / `record_outcome` / `match_intervention` 等 guardrails 提升到 tool runtime 层，让它们读取统一 tool state，而不是散落在 Agent 主循环里。

## 非目标

- 不在本轮重写业务规则本身
- 不在本轮重构前端

## 验收结果

如果本轮完成，`xinque.py` 会显著变薄，tool 系统从“主循环内联逻辑”升级成“运行时平台层”。
