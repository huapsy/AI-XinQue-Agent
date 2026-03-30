# Sprint 58 - 联合评估聚合视图

## 背景

`Sprint-57` 已把单个 session 的 `combined evaluation` 持久化到数据库，但当前读取方式仍以单 session 为主。admin / evaluator 虽然可以查看单条会话的联合评估结果，却无法直接看到整体覆盖率、风险分布和 judge 评分均值。

## 目标

本轮把已持久化的联合评估结果接入管理侧聚合读取能力，形成最小可用的“联合评估聚合视图”。

## 范围

- 新增联合评估结果列表读取 helper
- 在 admin metrics 聚合中纳入 `combined evaluation`
- 输出联合评估覆盖率、风险标记计数、平均 judge 分等聚合字段
- 保持现有 `/api/admin/metrics` 兼容，新增字段而非改坏旧字段

## 非目标

- 不新增新的 LLM 评估逻辑
- 不改动单 session `combined-evaluation` 生成逻辑
- 不做前端后台页面
- 不做跨时间窗口、按用户群组、按技能类型的复杂切片分析

## 预期结果

- `/api/admin/metrics` 返回 `combined_evaluation_summary`
- summary 至少包含：
  - `evaluated_session_count`
  - `coverage_rate`
  - `sessions_with_risk_flags`
  - `risk_flag_counts`
  - `average_scores`
- Evaluator 可以直接基于该聚合结果判断当前版本整体 phase 风险暴露情况
