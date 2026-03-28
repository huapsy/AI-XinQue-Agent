# Sprint 11 Contract — 可观测性与 Trace

## 成功标准

### 数据库

1. **traces 表**
   - Alembic 迁移后新增 `traces` 表
   - 能存储每轮对话的 trace 结构

### Trace 生成

2. **正常对话 trace**
   - 一次正常聊天请求后，数据库中新增对应 trace
   - trace 至少包含：
     - 输入安全层结果
     - LLM 调用信息
     - Tool 调用记录（如有）
     - 输出安全层结果
     - 总耗时

3. **危机绕过 trace**
   - 危机输入触发输入安全层、绕过 LLM 时，仍会生成完整 trace
   - trace 中明确标识“未调用 LLM”的原因

4. **Tool 调用 trace**
   - 当 LLM 调用 `recall_context()`、`formulate()`、`load_skill()`、`referral()` 等 Tool 时
   - trace 中能看到 tool 名称、调用结果摘要、耗时、成功/失败状态

### 查询能力

5. **最小查询入口**
   - 至少存在一种方式可查看指定 session 的 trace 列表：
     - 调试 API，或
     - 后端脚本/命令

### 安全与脱敏

6. **Trace 不直接泄露过长敏感文本**
   - Tool 输入输出、消息内容在 trace 中经过必要截断或脱敏
   - 不会把完整敏感长文本原样无限存储到 trace
