# Sprint 48 - Phase可观测性、评估闭环与权威设计回写

## 背景

Sprint 45-47 完成后，心雀将拥有：

- 主 agent + 4 个阶段子 agent profile
- 最小 flow state variables 与 phase router
- phase-aware tool guardrail

但若缺少 phase 级可观测性和设计回写，架构仍会停留在“代码有了、文档和评估跟不上”的状态，难以形成稳定产品真相。

## 目标

- 让 trace、contract、eval 能直接看到 phase 路由证据
- 补足 phase 架构的回归测试与对话级评估
- 根据落地结果决定回写：
  - `product-plan-v2.1.md`
  - 或新增 `product-plan-v2.2.md`

## 范围

- 扩展 trace，记录：
  - `active_phase`
  - `phase_transition_reason`
  - `phase_profile_selected`
  - `tool_blocked_by_phase`
- 为新架构建立评估模板
- 更新实施状态文档
- 回写权威设计文档中的稳定规则

## 非目标

- 不在本轮继续新增新的业务能力
- 不在本轮引入新的前端产品功能

## 预期结果

- phase routing 在 trace 中可见
- Evaluator 可以独立验证 phase 行为
- `v2.2` 架构不再只是计划，而成为有文档、有证据的稳定设计

