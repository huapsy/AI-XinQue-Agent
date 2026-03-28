# Sprint 18 Spec — 审查问题收口与契约纠偏

## 目标

针对 `Sprint 13-17` 代码复审中发现的真实问题做一次集中收口，补齐安全默认值、对齐正反馈、会话结束语义和管理端路由一致性，同时纠正文档与实现不一致的地方。

## 背景

当前系统的主链路已经跑通，但最新复审指出 4 个具体问题：

- 加密能力在缺少环境变量时会静默退回固定默认密钥
- `record_outcome(completed=true)` 的正向对齐加分仍被 `user_feedback` 分支错误门控
- `save_session()` 只保存摘要，不真正结束会话
- 管理页返回入口与前端 hash 路由不一致

这些问题不需要再拆成多个 sprint；它们共享一个明确目标：让 `Sprint 13-17` 的实现与 contract、eval、implementation status 的结论真正一致。

## 本 Sprint 范围

### 1. 加密默认值收口

**做**：
- 移除固定默认密钥兜底
- 明确要求 `XINQUE_ENCRYPTION_KEY` 必须存在
- 在应用启动阶段尽早失败，而不是运行时静默降级
- 保留对已有密文的正常解密能力

### 2. 正向对齐闭环纠偏

**做**：
- 让 `record_outcome(completed=true)` 与 `user_feedback` 解耦
- `completed=true` 时按规则增加 alliance 分数
- 偏好写入逻辑继续只受 `helpful / unhelpful` 控制

### 3. `save_session()` 语义补全

**做**：
- 明确 `save_session()` 不只是保存摘要，还应结束当前会话
- 补齐 `ended_at` 写入
- 保证与现有 `/api/sessions/{session_id}/end` 语义一致，避免两套结束逻辑分叉

### 4. 管理页路由一致性

**做**：
- 让匿名统计页返回动作遵循当前 hash 路由设计
- 避免不必要的整页跳转或部署路径问题

### 5. 文档与评估纠偏

**做**：
- 修正 `Sprint 13/14/16/17` 相关文档中的过度表述
- 在 implementation status 中把本次收口纳入状态说明

## 不在范围

- 新开更大的生产化 sprint
- 完整外部 OTel 平台接入
- 外部向量数据库
- 企业级 KMS、轮换、多租户权限

## 验收关注点

- 安全配置缺失时，系统应明确失败而非静默弱化
- `completed=true` 即可触发正向 alliance 加分
- `save_session()` 调用后，会话列表可见 `ended_at`
- 管理页与聊天页之间切换不依赖整页刷新
- 文档声明与代码行为一致
