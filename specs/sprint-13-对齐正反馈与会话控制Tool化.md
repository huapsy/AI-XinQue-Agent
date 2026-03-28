# Sprint 13 Spec — 对齐正反馈与会话控制 Tool 化

## 目标

补齐 `plan-v2` 当前最重要的两个剩余缺口：对齐正向反馈闭环，以及会话结束能力的 Tool 化。

## 背景

截至 Sprint 12，系统的负向对齐兜底已经完整，但正向强化还没有形成闭环。Claude Code 复审指出，`record_outcome(completed=true)` 后没有自动给对齐分加 `+5`，这会让系统只会“降压和回退”，不会在成功干预后巩固联盟。

同时，当前会话摘要依赖 `/api/sessions/{session_id}/end`，功能上可用，但不符合 `plan-v2` 中 “`save_session()` 可被 LLM 主动调用” 的设计。

## 本 Sprint 范围

### 1. 对齐正反馈闭环

**做**：
- 当 `record_outcome()` 记录一次已完成的干预时：
  - 给当前用户 alliance `alignment_score +5`
  - 上限继续受现有上界保护
- 如果存在 `user_feedback=helpful`，允许再写入一次正向证据
- 保证这条路径与现有负向信号机制兼容

### 2. `save_session()` Tool

**做**：
- 新增 `save_session()` Tool
- Tool 能触发当前会话摘要生成与持久化
- 返回结构化结果，如：
  - `status`
  - `summary`
  - `session_id`
- 心雀可在适当时机主动调用，而不是只依赖前端 `/end`

### 3. 系统 Prompt 更新

**做**：
- 明确何时使用 `save_session()`
- 明确在什么情况下 `record_outcome()` 的完成态意味着联盟增强

### 4. 回归测试

**做**：
- 测试 `record_outcome(completed=true)` 后 alliance 分数增加
- 测试 `save_session()` 可独立生成摘要
- 测试已有 `/end` 路径不回退

## 不在范围

- `render_card()` 独立 Tool
- 新的 card 类型
- embedding / 向量数据库
- OTel 真接入
