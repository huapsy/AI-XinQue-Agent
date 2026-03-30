# Sprint 59 Eval

## 结果

PASS

## 已完成

- `/api/admin/metrics` 支持 `recent_sessions`
- `/api/admin/metrics` 支持 `since_days`
- 过滤范围内的 `session_count`、`average_turns`、`combined_evaluation_summary` 会同步收口

## 验证证据

```bash
cd app/backend
.\.venv\Scripts\python.exe -m unittest tests/test_admin_metrics.py
# Ran 5 tests ... OK

.\.venv\Scripts\python.exe -m unittest tests/test_admin_metrics.py tests/test_combined_evaluation_store.py tests/test_session_state_api.py tests/test_judge_evaluation.py tests/test_phase_flow_evaluator.py
# Ran 24 tests ... OK
```

## 备注

- 本轮采用内存过滤实现最小可用版本
- 后续若 admin metrics 数据量增大，可再把过滤逻辑下沉到查询层
