# Sprint 01 Evaluation — 项目骨架

**日期**：2026-03-27
**结果**：✅ 通过

---

## 后端验证

| 标准 | 结果 | 备注 |
|------|------|------|
| `pip install -r requirements.txt` 无报错 | ✅ | uv pip install 完成 |
| `uvicorn app.main:app --reload` 启动成功 | ✅ | Uvicorn running on http://127.0.0.1:8000 |
| `POST /api/chat` 返回含 reply 的 JSON | ✅ | "你好" → "你好！有什么我可以帮你的吗？" |
| .env.example 存在 | ✅ | 含 4 个环境变量 |

## 前端验证

| 标准 | 结果 | 备注 |
|------|------|------|
| `npm install && npm run dev` 启动成功 | ✅ | Vite v8.0.3 |
| 浏览器能看到聊天界面 | ✅ | 需配置 host: '0.0.0.0' 解决 Windows IPv6 问题 |
| 界面含消息列表、输入框、发送按钮 | ✅ | ChatWindow.tsx |
| 用户消息靠右、AI 回复靠左 | ✅ | flexbox alignSelf 实现 |

## 联通验证

| 标准 | 结果 | 备注 |
|------|------|------|
| 前端发消息能收到 AI 回复 | ✅ | |
| 发送过程有加载状态 | ✅ | 显示"正在思考..." |
| 连续 3 条消息均正常回复 | ✅ | API 多轮测试通过 |

## 发现的问题（已修复）

1. **Vite IPv6 问题**：Windows 下 Vite 默认监听 IPv6，浏览器 localhost 解析到 IPv4 导致连接拒绝。已在 vite.config.ts 中配置 `host: '0.0.0.0'` 修复。
2. **端口冲突**：5173 被占用时自动切换到 5174，需要 CORS 同时允许两个端口。已修复。

## 结论

Sprint 01 全部验收标准通过。可进入 Sprint 02。
