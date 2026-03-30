# Sprint 50 Contract

## 目标

为四阶段架构补齐 assistant 显式阶段字段输出契约，并建立多轮脚本级 evaluator 闭环，使 `Flow Controller` 不再主要依赖隐式推导。

## 成功标准

1. assistant 阶段字段输出契约存在
   - 系统中定义了最小阶段字段 schema
   - assistant 每轮可稳定产出该字段对象，至少覆盖：
     - `intent`
     - `explore`
     - `asking`
     - `formulation_confirmed`
     - `needs_more_exploration`
     - `chosen_intervention`
     - `intervention_complete`

2. Flow Controller 已消费 assistant 显式字段
   - `Flow Controller` 优先消费 assistant 输出字段
   - 字段缺失时有默认值补全
   - 字段与 runtime 事实冲突时有明确纠偏规则

3. 关键阶段字段已进入主链路
   - `asking` 可进入 `flow_state`、persisted state 和 trace
   - `chosen_intervention` 可显式驱动 `P3 -> P4`
   - `intervention_complete` 可显式驱动 `P4 -> P1`

4. evaluator 多轮脚本闭环存在
   - 至少有覆盖以下场景的脚本级验证：
     - `P1 -> P2`
     - `P2 -> P3`
     - `P3 -> P4`
     - `P4 -> P1`
     - 负向样本不越级推进
   - 评估证据不只依赖单元测试，还包括多轮对话样本

5. 文档与测试齐备
   - `spec`、`contract`、`evaluation` 三件套齐备
   - 有定向测试结果和可读证据

## 证据要求

- assistant 阶段字段 schema 或解析链路的代码证据
- 定向测试结果
- 多轮 evaluator 样本或脚本结果
- trace 或持久化状态中字段流转证据

## 非验收项

- 不要求所有复杂真实对话都已完美命中阶段字段
- 不要求完全去掉 runtime 推导
- 不要求前端直接展示阶段字段
