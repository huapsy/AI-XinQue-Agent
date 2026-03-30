# Sprint 47 - Phase-aware Tool Guardrail与运行时状态收口

## 背景

Sprint 46 之后，主 agent 将具备 `active_phase` 和 phase router，但如果 tool 运行时仍不感知当前阶段，就会出现：

- 在 `p1_listener` 误调用 `match_intervention()`
- 在 `p2_explorer` 过早 `load_skill()`
- `active_phase` 与 `active_skill` 状态互相打架

因此需要把 phase 概念接入 tool runtime，形成 phase-aware guardrail。

## 目标

- 为每个 phase 定义允许调用的 tool 集
- tool preflight 接收 `active_phase`
- 非当前 phase 的 tool 调用返回结构化 blocked payload
- 收口 `active_phase` 与 `active_skill` 的优先级关系

## 范围

- phase -> allowed_tools 映射
- `preflight_tool_call()` 增加 `active_phase`
- blocked payload 结构统一
- 规定：
  - `active_skill` 存在时，`active_phase` 默认强制对齐到 `p4_interventor`

## 非目标

- 不重做技能内容本身
- 不在本轮改造前端展示
- 不把所有回复质量问题归因于 phase runtime

## 预期结果

- 非法跨 phase tool 调用被明确阻止
- blocked 返回可观测、可测试
- `active_phase` 与 `active_skill` 不再冲突
- 主 agent 的 phase 选择和 tool 权限形成闭环

