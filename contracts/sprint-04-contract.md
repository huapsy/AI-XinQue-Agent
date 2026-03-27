# Sprint 04 Contract — 探索与个案概念化

## 成功标准

### 数据库

1. **case_formulations 表**
   - alembic upgrade head 后新增 case_formulations 表

### formulate() Tool

2. **首次调用**
   - 对话中 LLM 探索到用户情绪后调用 formulate() → 数据库中创建 formulation 记录，readiness="exploring"

3. **增量更新**
   - 继续探索，LLM 多次调用 formulate() → formulation 记录的 cognitive_patterns / emotional_state 逐步丰富

4. **readiness 推进**
   - 当 formulation 包含情绪 + 认知 + 行为三个维度后 → readiness 从 "exploring" 变为 "sufficient" 或 "solid"

5. **mechanism 生成**
   - readiness="sufficient" 时 formulation 包含 mechanism 字段（问题维持机制描述）

### save_nickname() Tool

6. **昵称保存**
   - 用户告知昵称"小明" → LLM 调用 save_nickname → user_profiles.nickname = "小明"
   - 下次会话 recall_context() 返回 nickname="小明"

### 集成

7. **端到端探索流程**
   - 完整对话：用户倾诉工作压力 → 心雀探索情绪/认知/行为 → formulate() 多次调用 → formulation 逐步成熟 → readiness 达到 sufficient
   - 数据库中有完整的 formulation 记录
