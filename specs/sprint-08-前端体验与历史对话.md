# Sprint 08 Spec — 前端体验与历史对话

## 目标

让产品具备完整的用户体验：会话列表、历史查看、情绪签到。从"能聊"到"好用"。

## 功能点

### 1. 后端 API 扩展

- `GET /api/users/{client_id}/sessions` — 返回用户的所有会话列表（session_id, started_at, summary 预览, mood_score）
- `PATCH /api/sessions/{session_id}/mood` — 记录情绪签到分数（opening_mood_score）
- sessions 表已有 opening_mood_score/closing_mood_score 字段但未启用

### 2. 会话列表侧边栏

- 左侧显示历史会话列表
- 每条显示时间 + 摘要前 30 字
- 当前会话高亮
- 点击历史会话切换查看
- 响应式：窄屏时可折叠

### 3. 历史对话查看

- 点击历史会话 → 加载该会话的完整消息
- 已结束的会话为只读（输入框禁用，提示"此会话已结束"）
- 可以从历史查看中点击"新对话"回到活跃会话

### 4. 情绪签到

- 新会话首次打开时显示情绪选择界面
- 5 个选项：很差(1) / 不太好(2) / 一般(3) / 还不错(4) / 很好(5)
- 选择后记录到 session，然后进入聊天
- 情绪分数显示在会话列表中
