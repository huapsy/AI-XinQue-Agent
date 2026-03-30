# Sprint 54 Contract

## 目标

在 `evaluation_helpers` 中建立联合评估载荷，使 LLM judge 结果与 phase flow 风险信号合并为同一份结构化输出。

## 成功标准

1. 存在联合评估 helper
   - 输入至少包括：
     - judge result
     - phase flow report
   - 输出至少包括：
     - `scores`
     - `prompt_review`
     - `summary`
     - `phase_flow`
     - `phase_anomalies`

2. 有衍生风险摘要
   - 至少能输出一组可读的风险标签或总结项

3. 有单元测试覆盖
   - 验证正常合并
   - 验证 anomalies 会进入联合载荷

4. harness 文档齐备
   - `spec`
   - `contract`
   - `evaluation`

## 证据要求

- helper 代码
- 单元测试结果
- 联合评估结构示例

## 非验收项

- 不要求新增 API
- 不要求替代现有 judge 输出
