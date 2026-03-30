# Sprint 55 Contract

## 目标

把联合评估载荷暴露为 session 级 API，使 Evaluator 可通过统一入口读取 phase 风险与 judge 结构。

## 成功标准

1. 存在 session 联合评估读取接口
   - 返回结构至少包含：
     - `session_id`
     - `phase_flow`
     - `phase_anomalies`
     - `risk_flags`

2. 接口实现复用现有 helper
   - 不重复实现 phase anomalies 逻辑

3. 有 API 单测
   - 验证返回结构

4. harness 文档齐备
   - `spec`
   - `contract`
   - `evaluation`

## 证据要求

- API 代码
- 单测结果

## 非验收项

- 不要求实时调用 OpenAI judge
