# Sprint 22 Contract — 语义摘要持久化与 Phase 状态时间线

## 成功标准

1. `semantic_summary` 与关键长会话状态已可持久化和恢复，而不是只存在于单轮运行时
2. 一轮对话内部的 `phase/state timeline` 已被结构化记录，而不再只有 `final_phase`
3. 长会话恢复具备明确的加载优先级，不再默认全量重算历史
4. `Sprint 21` 的 layered context 已与持久化状态打通且不压过当前回合目标
5. 至少存在自动化测试或可重复验证覆盖本次改造
