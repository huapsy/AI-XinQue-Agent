# Sprint 57 - 联合评估持久化

## 背景

Sprint 56 已让 `/api/sessions/{session_id}/combined-evaluation` 返回真实 judge 结果与 phase 风险联合结构。

但当前结果仍是临时计算：

- 不会落库
- 无法追踪最近一次评估时间
- 后续 admin / evaluator 聚合仍需重复触发评估计算

## 目标

- 为联合评估结果增加持久化能力
- 让 session 级联合评估可被读取和复用

## 范围

- 数据模型
  - 新增联合评估结果表
- 存储 helper
  - 读取 / 保存联合评估结果
- API
  - `combined-evaluation` 在生成后落库
  - 提供持久化结果读取能力
- 测试
  - store 单测
  - API 单测

## 非目标

- 不做评估历史版本化
- 不做前端展示
- 不做 admin 聚合面板

## 预期结果

- 联合评估结果不再只是临时计算
- session 可以读取最近一次持久化联合评估结果
