# Sprint 44 Contract

## 目标

把“推荐并进入某个 skill 后，应在多轮中继续沿该 skill 执行直到完成或退出”变成可验证的运行时契约，而不是只靠模型自行记忆。

## 成功标准

1. `active_skill` 持久化
   - 当 `load_skill()` 成功加载某个 skill 后，持久化 session state 中会记录该 `active_skill`
   - `active_skill` 至少包含 `skill_name`

2. 跨轮可见
   - 下一轮构建的 layered context / working contract / prompt 能看到当前 `active_skill`
   - 契约中明确说明：未完成前优先继续当前 skill，除非用户明确拒绝、要求切换，或危机接管

3. 运行时守门
   - 当存在 `active_skill` 且用户未明确反对、未要求换方法、未进入危机场景时：
     - `match_intervention()` 会被阻止
     - 新的 `load_skill()` 会被阻止
   - 阻止结果必须是结构化 blocked payload

4. 退出条件
   - 当用户明确表示不想继续、要换方法、当前方法不适合时，允许退出 `active_skill`
   - 当 `record_outcome()` 成功记录当前 skill 结果后，`active_skill` 被清除

## 证据要求

- 定向单元测试覆盖：
  - `active_skill` 持久化与恢复
  - `active_skill` 存在时的 tool guardrail
  - 用户反对 / 切换时 guardrail 放行
  - `record_outcome()` 后 `active_skill` 清除
- 至少运行相关定向测试并记录通过结果

## 非验收项

- 不要求 step 级自动推进器
- 不要求对话级大模型行为完全稳定
- 不要求所有 skill 都带结构化 current_step
