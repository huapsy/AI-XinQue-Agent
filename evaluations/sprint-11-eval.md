# Sprint 11 评估报告

**日期**: 2026-03-28
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | traces 表 | ✅ | 新增 `TraceRecord` 模型 + Alembic 迁移 |
| 2 | 正常对话 trace | ✅ | `POST /api/chat` 正常路径会写入包含 input/output/llm/tool_calls 的 trace |
| 3 | 危机绕过 trace | ✅ | 输入安全层阻断时也会写入 `llm_call.skipped=true` 的 trace |
| 4 | Tool 调用 trace | ✅ | `xinque.chat()` 已收集 tool 名称、成功状态、延迟、裁剪后的输入输出摘要 |
| 5 | 最小查询入口 | ✅ | 新增 `GET /api/sessions/{session_id}/traces` |
| 6 | Trace 不直接泄露过长敏感文本 | ✅ | `trace_helpers.redact_trace_text()` 会截断长文本，tool trace 不落完整长原文 |

## 本 Sprint 产出

### 后端新增
- `app/backend/app/trace_helpers.py` — trace 脱敏、tool trace 构建、trace 序列化 helper
- `app/backend/app/trace_sink.py` — trace sink 抽象，预留后续接 OpenTelemetry/其他后端
- `app/backend/alembic/versions/d93f5eab71a2_add_traces_table.py` — 新增 traces 表
- `app/backend/tests/test_trace_helpers.py`
- `app/backend/tests/test_trace_api.py`
- `app/backend/tests/test_trace_runtime.py`
- `app/backend/tests/test_trace_sink.py`
- `app/backend/tests/test_xinque_trace.py`

### 后端修改
- `app/backend/app/models/tables.py` — 新增 `TraceRecord`
- `app/backend/app/agent/xinque.py` — 汇总 LLM usage/latency，并在 tool 成功/失败两条路径都记录 trace entry
- `app/backend/app/main.py` — 正常/危机聊天路径写 trace，并补齐 input/output/llm 分段延迟与 token 统计

### 数据库迁移
- `d93f5eab71a2_add_traces_table.py`

### 测试
- `python -m unittest discover -s tests -p 'test_*.py'` → 28 tests passed
- `python -m py_compile app/trace_helpers.py app/trace_sink.py app/main.py app/agent/xinque.py app/models/tables.py` → passed

## 亮点

- trace 能力已覆盖输入安全层、LLM/tool 调用、输出安全层和总耗时这条主链路
- LLM trace 已记录模型名、请求次数、token usage 和累计 latency
- Tool 失败不再丢失，可直接在 trace 中看到 failure 状态与错误摘要
- tool trace 做了最小脱敏，不会直接把超长原文塞进 trace
- 查询接口已经具备，且已预留 trace sink 抽象，后续接 dashboard 或 OTel 不需要重写主流程

## 注意事项

- 当前 trace 仍是最小实现，尚未真正接入 OpenTelemetry / 可视化面板
- 目前记录的是诊断级信息，不包含 chain-of-thought
- token 统计依赖 Azure 响应 `usage` 字段；若上游返回为空，则会回退为 0
