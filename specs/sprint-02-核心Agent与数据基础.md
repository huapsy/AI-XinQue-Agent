# Sprint 02 — 核心 Agent 与数据基础

## 目标

将 Sprint 01 的"Azure OpenAI API 代理"改造为 v2 架构下的**心雀核心 Agent**：具备完整人设、会话持久化、基础 Tool Use 循环。用户在浏览器中与心雀对话时，感受到的不再是通用 AI，而是一个温暖专业的心理咨询师。

## 背景

Sprint 01 已验收通过：前后端联通，能收发消息。但当前后端只是把用户消息直接转发给 Azure OpenAI，没有人设、没有会话管理、没有数据持久化。

v2 架构（见 `docs/design/product-plan-v2.md`）要求：
- 单一核心 LLM + Tool Use 自主推理循环
- System Prompt 注入心雀人设、安全红线、对话阶段指南
- 会话和消息持久化到数据库
- 为后续 Sprint 的 Tool（formulate、match_intervention 等）建立基础

## 本 Sprint 范围

### 1. 数据库基础

**做**：
- SQLAlchemy 模型定义：users、sessions、messages 三张核心表
- Alembic 初始化 + 初始迁移脚本
- SQLite 开发数据库（`app/backend/data/xinque.db`）

**不做**：
- user_profiles、case_formulations、interventions、episodic_memories 等表（后续 Sprint）
- PostgreSQL 生产配置

**表结构**：

```sql
users (
  user_id       TEXT PK (UUID)
  nickname      TEXT
  created_at    DATETIME
  last_seen_at  DATETIME
)

sessions (
  session_id    TEXT PK (UUID)
  user_id       TEXT FK → users
  started_at    DATETIME
  ended_at      DATETIME NULL
  summary       TEXT NULL
)

messages (
  message_id    TEXT PK (UUID)
  session_id    TEXT FK → sessions
  role          TEXT  -- 'user' | 'assistant'
  content       TEXT
  tool_calls    JSON NULL
  created_at    DATETIME
)
```

### 2. 心雀核心 Agent

**做**：
- `app/backend/app/agent/xinque.py` — 核心 Agent 入口
  - 接收用户消息 + session_id
  - 从数据库加载本次会话历史
  - 构建 LLM 输入（System Prompt + 对话历史 + 用户消息）
  - 调用 Azure OpenAI（支持 Tool Use 循环结构，本 Sprint 暂无实际 Tool）
  - 返回回复文本
  - 将用户消息和 AI 回复持久化到 messages 表

- `app/backend/app/agent/system_prompt.py` — System Prompt 构建
  - 注入心雀人设（第 2 节全部内容）
  - 注入安全红线（10 条）
  - 注入双维度响应模型摘要
  - 注入四阶段对话指南摘要
  - 本 Sprint 暂不注入 Tool 定义（无实际 Tool）

**不做**：
- Tool 实现（recall_context、formulate 等留到后续 Sprint）
- 输入/输出安全层（留到 Sprint 03）
- 对齐分数计算

### 3. 会话管理

**做**：
- 会话创建：首次对话时自动创建 user + session
- 会话恢复：基于 session_id 加载历史消息
- 简易用户识别：前端生成一个 client_id（UUID，存 localStorage），后端据此查找或创建 user

**不做**：
- 登录/认证系统
- 会话列表/历史对话查看
- 会话摘要生成

### 4. API 改造

**做**：
- 改造 `POST /api/chat`：
  - 请求体增加 `session_id`（可选）和 `client_id`
  - 首次请求不传 session_id → 后端创建新会话，返回 session_id
  - 后续请求传 session_id → 后端加载该会话的历史消息
  - 响应体增加 `session_id`
- 新增 `POST /api/sessions` — 创建新会话（用户点"新对话"时调用）

**不做**：
- WebSocket（暂时保持 HTTP 轮询）
- 流式响应（后续 Sprint）

### 5. 前端适配

**做**：
- ChatWindow 适配新的 API 格式（传 session_id、client_id）
- localStorage 存储 client_id（首次访问时生成）
- localStorage 存储当前 session_id
- "新对话"按钮（调用 `POST /api/sessions`，清空当前对话）

**不做**：
- 会话列表侧边栏
- 登录页面
- 样式优化

## 用户可感知的变化

Sprint 01：
> 用户："你好"
> AI："你好！有什么我可以帮你的吗？"（通用 AI 回复）

Sprint 02：
> 用户："你好"
> 心雀："你好，欢迎来到这里。我是心雀，一位心理咨询师。你可以和我聊聊你的感受、困扰，或者任何你想说的事。你希望我怎么称呼你呢？"（心雀人设）

- 刷新页面后对话不丢失（会话持久化）
- 点击"新对话"可以开始新的会话

## 不在范围

- 输入/输出安全层
- Tool 实现（formulate、match_intervention 等）
- 用户画像
- Skill 系统
- 对齐分数
- 情景记忆
- 可观测性 Trace
