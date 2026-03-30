# Sprint 51 Contract

## 目标

建立可复用的 `Phase Flow Scenario Evaluator`，让四阶段架构的多轮流转验证可以通过结构化场景报告复用，而不只依赖零散单测。

## 成功标准

1. 存在 phase flow scenario evaluator
   - 能运行一组多轮场景
   - 能收集每轮实际 `active_phase`
   - 能与预期 phase 序列对比

2. 输出结构化报告
   - 至少包含：
     - `passed`
     - `observed_phases`
     - `expected_phases`
     - `mismatches`

3. 有 PASS / FAIL 两类场景测试
   - PASS：`P1 -> P2 -> P3 -> P4 -> P1`
   - FAIL：至少一个 phase 偏离预期时报告 mismatch

4. harness 证据齐备
   - `spec`、`contract`、`evaluation` 三件套存在
   - 有定向测试结果

## 证据要求

- evaluator 模块代码
- PASS / FAIL 场景测试
- 结构化场景报告示例

## 非验收项

- 不要求接入真实 OpenAI API
- 不要求替代现有 LLM judge
