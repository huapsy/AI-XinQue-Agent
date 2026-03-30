# Sprint 46 Contract

## 目标

将四阶段子 agent profile 的使用，从“仅能显式指定当前 phase”升级为“由最小 flow state variables 驱动的 phase 路由”。

## 成功标准

1. 最小 flow state variables 存在
   - 后端有统一的 phase state 结构与默认值
   - 至少包含以下字段：
     - `active_phase`
     - `intent`
     - `explore`
     - `asking`
     - `formulation_confirmed`
     - `needs_more_exploration`
     - `chosen_intervention`
     - `intervention_complete`
     - `active_skill`

2. phase router 存在
   - 有独立的路由入口函数或模块
   - 可根据当前 phase state 输出：
     - 下一 `active_phase`
     - `transition_reason`

3. 核心路由规则成立
   - `intent=True` 时可直达 `p4_interventor`
   - `explore=True` 时可从 `p1_listener` 推进到 `p2_explorer`
   - `formulation_confirmed=True` 且信息充分时可推进到 `p3_recommender`
   - `active_skill` 存在时，默认不离开 `p4_interventor`，除非满足退出条件

4. 与现有主链路兼容
   - 现有 Responses + tool loop 主路径仍能运行
   - phase router 不得绕过安全层和现有 guardrail

## 证据要求

- 定向单元测试覆盖：
  - phase state 默认结构
  - phase router 基本分支
  - direct intent / active skill / formulation 路由规则
- 至少运行相关定向测试并记录通过结果

## 非验收项

- 不要求所有 phase 分支都已完全最优
- 不要求所有 tool 都已受 phase 权限控制

