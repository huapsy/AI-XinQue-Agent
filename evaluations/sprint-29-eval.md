# Sprint 29 评估报告

**日期**: 2026-03-29
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| 1 | Alembic 覆盖 `clinical_profile`、`session_states`、`session_state_history` 等最新 schema | ✅ | 已新增合并双头的 Alembic revision，并保留旧 SQLite 开发期兼容修复 |
| 2 | Tool schema 从源头统一为 Responses-native 格式 | ✅ | 所有 Tool 定义已移除嵌套 `function` 包装，Agent 主链路不再依赖运行时转换 |
| 3 | 前后端配置不再硬编码 localhost | ✅ | 后端 CORS 改为 `CORS_ORIGINS`，前端 API 改为 `VITE_API_BASE_URL` |
| 4 | 前端入口从单一 `#admin` 条件页升级为 `chat/history/admin` 三入口 | ✅ | 已新增 hash route 解析与 `HistoryPage` |
| 5 | 至少一类横切逻辑从 `main.py` / `xinque.py` 下沉 | ✅ | 已抽出 `chat_service.py` 与 `settings.py` |
| 6 | 验证通过 | ✅ | 后端全量 `100` 项通过，前端 `npm run build` 通过 |

## 本 Sprint 实际产出

### 后端修改
- `app/backend/app/chat_service.py`
- `app/backend/app/settings.py`
- `app/backend/app/schema_compat.py`
- `app/backend/app/main.py`
- `app/backend/app/agent/xinque.py`
- `app/backend/app/agent/tools/*.py`（tool schema 统一）
- `app/backend/alembic/versions/f4c8e2b7a9d1_merge_heads_add_session_state_tables.py`
- `app/backend/.env.example`

### 前端修改
- `app/frontend/src/config.ts`
- `app/frontend/src/navigation.ts`
- `app/frontend/src/sessionStorage.ts`
- `app/frontend/src/pages/ChatPage.tsx`
- `app/frontend/src/pages/HistoryPage.tsx`
- `app/frontend/src/pages/AdminPage.tsx`
- `app/frontend/src/App.tsx`
- `app/frontend/src/components/chat/ChatWindow.tsx`
- `app/frontend/src/components/admin/AdminDashboard.tsx`
- `app/frontend/.env.example`

### 测试修改
- `app/backend/tests/test_schema_compat.py`
- `app/backend/tests/test_tool_definitions.py`
- `app/backend/tests/test_settings.py`
- `app/backend/tests/test_xinque_trace.py`
- `app/backend/tests/test_response_state.py`

## 当前验证证据

- `& .\\app\\backend\\.venv\\Scripts\\python.exe -m unittest discover -s app\\backend\\tests -p "test_*.py"`
- `npm run build`

## 当前结论

`Sprint 29` 不是新增产品能力，而是一次结构收口：

- 数据库迁移链从“代码已演进但 Alembic 未跟上”收成了可追踪的 revision
- Agent / Tool 协议从兼容转换层回到源头统一
- 前后端本地硬编码配置改成环境化入口
- 前端从单一聊天页 + `#admin` 条件页，升级成 `chat/history/admin` 三入口壳层
- `main.py` 的会话装配职责开始下沉到独立服务模块

当前系统主链路未回归，且开发环境与后续生产化演进的边界更清楚了。
