# Sprint 59 - 联合评估聚合过滤视图

## 背景

`Sprint-58` 已让 `/api/admin/metrics` 返回 `combined_evaluation_summary`，但当前聚合结果只能看全量数据，无法回答“最近 7 天是否更容易卡在 P2”或“最近 20 个 session 的风险暴露情况如何”这类问题。

## 目标

给管理侧聚合读取补上最小过滤能力，让 evaluator / admin 可以基于时间窗口或最近会话范围查看联合评估摘要。

## 范围

- `/api/admin/metrics` 支持按最近 N 个 session 过滤
- `/api/admin/metrics` 支持按最近 N 天过滤
- 过滤后，`session_count`、`average_turns`、`combined_evaluation_summary` 等聚合值同步收口

## 非目标

- 不做复杂 SQL 优化
- 不做前端后台页面
- 不做分页
- 不做多维切片（部门、用户、skill、风险等级组合分析）

## 预期结果

- evaluator 可读取最近样本窗口的 phase 风险分布
- admin metrics 不再只能给出全量历史平均
