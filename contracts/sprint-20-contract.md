# Sprint 20 Contract — Responses API 与 Phase 感知迁移

## 成功标准

1. 核心对话循环已从 Chat Completions 迁移到 Responses API
2. 运行时能够显式区分中间工作态、工具调用态和最终答复态
3. 历史重放或对话延续时，assistant 的 `phase` 语义不会丢失
4. `/api/chat` 对前端的返回协议保持兼容
5. trace 中能够观察到 phase-aware 的协议流
6. 至少存在自动化测试或可重复验证覆盖本次迁移
