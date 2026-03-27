# Sprint 01 — 项目骨架

## 需求

搭建前后端项目骨架，让一个最简单的对话能跑通：用户发消息 → 后端调 Azure OpenAI → 返回回复 → 前端显示。

## 后端

- FastAPI 项目初始化
- 一个 `POST /api/chat` 端点
  - 请求体：`{ "messages": [{"role": "user", "content": "..."}] }`
  - 调用 Azure OpenAI GPT（使用 openai Python SDK 的 Azure 配置）
  - 返回：`{ "reply": "..." }`
- CORS 配置（允许前端开发服务器访问）
- 环境变量管理（.env 文件存放 Azure OpenAI 的 endpoint、api_key、deployment_name）
- requirements.txt 包含：fastapi、uvicorn、openai、python-dotenv、pydantic

## 前端

- React + Vite + TypeScript 项目初始化
- 一个聊天页面：
  - 消息列表（用户消息靠右、AI 回复靠左）
  - 底部输入框 + 发送按钮
  - 发送后显示加载状态
- 前端维护消息历史数组，每次发送带上完整历史
- 调用后端 `POST /api/chat`
- 基本样式（不需要精美，能看清对话即可）

## 不做

- 数据库 / 数据持久化
- 用户认证
- 心雀人设 / 系统提示
- 安全层 / 对齐 / 多 Agent
- 生产部署配置
