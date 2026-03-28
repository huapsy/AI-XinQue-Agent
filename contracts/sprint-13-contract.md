# Sprint 13 Contract — 对齐正反馈与会话控制 Tool 化

## 成功标准

1. `record_outcome(completed=true)` 后，用户 alliance 分数会按规则增加，且不突破上限
2. 正向 alliance 更新不会破坏现有负向兜底逻辑
3. 存在可调用的 `save_session()` Tool，能生成并保存当前会话摘要
4. 现有 `/api/sessions/{session_id}/end` 仍可正常工作，不回退
5. 至少有自动化测试覆盖对齐加分与会话摘要 Tool 路径
