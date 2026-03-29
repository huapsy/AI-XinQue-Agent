# Sprint 23 Contract — 独立会话状态模型

## 成功标准

1. 长会话状态已有独立状态模型承载，而不再只依附于 `TraceRecord.llm_call`
2. 恢复逻辑优先读取独立状态模型，并保留 trace 兼容回退路径
3. 写入逻辑已切到“主写独立状态、trace 仅兼容保留”
4. `Sprint 21/22` 的 layered context 继续可用且不压过当前回合目标
5. 至少存在自动化测试或可重复验证覆盖本次改造
