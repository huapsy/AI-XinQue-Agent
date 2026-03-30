# Sprint 53 Contract

## 目标

在 phase flow report 和 session analysis 中补齐阶段异常模式识别，使 Evaluator 能直接读取 phase 风险信号。

## 成功标准

1. phase flow report 新增异常模式识别
   - 至少覆盖：
     - `stuck_in_p2`
     - `phase_regression`
     - `unfinished_p4`

2. session analysis 已聚合异常模式
   - `analysis` 中可直接读取 phase 异常摘要或异常列表

3. 有测试覆盖
   - helper 单测
   - analysis 聚合/API 单测

4. harness 文档齐备
   - `spec`
   - `contract`
   - `evaluation`

## 证据要求

- 代码 diff
- 定向测试结果
- analysis 返回结构示例

## 非验收项

- 不要求所有异常都自动解释原因
- 不要求前端展示这些异常
