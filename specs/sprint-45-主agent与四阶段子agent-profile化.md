# Sprint 45 - 主Agent与四阶段子Agent Profile化

## 背景

截至 Sprint 44，心雀已经具备：

- 单一核心 LLM + tool use 自主推理循环
- `active_skill` 锁定与跨轮持续推进
- 较完整的 system prompt / working contract / working context 分层

但四阶段（P1/P2/P3/P4）目前仍主要通过一个统一大 prompt 中的阶段纪律来约束，存在以下问题：

- 阶段行为混在单体 prompt 中，修改某一阶段时容易影响其他阶段
- 运行时无法明确表达“本轮主导的是哪个阶段 profile”
- trace / eval 难以直接观察当前轮次究竟在执行哪一阶段的行为约束

Limbic 的启发不是回到多 Agent 管道，而是为不同阶段提供更清晰的 prompt profile 与路由依据。

## 目标

- 在不引入真实多运行时 agent 的前提下，将心雀改造成：
  - 1 个主 agent orchestrator
  - 4 个阶段子 agent profile（P1/P2/P3/P4）
- 将当前单体 system prompt 拆成：
  - base contract
  - 当前 active phase 对应的单个 phase profile block
- 让运行时最小持久化状态中出现 `active_phase`

## 范围

- 设计并实现 4 个 phase profile：
  - `p1_listener`
  - `p2_explorer`
  - `p3_recommender`
  - `p4_interventor`
- `system_prompt.py` 支持按 `active_phase` 注入单个 phase profile
- `session_context` / `responses_contract` / trace 中可见 `active_phase`
- 保持现有 tool runtime 与安全守门逻辑不被破坏

## 非目标

- 不引入 5 个独立 LLM 会话或多 agent runtime handoff
- 不在本轮实现完整 phase router
- 不在本轮重写 skill 内容或前端交互
- 不在本轮定义完整 flow state variables 全集

## 预期结果

- 心雀对外仍只有一个主 agent 在说话
- 当前回合可以明确知道使用的是哪个 phase profile
- system prompt 不再同时注入四阶段全部细节，而是“基座 + 单个活动 phase block”
- `active_phase` 可在 runtime state 与 trace 中观察到

