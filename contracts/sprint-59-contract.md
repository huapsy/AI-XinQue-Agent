# Sprint 59 Contract

## 成功标准

1. `/api/admin/metrics` 支持 `recent_sessions`
2. `/api/admin/metrics` 支持 `since_days`
3. 过滤后以下字段必须同步收口：
   - `session_count`
   - `average_turns`
   - `intervention_completion_rate`
   - `safety_trigger_rate`
   - `tool_failure_rate`
   - `combined_evaluation_summary`
4. `combined_evaluation_summary.average_scores` 和 `risk_flag_counts` 仅统计过滤范围内的 session

## 证据要求

- 单元测试覆盖 `recent_sessions`
- 单元测试覆盖 `since_days`
- 原有 admin metrics 聚合测试继续通过

## 测试约束

- 使用本地单元测试
- 不依赖真实 OpenAI 调用
- 允许先以内存过滤实现最小可用版本
