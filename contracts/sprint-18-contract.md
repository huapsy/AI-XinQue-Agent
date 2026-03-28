# Sprint 18 Contract — 审查问题收口与契约纠偏

## 成功标准

1. 未配置 `XINQUE_ENCRYPTION_KEY` 时，系统不会使用固定默认密钥继续运行，而会显式失败或给出明确错误
2. `record_outcome(completed=true)` 会独立触发 alliance 加分，且不依赖 `user_feedback=helpful/unhelpful`
3. `save_session()` 调用后，会话摘要被保存，`ended_at` 被写入，并且行为与 `/api/sessions/{session_id}/end` 保持一致
4. 管理页与聊天页之间的切换遵循 hash 路由，不产生不必要的整页跳转
5. `Sprint 13/14/16/17` 的 eval 和 implementation status 中，不再保留与真实实现不一致的表述
6. 至少存在自动化测试或可重复验证覆盖以上修复

