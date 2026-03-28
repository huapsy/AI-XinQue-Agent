# Sprint 10 Contract — 情景记忆与 search_memory

## 成功标准

### 数据库

1. **episodic_memories 表**
   - Alembic 迁移后新增 `episodic_memories` 表
   - 表中可存储：`user_id`、`session_id`、`content`、`topic`、`emotions`、`embedding`

### 记忆写入

2. **关键事件可沉淀为情景记忆**
   - 用户在对话中提到重要事件（如亲人住院、工作变动、反复出现的特定困扰场景）后，系统能写入一条 episodic memory

3. **不会无节制写入**
   - 普通寒暄、低信息量消息不会大量进入 episodic memories
   - 同一事件不会在短时间内重复写入多条近似记录

### search_memory() Tool

4. **相似检索有效**
   - 调用 `search_memory(query=...)` 时，能返回最相关的历史片段
   - 返回结果包含内容、时间、话题或情绪标签等必要上下文

5. **与 recall_context 分工明确**
   - `recall_context()` 仍返回稳定上下文（昵称、摘要、作业、最近干预）
   - `search_memory()` 只在需要更细粒度历史事件时按需调用

### 集成

6. **跨会话事件回忆**
   - 用户在新会话中重新提到旧人物/旧场景时，LLM 能调用 `search_memory()`
   - 回复中能自然关联更早的关键历史事件，而不只依赖上次会话摘要
