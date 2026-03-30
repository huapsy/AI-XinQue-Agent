# Sprint 53 - Phase 异常模式识别与 Analysis 聚合

## 背景

Sprint 52 已把 phase flow report 接到了 session trace / API 层，Evaluator 可以基于真实 traces 读取：

- `phase_sequence`
- `phase_counts`
- `transition_pairs`
- `repeated_phase_runs`

但当前 report 仍偏“原始统计”，对 Evaluator 来说还缺少更高层的异常模式识别。例如：

- 会话是否长期卡在 `P2`
- 是否出现 `P3 -> P2` 这类回退
- 是否进入 `P4` 却没有收口回到 `P1`

这些信号已经能从 phase sequence 推导出来，但目前没有被显式汇总进 `session analysis`。

## 目标

- 在 phase flow report 中新增异常模式识别
- 将这些异常模式并入现有 `session analysis` 聚合
- 让 Evaluator 能直接从 analysis 层看到 phase 风险信号

## 范围

- `trace_helpers`
  - 扩展 `build_phase_flow_report`
  - 扩展 `build_session_analysis_payload`
- 测试
  - helper 单测
  - analysis API 单测
- harness 文档
  - `spec` / `contract` / `evaluation`

## 非目标

- 不做自动咨询质量总分
- 不做前端告警 UI
- 不接入新的外部 judge

## 预期结果

- phase flow report 中可见异常模式
- session analysis 中可见异常摘要
- Evaluator 能直接读取异常信号，而不是自己手工分析 phase sequence
