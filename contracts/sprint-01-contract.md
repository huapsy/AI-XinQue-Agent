# Sprint 01 Contract — 项目骨架

## 成功标准

以下全部通过则 Sprint 01 完成：

### 后端

- [ ] `cd app/backend && pip install -r requirements.txt` 无报错
- [ ] `cd app/backend && uvicorn app.main:app --reload` 启动成功，终端显示 "Uvicorn running"
- [ ] `curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"你好"}]}'` 返回包含 `reply` 字段的 JSON
- [ ] .env.example 文件存在，列出所需的环境变量名

### 前端

- [ ] `cd app/frontend && npm install && npm run dev` 启动成功，无报错
- [ ] 浏览器打开 http://localhost:5173 能看到聊天界面
- [ ] 界面包含：消息列表区域、底部输入框、发送按钮
- [ ] 用户消息靠右显示，AI 回复靠左显示

### 联通

- [ ] 在前端输入框输入文字，点发送，能收到后端返回的 AI 回复并显示
- [ ] 发送过程中有加载状态提示
- [ ] 连续发送 3 条消息，每次都能正常收到回复（多轮对话）

## 不评估

- UI 美观度
- 回复质量（只要 Azure OpenAI 返回了内容即可）
- 错误处理的完整性
