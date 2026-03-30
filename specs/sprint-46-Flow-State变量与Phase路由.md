# Sprint 46 - Flow State变量与Phase路由

## 背景

Sprint 45 完成后，心雀将拥有 4 个阶段子 agent profile，但仍缺少稳定的 phase 路由依据。当前阶段切换主要依赖模型自由判断，不利于：

- 让主 agent 显式决定何时从 P1 进入 P2
- 让 P2/P3/P4 的进入和回退具备可验证证据
- 对齐 Limbic 风格的“结构化字段 + 本地路由”方法

因此需要在保持单 agent 架构的前提下，引入最小 flow state variables 与 phase router。

## 目标

- 定义一组最小 flow state variables
- 主 agent 根据这些字段选择当前 `active_phase`
- 保留高优先级快捷路径：
  - direct intent → 直达 P4
  - `active_skill` 存在 → 偏向维持 P4
  - misalignment / safety → 回退或停留 P1

## 范围

- 新增 phase state 数据结构
- 支持的最小字段至少包括：
  - `active_phase`
  - `intent`
  - `explore`
  - `asking`
  - `formulation_confirmed`
  - `needs_more_exploration`
  - `chosen_intervention`
  - `intervention_complete`
  - `active_skill`
- 新增 phase router，输出：
  - 下一 `active_phase`
  - `transition_reason`

## 非目标

- 不在本轮完成 phase-aware tool guardrail
- 不在本轮重做 formulate / match_intervention / load_skill 的内部业务逻辑
- 不做 step-level skill 工作流

## 预期结果

- 每轮运行时都有一份最小 phase state
- 主 agent 不再纯靠 prompt 猜测阶段，而是结合字段路由
- trace 中可看到 `transition_reason`
- 与现有 `active_skill` 锁定兼容

