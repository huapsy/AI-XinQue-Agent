# Sprint 48 Contract

## 目标

为“主 agent + 四阶段子 agent profile”架构补齐可观测性、评估闭环和权威设计文档回写，形成可审计、可交接的稳定产品设计。

## 成功标准

1. phase 路由证据可观测
   - trace 中可见：
     - `active_phase`
     - `phase_transition_reason`
     - `phase_profile_selected`
   - 若 tool 被 phase 阻止，trace 中可见相关记录

2. phase 评估闭环存在
   - 有覆盖 phase 路由与 guardrail 的定向测试
   - Evaluator 文档模板可区分：
     - phase 选择正确性
     - phase-aware tool guardrail
     - skill 连续性
     - 负向 flow 不越级推进

3. 权威设计完成回写
   - `docs/design/product-plan-v2.1.md` 已回写稳定规则，或新增 `docs/design/product-plan-v2.2.md`
   - `runtime-variable-reference-v1.md` 或等价文档已纳入 phase state 说明

4. 实施状态文档更新
   - `product-plan-v2-implementation-status.md` 反映 v2.2 phase-agent 架构首轮落地状态

## 证据要求

- 定向测试结果
- trace 示例或结构性验证
- 文档 diff 或新增权威文档

## 非验收项

- 不要求 phase 架构已经是最终形态
- 不要求所有对话质量问题都已完全消失

