# Sprint 56 - 真实 Judge 接入联合评估 API

## 背景

Sprint 55 已提供 `/api/sessions/{session_id}/combined-evaluation`，但当前返回的 judge 区域仍是占位空结构：

- `scores = {}`
- `prompt_review = {}`
- `summary = ""`

这意味着 API 虽然已经统一了 phase 风险读取口，但还没有把真实 LLM judge 结果接进来。

## 目标

- 在 session 联合评估接口中接入真实 `run_llm_judge`
- 让 combined evaluation API 同时返回：
  - 文本质量 judge 结果
  - phase flow / anomalies

## 范围

- `main.py`
  - 更新 `get_session_combined_evaluation`
- 测试
  - API 单测
- harness 文档
  - `spec` / `contract` / `evaluation`

## 非目标

- 不做 judge 结果持久化
- 不做前端消费
- 不重写 judge prompt

## 预期结果

- `combined-evaluation` 接口不再返回空 judge 结果
- Evaluator 能通过单一接口拿到真实 judge + phase risk 联合结构
