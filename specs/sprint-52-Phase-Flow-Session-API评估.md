# Sprint 52 - Phase Flow Session API 评估

## 背景

Sprint 51 已新增可复用的 `Phase Flow Scenario Evaluator`，可以对预定义多轮场景输出结构化 PASS / FAIL 报告。

但它仍主要服务于测试层，尚未进入 session trace / API 读取链路。当前项目里：

- trace 已能记录 `phase_timeline`
- session API 已能读取 traces、timeline 和 analysis
- 但没有一个面向真实会话的 phase flow 评估载荷

这意味着 Evaluator 仍然缺少一个统一入口，去基于真实 session traces 读取阶段推进质量，而不是只在测试代码里手工比对。

## 目标

- 基于真实 session trace，输出会话级 phase flow 报告
- 为 API 层新增可读的 phase flow evaluation 载荷
- 让 Evaluator 可以直接读取真实会话的阶段推进概览和异常点

## 范围

- `trace_helpers`
  - 新增基于 trace timeline 的 phase flow report 构建函数
- API 层
  - 新增 session phase flow evaluation 读取接口
- 测试
  - helper 单测
  - API 单测

## 非目标

- 不在本轮自动判定咨询质量分数
- 不在本轮引入新的 OpenAI judge 调用
- 不在本轮做前端可视化

## 预期结果

- 存在会话级 phase flow report
- API 可直接返回该 report
- Evaluator 可以基于真实 traces 读取阶段推进摘要与潜在异常
