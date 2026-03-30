# Sprint 47 Contract

## 目标

让主 agent 的 phase 选择真正影响 tool runtime，形成 phase-aware tool guardrail，并与现有 `active_skill` 锁定规则兼容。

## 成功标准

1. phase-aware allowed tools 生效
   - 每个 phase 有明确 `allowed_tools`
   - preflight 使用当前 `active_phase` 判断工具是否允许

2. 非法 tool 调用被结构化阻止
   - 当 tool 不属于当前 phase 的 allowed set 时，返回结构化 blocked payload
   - payload 至少包含：
     - `status=blocked`
     - `tool`
     - `reason=phase_tool_not_allowed`
     - `active_phase`

3. 关键 phase 权限成立
   - `p1_listener` 不允许直接 `match_intervention()` / `load_skill()`
   - `p2_explorer` 可 `formulate()`，但不应直接切入新的 skill 执行
   - `p3_recommender` 可 `match_intervention()`，但仍需用户接受后才能 `load_skill()`
   - `p4_interventor` 允许 `load_skill()` / `record_outcome()`，并优先继续当前 skill

4. `active_phase` 与 `active_skill` 收口规则成立
   - 当存在 `active_skill` 时，`active_phase` 默认与 `p4_interventor` 一致
   - 不出现 `active_skill` 仍在执行但 phase 停留在 P1/P2/P3 的冲突状态

## 证据要求

- 定向单元测试覆盖：
  - phase allowed tools
  - 结构化 blocked payload
  - `active_skill` 与 `active_phase` 对齐
- 至少运行相关定向测试并记录通过结果

## 非验收项

- 不要求 phase router 完全无误判
- 不要求所有自由回复质量问题在本轮全部解决

