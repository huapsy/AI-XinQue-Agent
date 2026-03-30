# Sprint 56 Contract

## 目标

把真实 `run_llm_judge` 接入 session 联合评估接口，使 `combined-evaluation` 返回真实 judge 结果和 phase 风险信号。

## 成功标准

1. `get_session_combined_evaluation` 调用真实 judge helper
   - 读取 session messages
   - 调用 `run_llm_judge`

2. 接口返回真实 judge 结构
   - `scores`
   - `prompt_review`
   - `summary`
   不再是占位空对象

3. 仍保留 phase 风险字段
   - `phase_flow`
   - `phase_anomalies`
   - `risk_flags`

4. 有 API 单测
   - 验证 helper 被调用
   - 验证返回结构包含真实 judge 内容

## 证据要求

- API 代码
- 单测结果

## 非验收项

- 不要求 judge 结果落库
