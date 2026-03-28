# Sprint 10 Spec — 情景记忆与 search_memory

## 目标

落地 `product-plan-v2` 中的 episodic memory 能力：把“值得记住的关键事件片段”从会话中提取出来，生成 embedding，并通过 `search_memory()` Tool 在后续会话中按需检索。

## 背景

Sprint 06 已经让心雀能够依赖会话摘要、作业和干预历史实现基础的跨会话连续性，但这仍然主要是“基于上次会话摘要”的连续性。`product-plan-v2` 第 8 节希望系统具备更细粒度的“情景记忆”能力，比如：

- 用户提到“妈妈上周住院”
- 用户提到“最近换了新领导”
- 用户提到“自己最怕在会上被点名”

这些内容未必都应该进入长期画像，也不一定只在“上次会话”里有价值。它们更适合沉淀为**可检索的关键事件片段**。

## 本 Sprint 范围

### 1. episodic_memories 表

**做**：
- Alembic 迁移新增 `episodic_memories` 表
- 字段建议：
  - `memory_id`
  - `user_id`
  - `session_id`
  - `content`
  - `topic`
  - `emotions`
  - `created_at`
  - `embedding`

**注意**：
- 开发阶段若 SQLite 不便直接存向量，可先存为 JSON / BLOB
- 后续迁移 PostgreSQL 时再切换到更合适的向量存储方案

### 2. 记忆提取策略

**做**：
- 设计一条“何时写入 episodic memory”的最小策略，避免什么都记
- 推荐只记录以下类型片段：
  - 重要人物与关系事件
  - 重大生活变化
  - 用户反复提到的困扰情境
  - 用户自己的关键表达/核心比喻
- 每轮对话结束后，由后端检查当前轮是否值得沉淀

**推荐实现方式**：
- 第一版不要让 LLM 每轮都额外生成复杂结构
- 可以先基于：
  - formulate 里的结构化内容
  - 简单规则 + 最后一轮用户消息
  - 或结束会话时批量提取 1-3 条关键片段

**不做**：
- 全量消息 embedding
- 自动总结成复杂事件图谱

### 3. embedding 生成与存储

**做**：
- 为 episodic memory 生成 embedding
- 建立最小可用的相似度检索流程
- 抽象 embedding 生成接口，避免后续切模型时改动过大

**不做**：
- 高性能 ANN 检索优化
- 多模型 embedding 对比实验

### 4. search_memory() Tool

**做**：
- 新增 `app/backend/app/agent/tools/search_memory.py`
- Tool 输入：
  - `query`
  - `top_k`
  - 可选 `topic`
- Tool 输出：
  - 最相关的 3-5 条 episodic memory
  - 含内容、话题、时间、情绪标签
- 在 system prompt 中明确：
  - 只有当用户提到旧话题、人物、场景，或需要回忆更早会话时才调用
  - 不要每轮都调用

### 5. recall_context 与 search_memory 分工

**做**：
- 明确：
  - `recall_context()` 用于加载稳定上下文：昵称、摘要、作业、最近干预
  - `search_memory()` 用于按需检索更早、更细粒度的关键事件
- 避免两者职责重叠

### 6. 验证与质量控制

**做**：
- 新增测试覆盖：
  - 记忆写入阈值不过宽
  - 相似 query 能检索到对应历史片段
  - 无关 query 不返回太多噪音
  - 同一事件不会被无限重复写入

## 用户可感知的变化

本 Sprint 完成后，用户会更明显感受到“心雀不只是记得上次摘要，而是真的记得一些重要事情”：

- “你上次提到妈妈住院，这件事最近怎么样了？”
- “之前你说每次周会前都会特别紧张，今天也有这种感觉吗？”

## 不在范围

- 完整画像趋势分析
- 可观测性 Trace
- 自动评估体系
- 管理后台
