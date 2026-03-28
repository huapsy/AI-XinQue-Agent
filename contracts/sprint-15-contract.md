# Sprint 15 Contract — 向量记忆升级与趋势深化

## 成功标准

1. `episodic_memories` 写入路径支持真实 embedding
2. `search_memory()` 检索优先使用向量召回，并保留可工作的降级路径
3. 趋势 payload 至少新增 trend direction 或等价判断字段
4. 前端趋势视图能消费新的趋势字段
5. 相关测试能覆盖召回、降级与趋势计算
