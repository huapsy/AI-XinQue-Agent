# Sprint 52 Contract

## 目标

把 phase flow evaluator 接到 session trace / API 层，使真实会话可以输出结构化 phase flow report。

## 成功标准

1. 存在 trace-based phase flow report helper
   - 输入 session traces
   - 输出至少包含：
     - `phase_sequence`
     - `phase_counts`
     - `transition_pairs`
     - `repeated_phase_runs`

2. API 层存在读取接口
   - 可基于 session traces 返回 phase flow report

3. 有 helper 与 API 测试
   - helper 单测
   - API 单测

4. harness 证据齐备
   - `spec`、`contract`、`evaluation`
   - 定向测试结果

## 证据要求

- helper 代码
- API 代码
- 测试结果

## 非验收项

- 不要求自动判定 PASS / FAIL 咨询质量
- 不要求前端消费该接口
