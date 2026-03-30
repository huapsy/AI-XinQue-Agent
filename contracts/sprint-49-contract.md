# Sprint 49 Contract

## 目标

把当前最小 phase router 升级为可审计的 `Flow Controller` 运行时闭环，使阶段字段、迁移规则、trace 与持久化状态使用同一套控制语义。

## 成功标准

1. Flow Controller 已成为单一控制平面入口
   - 后端存在明确的 `Flow Controller` 实现
   - `xinque.chat()` 不再直接用零散条件手动拼阶段迁移
   - `Flow Controller` 至少负责：
     - 字段默认值补全
     - 字段 normalization
     - 阶段迁移
     - `phase_transition_reason` 产出

2. `flow_state` 字段语义稳定
   - 默认 state 与 persisted state 至少包含：
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
   - `active_skill` 存在时优先进入或保持 `P4`
   - `intent=true` 不再无条件把 `P1` 直推到 `P4`

3. 阶段迁移规则符合设计文档
   - `P1 -> P2` 由 `explore=true` 驱动
   - `P1 -> P3` 由 `intent=true` 且无进行中 `active_skill` 驱动
   - `P2 -> P3` 需 `formulation_confirmed=true` 且 `needs_more_exploration=false`
   - `P3 -> P4` 需 `chosen_intervention != null`
   - `P4 -> P1` 需 `intervention_complete=true`

4. Prompt / contract / trace 三层对齐
   - `working_contract` 显式可见 flow controller 语义
   - system prompt 中可见阶段字段纪律
   - trace 中可见：
     - `phase_fields_raw`
     - `phase_fields_normalized`
     - `phase_routing`
     - `phase_transition_reason`

5. 证据充分
   - 有新的或更新后的单元测试覆盖 Flow Controller
   - 有 `xinque` 集成测试证明 controller 已接管主链路
   - 有 evaluation 文档记录结果、证据和残余问题

## 证据要求

- 定向测试结果
- 关键代码 diff
- trace 结构性验证
- `spec` / `contract` / `evaluation` 文档齐备

## 非验收项

- 不要求 assistant 已强制产出严格 JSON 结构化 phase fields
- 不要求 phase flow 已覆盖所有复杂对话边角情况
- 不要求 Evaluator 已通过真实浏览器做端到端 UI 验证
