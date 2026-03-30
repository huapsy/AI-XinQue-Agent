# Sprint 51 - Phase Flow 场景评估器

## 背景

Sprint 49-50 已完成：

- `Flow Controller` 控制平面
- assistant 显式阶段字段输出契约
- 多轮脚本级测试验证 `P1 -> P2 -> P3 -> P4 -> P1`

但目前多轮验证仍主要以测试文件存在，缺少一个可复用、可产出评估报告的 evaluator 场景层。也就是说：

- 已经能“写测试证明阶段能跑通”
- 但还不能“用统一 evaluator 方式复放场景并给出结构化结论”

这会让后续 phase flow 回归验证仍然依赖零散测试实现，不利于 harness 中 Evaluator 角色持续复用。

## 目标

- 建立一个可复用的 `Phase Flow Scenario Evaluator`
- 让 Evaluator 能以“场景定义 + 预期 phase 序列”的方式验证多轮阶段流转
- 输出结构化报告，而不只是依赖 unittest 断言

## 范围

- 后端 evaluator 层
  - 新增 phase flow scenario runner
  - 新增 phase flow report 结构
  - 支持对每轮实际 `active_phase`、预期 `active_phase` 做对比
- 测试
  - PASS 场景：`P1 -> P2 -> P3 -> P4 -> P1`
  - FAIL 场景：中途 phase 偏离预期
- harness 文档
  - 新增 `sprint-51` contract 与 evaluation

## 非目标

- 不在本轮引入真实浏览器 UI evaluator
- 不在本轮改写已有 LLM judge 评分体系
- 不在本轮接入外部评估平台

## 预期结果

- 项目中存在可复用的 phase flow evaluator 帮助函数或模块
- phase 场景验证不再只是散落在单测中
- Evaluator 可以拿一组 turns 和期望 phase 序列，生成 PASS / FAIL 报告
