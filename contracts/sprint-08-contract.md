# Sprint 08 Contract — 前端体验与历史对话

## 成功标准

### 后端 API

1. **会话列表 API**
   - GET /api/users/{client_id}/sessions 返回会话列表
   - 每条包含 session_id, started_at, summary(前30字), opening_mood_score
   - 按时间倒序

2. **情绪签到 API**
   - PATCH /api/sessions/{session_id}/mood 接受 mood_score(1-5)
   - 写入 sessions.opening_mood_score

### 前端

3. **会话列表**
   - 页面左侧显示会话列表
   - 列表显示时间和摘要预览
   - 点击切换查看不同会话

4. **历史只读**
   - 已结束的会话：消息正常显示，输入框禁用

5. **情绪签到**
   - 新会话时显示情绪选择
   - 选择后调用 mood API 并进入聊天

6. **端到端**
   - 完成一次对话 → 结束 → 在侧边栏看到该会话 → 点击查看历史消息
