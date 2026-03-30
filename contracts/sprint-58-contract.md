# Sprint 58 Contract

## 成功标准

1. `combined_evaluation_store` 提供读取全部已持久化联合评估结果的 helper
2. `build_admin_metrics_payload` 接受联合评估输入并输出 `combined_evaluation_summary`
3. `/api/admin/metrics` 返回 `combined_evaluation_summary`
4. 聚合字段至少包含：
   - `evaluated_session_count`
   - `coverage_rate`
   - `sessions_with_risk_flags`
   - `risk_flag_counts`
   - `average_scores`
5. 现有 admin metrics 核心字段保持可用：
   - `session_count`
   - `average_turns`
   - `intervention_completion_rate`
   - `safety_trigger_rate`
   - `tool_failure_rate`

## 证据要求

- 单元测试覆盖 store 列表读取
- 单元测试覆盖 admin metrics 聚合字段
- 单元测试覆盖 `/api/admin/metrics` 返回联合评估聚合摘要

## 测试约束

- 仅使用本地单元测试
- 不依赖真实 OpenAI 调用
- 不要求新增数据库迁移，本轮复用已存在 `combined_evaluations` 表
