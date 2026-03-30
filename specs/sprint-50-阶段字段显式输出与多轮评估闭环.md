# Sprint 50 - 阶段字段显式输出与多轮评估闭环

## 背景

Sprint 49 已把四阶段推进从“最小 phase router”提升为“最小 Flow Controller 闭环”：

- 存在单一 `Flow Controller` 控制平面
- `flow_state` 最小字段集已稳定
- `xinque.chat()` 已通过 controller 统一做阶段迁移
- `working_contract`、`session_context`、`trace` 已对齐同一套阶段语义

但当前实现仍有两个关键缺口：

1. assistant 端还没有稳定、显式地产出完整阶段字段  
   目前 `intent / explore / formulation_confirmed` 等字段仍主要依赖 runtime 与已有状态推导，而不是模型在每轮输出中明确回填。

2. evaluator 还缺少多轮对话脚本级验证  
   当前证据以单元测试和 trace 结构验证为主，尚未形成能覆盖 `P1 -> P2 -> P3 -> P4 -> P1` 连续流转的多轮脚本评估。

因此，Sprint 50 的目标不是再扩展新的业务能力，而是把 `06-Flow模块与阶段子Agent架构-v1.md` 中尚未落地的“阶段输出契约”和“评估闭环”继续往前推一轮。

## 目标

- 让主 Agent 每轮显式产出最小阶段字段对象，供 `Flow Controller` 消费
- 减少 `Flow Controller` 对隐式 runtime 推导的依赖，提高阶段推进的可解释性
- 建立多轮脚本级 evaluator 证据，验证核心阶段流转在真实对话样本中成立
- 为后续更强的 structured outputs / evaluator 自动化打基础

## 范围

- 后端运行时
  - 定义 assistant 最小阶段字段输出 schema
  - 在 Responses 链路中解析并消费该 schema
  - 将 `asking`、`chosen_intervention`、`intervention_complete` 的显式模型输出接入 `Flow Controller`
- Prompt / contract
  - system prompt 与 working contract 明确要求模型同时维护用户可见回复与阶段字段
  - 约束模型不要遗漏关键字段，字段冲突时由 runtime 纠偏
- 评估
  - 新增多轮对话脚本级测试或 evaluator fixtures
  - 至少覆盖：
    - `P1 -> P2`
    - `P2 -> P3`
    - `P3 -> P4`
    - `P4 -> P1`
    - 负向场景下不越级推进

## 非目标

- 不在本轮引入新的业务 Tool
- 不在本轮改前端交互
- 不在本轮把完整对话都强制改成单一 JSON-only 输出
- 不在本轮实现完整 Limbic 式“问题标签 + 用户回答”知识装配系统

## 预期结果

- assistant 每轮存在可解析的最小阶段字段输出
- `Flow Controller` 优先消费 assistant 显式字段，其次才回退到 runtime 推导
- `asking`、`chosen_intervention`、`intervention_complete` 不再只是弱隐式状态
- evaluator 能用多轮脚本独立验证阶段流转，不只看单轮 trace
- `06-Flow模块与阶段子Agent架构-v1.md` 中“阶段输出契约”和“结构化装配职责”的落地度进一步提高
