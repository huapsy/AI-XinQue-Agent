# Sprint 03 — 安全层与用户上下文

## 目标

给心雀加上两道安全防线（输入安全层 + 输出安全层），并实现第一个实际 Tool `recall_context()`，让心雀在回访用户时能关联历史。

## 背景

Sprint 02 心雀已有人设和会话持久化，但存在两个关键缺失：
1. **没有安全层**：用户发送危机信号（"我不想活了"）时，心雀全靠 System Prompt 中的红线约束 LLM 回应，没有硬编码兜底
2. **没有跨会话记忆**：回访用户时心雀不知道上次聊了什么、用户叫什么名字

## 本 Sprint 范围

### 1. 输入安全层（硬编码，LLM 之前执行）

**做**：
- `app/backend/app/safety/input_guard.py`
- 危机关键词检测：自杀、自伤、不想活、结束生命、割腕等关键词和模式匹配
- 检测到危机信号时，返回预设的危机响应（共情 + 安全确认 + 危机热线卡片），**绕过 LLM**
- 注入防护：检测常见的 prompt injection 模式（"忽略上面的指令"、"你现在是…"等），拒绝并回到正常对话

**不做**：
- 内容合规的完整检测（后续 Sprint）
- 基于 LLM 的二次危机检测（依赖 System Prompt，已在 Sprint 02 中配置）

### 2. 输出安全层（硬编码，LLM 之后执行）

**做**：
- `app/backend/app/safety/output_guard.py`
- 红线关键词过滤：检测 LLM 回复中是否包含诊断性表述（"你患有…"、"你得了…"）、药物推荐（"建议服用…"）、绝对化承诺（"保证…"、"一定会好"）
- 触发时替换为安全回复

**不做**：
- 完整的医学术语库匹配（后续迭代扩充）

### 3. 用户画像基础表

**做**：
- 新增 `user_profiles` 表（Alembic 迁移）
- 字段：user_id (FK)、nickname、session_count、risk_level、preferences (JSON)、updated_at
- 本 Sprint 只存 nickname 和 session_count，其他字段留空待后续填充

**不做**：
- clinical_profile、alliance、intervention_history 等复杂字段（后续 Sprint）

### 4. recall_context() Tool — P1 主力工具

**做**：
- `app/backend/app/agent/tools/recall_context.py`
- 功能：会话开始时一次性加载用户上下文
  - 用户基本信息（nickname、session_count）
  - 上次会话摘要（从 sessions.summary 读取，本 Sprint 手动或简单生成）
  - 用户偏好（如有）
- 在 Agent 的 Tool Use 循环中注册此 Tool
- LLM 可在首轮对话时调用，获取用户历史信息

**不做**：
- 情景记忆检索（search_memory，后续 Sprint）
- 未完成作业查询（需要 interventions 表，后续 Sprint）
- 复杂的会话摘要生成（本 Sprint 用简单方式：取上次会话最后几条消息拼接）

### 5. 会话结束时保存摘要

**做**：
- 会话结束逻辑：前端关闭页面 / 用户点"新对话"时，后端生成简单的会话摘要存入 sessions.summary
- 简单摘要策略：取本次会话的用户消息拼接为摘要（后续 Sprint 用 LLM 生成更好的摘要）

**不做**：
- LLM 生成的高质量摘要（后续 Sprint）

### 6. API 改造

**做**：
- 新增 `POST /api/sessions/{session_id}/end` — 结束会话，触发摘要生成
- 改造 chat 端点：在 LLM 调用前后分别执行输入/输出安全层

### 7. 前端适配

**做**：
- 点"新对话"时调用 end session API（保存当前会话摘要）
- 页面关闭时（beforeunload）尝试调用 end session API

**不做**：
- 会话列表侧边栏

## 用户可感知的变化

Sprint 02：
> 用户发送"我不想活了" → 心雀靠 LLM 自行判断，回复质量不可控

Sprint 03：
> 用户发送"我不想活了" → 硬编码安全层立即响应：共情 + 安全确认 + 危机热线卡片，绝不遗漏

Sprint 02：
> 用户第二次来对话 → 心雀不知道上次聊了什么

Sprint 03：
> 用户第二次来对话 → 心雀调用 recall_context() → "你好小明，上次我们聊了工作压力的问题，今天感觉怎么样？"

## 不在范围

- formulate() Tool（P2 探索用，Sprint 04）
- match_intervention() / load_skill()（P3/P4，后续 Sprint）
- 对齐分数计算
- 情景记忆 embedding
- 可观测性 Trace
