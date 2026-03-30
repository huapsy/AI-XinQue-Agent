# Sprint 45 Contract

## 目标

把“四阶段只是单体 prompt 内部纪律”的实现，升级为“主 agent + 四阶段子 agent profile”的最小运行时结构，并保证不破坏当前单 agent 架构。

## 成功标准

1. phase profile 存在
   - 后端存在 4 个明确的 phase profile 定义：
     - `p1_listener`
     - `p2_explorer`
     - `p3_recommender`
     - `p4_interventor`
   - 每个 profile 至少包含：
     - display_name
     - goal
     - allowed_tools
     - prompt_block

2. prompt 组织完成拆分
   - `build_system_prompt()` 或等价入口支持传入 `active_phase`
   - 生成结果中保留 base contract
   - 生成结果中只注入当前 `active_phase` 对应的 phase profile block
   - 不同时注入多个 phase profile block

3. `active_phase` 可持久化、可跨轮可见
   - `active_phase` 进入 persisted session state
   - layered context / working contract / trace 中至少有一处能直接看到当前 `active_phase`

4. 不破坏当前主路径
   - 现有 `active_skill` 运行时逻辑仍保留
   - 现有 `build_working_contract_message()`、`build_layered_context()`、主 `chat()` 链路仍能正常运行

## 证据要求

- 定向单元测试覆盖：
  - phase profile 定义存在
  - system prompt 仅注入当前 phase block
  - `active_phase` 持久化与上下文可见
- 至少运行相关定向测试并记录通过结果

## 非验收项

- 不要求 phase 自动切换已经完整实现
- 不要求 phase-aware tool guardrail 已经接入
- 不要求对话质量在本轮就全面优化

