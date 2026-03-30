# Sprint 55 - 联合评估 API

## 背景

Sprint 54 已建立联合评估载荷 helper，可以合并：

- LLM judge 结果
- phase flow report
- phase anomalies

但目前它仍停留在 helper 层，还没有 session 级读取入口。也就是说：

- Evaluator 在代码里能组合这些信息
- 但还不能通过统一 API 读取同一份联合评估载荷

## 目标

- 为联合评估载荷提供 session 级 API 读取入口
- 让 Evaluator 能通过统一 endpoint 获取 phase 风险与 judge 信息的聚合结构

## 范围

- `main.py`
  - 新增 session 联合评估读取接口
- 测试
  - API 单测
- harness 文档
  - `spec` / `contract` / `evaluation`

## 非目标

- 不在本轮引入新的真实 LLM judge 调用链
- 不在本轮做前端消费
- 不在本轮设计持久化 judge 结果表

## 预期结果

- session API 可返回联合评估结构
- Evaluator 有统一读取口
