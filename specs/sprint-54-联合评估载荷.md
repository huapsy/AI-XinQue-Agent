# Sprint 54 - 联合评估载荷

## 背景

Sprint 53 已让 session analysis 可以直接输出 phase 异常模式：

- `stuck_in_p2`
- `phase_regression`
- `unfinished_p4`

项目中也已有 `LLM-as-Judge` 评估链路，会输出：

- empathy
- safety
- stage_appropriateness
- intervention_quality
- alignment_sensitivity
- prompt_review

但这两条线目前仍是分开的：

- judge 结果只看对话文本
- phase anomalies 只看 trace 阶段流转

Evaluator 还缺一份联合载荷，把“文本质量判断”和“阶段推进风险”放到同一份结构里。

## 目标

- 新增联合评估载荷 helper
- 将 LLM judge 结果与 phase flow report / anomalies 合并
- 给 Evaluator 提供单一评估对象

## 范围

- `evaluation_helpers`
  - 新增联合评估 helper
- 测试
  - 新增 helper 单测
- harness 文档
  - `spec` / `contract` / `evaluation`

## 非目标

- 不新增新的 OpenAI judge 提示链路
- 不在本轮新增 API endpoint
- 不做前端展示

## 预期结果

- 存在统一的联合评估载荷
- Evaluator 能一次拿到 judge 分数、prompt_review、phase_flow、phase_anomalies
