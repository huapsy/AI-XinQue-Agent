# Sprint 09 Contract — 用户画像完善与 Profile 收口

## 成功标准

### 数据模型

1. **user_profiles 结构完善**
   - Alembic 迁移后，`user_profiles` 具备本 Sprint 约定的画像字段承载能力
   - 至少能稳定存储：`nickname`、`risk_level`、`alliance`、`preferences`、`clinical_profile`

### Profile 更新策略

2. **风险与对齐信息不互相覆盖**
   - 危机检测更新 `risk_level` 后，不会覆盖已有 `alliance` / `preferences`
   - 对齐分数更新 `alliance` 后，不会覆盖已有 `risk_level` / `clinical_profile`

3. **formulate 聚合入画像**
   - 对话中多次调用 `formulate()` 后，关键主题、认知扭曲、情绪、行为模式能聚合写入 `clinical_profile`
   - 写入逻辑是增量合并，而不是每轮整块覆盖

4. **用户偏好可持久化**
   - 用户明确表达偏好（如“我更喜欢直接一点”“我不太喜欢呼吸练习”）后，系统能把对应偏好写入 `preferences`

### recall_context 收口

5. **返回结构稳定**
   - `recall_context()` 返回结构清晰区分：
     - `profile_snapshot`
     - `last_session_summary`
     - `pending_homework`
     - `recent_interventions`
   - 不再继续向顶层无边界增加零散字段

### 集成

6. **端到端回访一致性**
   - 用户完成一次探索/干预后结束会话，再次开启新会话
   - 心雀能稳定利用画像信息（称呼、主题、偏好、对齐状态）开展回访
   - 多次回访中画像信息不会出现明显丢失或相互覆盖
