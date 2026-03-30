# Sprint 44 - Skill执行锁定与主动流程控制

## 背景

截至 Sprint 43，系统已经支持在特定条件下直达某个 skill，但运行时仍缺少“skill 一旦开始执行，就应在后续多轮中沿该 skill 流程继续，直到完成、被用户明确拒绝、或被危机打断”的硬状态。

当前问题主要表现为：

- `load_skill()` 只把 protocol 暴露给模型，运行时没有 `active_skill` 概念
- skill 已启动后，后续轮次仍可能重新推荐、切换 skill，或脱离 skill 流程自由发挥
- 只有 prompt 提醒，没有多轮可见的执行锁定状态

这会导致干预流程不稳定，尤其在正向巩固、呼吸练习、认知重评等多步 skill 中，用户体验容易从“带我做完”退化成“推荐后就散了”。

## 目标

- 当某个 skill 已被 `load_skill()` 成功加载后，运行时建立 `active_skill`
- 在 `active_skill` 未完成前，默认继续沿该 skill 流程推进，而不是切换到新的 skill 或重新推荐
- 只有在以下情况才允许退出当前 skill：
  - 用户明确表示不想继续、要换方法、该练习不适合
  - 输入安全层检测到危机并接管
  - 已完成该 skill，并通过 `record_outcome()` 收口

## 范围

- 引入跨轮可见的最小 `active_skill` 状态
- 在 system prompt / working contract / layered context 中显式告知当前 skill 正在执行
- 在 runtime preflight 中阻止 skill 执行中的随意切换
- 允许在“强烈反对 / 要换方法 / 完成记录”这几个出口下释放锁定

## 非目标

- 不实现复杂的 step-level 状态机
- 不实现每个 skill 的自动步骤解析器
- 不把所有 skill 改造成结构化 workflow engine

## 预期结果

- 成功加载 skill 后，后续几轮拥有明确的 `active_skill`
- prompt / contract 能看到 `active_skill`，并被要求优先继续该 skill
- `match_intervention()` 与新的 `load_skill()` 在 `active_skill` 未释放前会被 guardrail 阻断
- 用户明确反对或要换方法时，锁定解除，系统可回到重新探索 / 推荐
