# Sprint 49 - Flow Controller 与阶段输出契约闭环

## 背景

Sprint 45-48 已完成：

- 主 Agent + 四阶段 phase profile
- 最小 phase state 与 phase router
- phase-aware tool guardrail
- 基础 phase trace 与权威设计回写

但当前运行时仍停留在“最小 phase router”层级，和 [`06-Flow模块与阶段子Agent架构-v1.md`](../docs/design/06-Flow模块与阶段子Agent架构-v1.md) 定义的目标状态仍有明显差距：

- `phase_router` 仍是薄规则函数，不是完整的 `Flow Controller`
- 最小状态未形成明确的 normalization / routing / trace 闭环
- assistant 侧没有清晰的阶段输出契约
- `asking`、`chosen_intervention`、`intervention_complete` 等字段尚未形成稳定运行时语义
- `xinque.chat()` 内的阶段推进仍以零散推导为主，缺少单一控制平面

## 目标

- 把当前最小 `phase router` 收口为 `Flow Controller`
- 建立最小但稳定的阶段字段 schema、normalization 与 routing 机制
- 让主 Agent、working contract、trace、persisted state 看到同一套 `flow_state`
- 让 `P1 -> P2 -> P3 -> P4 -> P1` 的核心迁移规则具备代码级闭环
- 为后续 evaluator 提供独立可验证的阶段证据

## 范围

- 后端运行时
  - 新增或重构 `Flow Controller` 控制平面
  - 统一 `flow_state` 字段默认值、归一化、迁移理由
  - 将 `xinque.chat()` 中零散的 phase 推导收口为 controller 调用
- Prompt / runtime contract
  - working contract 中显式可见 flow controller 字段语义
  - system prompt 中显式说明阶段字段及其运行时意义
- 可观测性
  - trace 中记录 raw fields / normalized fields / routing result
  - persisted session state 保持与 controller 一致
- 测试
  - Flow Controller 单元测试
  - `xinque` 集成测试
  - contract / context / trace 的回归测试

## 非目标

- 不在本轮引入新的业务 Tool
- 不在本轮把 assistant 阶段字段改成强制 Structured Output JSON 模式
- 不在本轮重做前端交互
- 不在本轮实现完整的 Limbic 式 `52a/52b/52c/52d` prompt generator 体系

## 预期结果

- 代码中存在单一 `Flow Controller` 入口，而不是零散 phase 条件拼接
- `flow_state` 至少稳定包含：
  - `active_phase`
  - `phase_transition_reason`
  - `intent`
  - `explore`
  - `asking`
  - `formulation_confirmed`
  - `needs_more_exploration`
  - `chosen_intervention`
  - `intervention_complete`
  - `active_skill`
- `P1` 不再把 `intent=true` 直接等同于“立即进入 P4 开始执行”
- 存在 `active_skill` 时，`P4` 优先级高于普通入口
- trace、working contract、persisted state 三处看到一致的阶段控制信息
- evaluators 可以依据文档和测试独立判断 phase flow 是否符合设计
