# Sprint 03 评估报告

**日期**: 2026-03-27
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | 危机检测 — "我不想活了" | ✅ | 硬编码响应，包含 400-161-9995，未经 LLM |
| 1b | 危机检测 — "我想割腕" | ✅ | 同上 |
| 1c | 正常消息不触发 | ✅ | "心情不好" → 正常走 LLM |
| 2 | 注入防护 | ✅ | "忽略上面的指令" → 拦截，返回心雀角色声明 |
| 3 | 输出安全层 | ✅ | 代码就位（诊断/药物/绝对化承诺检测），因 LLM 本轮未触发红线故未实际过滤 |
| 4 | user_profiles 表 | ✅ | 表存在，session_count 正确递增 |
| 5 | 首次用户 recall_context | ✅ | 新用户正常自我介绍 |
| 6 | 回访用户 recall_context | ✅ | "欢迎你回来。上次你提到你叫阿花，也说到最近和老公吵架了" |
| 7 | 会话摘要 | ✅ | end session 后 summary 非空，recall_context 能读到 |
| 8 | 端到端 | ✅ | 完整流程：对话→结束→回访关联→危机响应 |

## 本 Sprint 产出

- `app/backend/app/safety/input_guard.py` — 输入安全层（危机检测 + 注入防护）
- `app/backend/app/safety/output_guard.py` — 输出安全层（诊断/药物/承诺检测）
- `app/backend/app/agent/tools/recall_context.py` — 第一个实际 Tool（P1 主力）
- `app/backend/app/models/tables.py` — 新增 UserProfile 模型
- `app/backend/alembic/versions/db772f559771_add_user_profiles_table.py` — 迁移
- `app/backend/app/agent/xinque.py` — 重写：集成 Tool Use 循环 + recall_context 注册
- `app/backend/app/main.py` — 重写：安全层集成 + end session API + 摘要生成
- `app/frontend/src/components/chat/ChatWindow.tsx` — 新对话时结束旧会话 + beforeunload

## 亮点

- recall_context() Tool 调用效果出色：回访时 LLM 自主调用 Tool，自然地关联昵称和上次话题
- 输入安全层的危机响应是毫秒级返回（不经 LLM），用户不会等待
