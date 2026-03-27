# Sprint 02 Contract — 核心 Agent 与数据基础

## 成功标准

### 后端

1. **数据库初始化**
   - `cd app/backend && alembic upgrade head` 成功执行，生成 `data/xinque.db`
   - 数据库包含 users、sessions、messages 三张表

2. **API — 创建会话**
   - `POST /api/sessions` 传入 `{"client_id": "xxx"}` → 返回 `{"session_id": "...", "user_id": "..."}`
   - 相同 client_id 多次调用 → user_id 相同（复用用户）

3. **API — 对话**
   - `POST /api/chat` 传入 `{"session_id": "...", "client_id": "...", "message": "你好"}` → 返回 `{"reply": "...", "session_id": "..."}`
   - 不传 session_id → 自动创建新会话，返回 session_id
   - 回复内容体现心雀人设（自称"我"，温暖专业，询问称呼）

4. **会话持久化**
   - 发送 3 条消息后，重启后端服务
   - 用相同 session_id 发送第 4 条消息 → 回复能关联前 3 条的上下文

5. **心雀人设**
   - 首次对话时心雀主动自我介绍并询问用户称呼
   - 回复风格符合三层结构（共情 + 功能 + 推进）
   - 不做诊断、不推荐药物（安全红线体现在 System Prompt 中）

### 前端

6. **基础适配**
   - 页面加载后发送消息 → 正常收到心雀回复
   - 刷新页面后 → 对话历史保留（通过 session_id 恢复）

7. **新对话**
   - 点击"新对话"按钮 → 清空当前对话，开始新会话
   - 新会话中心雀重新自我介绍

### 集成

8. **端到端**
   - 完整流程：打开页面 → 发消息 → 收到心雀回复 → 多轮对话 → 刷新页面 → 对话恢复 → 点新对话 → 新会话开始
