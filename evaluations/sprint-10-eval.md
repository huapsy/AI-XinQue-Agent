# Sprint 10 评估报告

**日期**: 2026-03-28
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | episodic_memories 表 | ✅ | 新增模型 + Alembic 迁移，字段包含 user/session/content/topic/emotions/embedding |
| 2 | 关键事件可沉淀为情景记忆 | ✅ | `main.py` 已接入自动写入；重要事件消息可生成 memory candidate |
| 3 | 不会无节制写入 | ✅ | 低信息量消息被过滤；近似重复事件会被去重 |
| 4 | search_memory 相似检索有效 | ✅ | `search_memory()` 会按 query 相似度返回最相关记忆 |
| 5 | recall_context 与 search_memory 分工明确 | ✅ | `recall_context` 保持稳定上下文；`search_memory` 作为按需检索补充写入 prompt |
| 6 | 跨会话事件回忆 | ✅ | 新增 workplace 场景测试，`周会紧张` query 能命中历史事件 |

## 本 Sprint 产出

### 后端新增
- `app/backend/app/memory_helpers.py` — 情景记忆候选提取、去重、相似度排序、自动写入 helper
- `app/backend/app/agent/tools/search_memory.py` — 按 query 检索更早历史事件的 Tool
- `app/backend/alembic/versions/c2b7f2a1d4e9_add_episodic_memories_table.py` — 新增 `episodic_memories` 表
- `app/backend/tests/test_memory_helpers.py`
- `app/backend/tests/test_search_memory.py`
- `app/backend/tests/test_episodic_memory_capture.py`

### 后端修改
- `app/backend/app/models/tables.py` — 新增 `EpisodicMemory` 模型
- `app/backend/app/agent/xinque.py` — 注册 `search_memory` Tool
- `app/backend/app/agent/system_prompt.py` — 新增 `search_memory` 使用指南
- `app/backend/app/main.py` — 对正常对话新增情景记忆自动写入

### 数据库迁移
- `c2b7f2a1d4e9_add_episodic_memories_table.py`

### 测试
- `python -m unittest discover -s tests -p 'test_*.py'` → 19 tests passed
- `python -m py_compile app/memory_helpers.py app/agent/tools/search_memory.py app/main.py app/models/tables.py` → passed

## 亮点

- Sprint 10 第一版没有依赖外部 embedding 服务，先用确定性的轻量相似度把存储与检索链路跑通
- `search_memory` 已经能命中“妈妈住院”“周会紧张”这类具体历史事件，而不只依赖上次摘要
- 自动写入路径已经接到正常聊天流程中，关键事件会自然沉淀为 episodic memory

## 注意事项

- 当前 `embedding` 为轻量 token 表示，属于开发阶段替代方案；后续可替换为真实 embedding 服务
- 当前记忆提取策略仍偏保守，目的是先避免噪音过多
- 尚未加入前端可见的 memory 调试界面；当前以后端测试和 Tool 调用为主
