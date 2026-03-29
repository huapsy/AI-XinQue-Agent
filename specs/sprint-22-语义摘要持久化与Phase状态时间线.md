# Sprint 22 Spec — 语义摘要持久化与 Phase 状态时间线

## 目标

在 `Sprint 20` 完成 Responses API 迁移、`Sprint 21` 完成长会话分层上下文后，继续把这些“运行时状态”升级为“可恢复状态”。

本 Sprint 的目标是解决两个问题：

1. `semantic_summary` 与关键 `stable_state` 目前只存在于单轮运行时，跨轮与跨会话恢复能力仍然有限
2. Responses API 虽已接入 `previous_response_id`，但当前 trace 仍只记录 `final_phase + response_ids`，缺少更细粒度的 `phase/state timeline`

本 Sprint 不扩展新的业务能力，只补长会话状态的持久化与可恢复性。

## 背景

当前系统已经具备：

- Responses API 主链路
- `previous_response_id` 跨轮延续
- 长会话 `layered context`
- `semantic_summary`
- `current_focus / stable_state / retrieval_context / working_memory`

但这些能力还停留在“本轮生成、本轮消费”的阶段：

- `semantic_summary` 未单独入库
- `stable_state` 仍主要依赖实时回查 profile / formulation / intervention
- 没有结构化记录一轮对话内部经历了哪些 `phase`
- 出现长会话恢复、审查、回放或行为回归时，缺少稳定的状态依据

因此，需要一个独立 Sprint，把长会话状态从“运行时临时拼装”推进到“可存储、可恢复、可观察”。

## 本 Sprint 范围

### 1. 持久化语义摘要与关键长会话状态

**做**：

- 为当前会话增加长会话状态载体，至少能持久化：
  - 最新 `semantic_summary`
  - 最近一次 `current_focus`
  - 最近一次 `stable_state` 的关键快照
- 明确这些状态何时生成、何时更新、何时覆盖
- 保证状态恢复时，不必完全依赖重新扫描整段历史

**验收要点**：

- 长会话关键状态可以从数据库或持久层恢复
- 不再只依赖“重新拼 history”

### 2. 为 Responses 增加更细粒度的 phase/state timeline

**做**：

- 在 trace 或相邻持久化结构中，记录一轮对话内部的关键 phase/state 时间线
- 至少能区分：
  - working context 注入
  - tool call / tool result 往返
  - final answer
  - 是否发生 state refresh / summary refresh
- 保持与当前 trace 体系兼容

**验收要点**：

- 调试时能看出“一轮里状态是怎么推进的”
- 不再只有最终 phase 的单点信息

### 3. 建立长会话恢复优先级

**做**：

- 明确恢复长会话时的加载顺序：
  - 先恢复持久化状态
  - 再补工作记忆
  - 再按需触发 `recall_context` / `search_memory`
- 明确哪些状态可直接复用，哪些状态必须重新计算

**验收要点**：

- 恢复逻辑边界清晰
- 不会把所有状态都“每轮重算”

### 4. 让持久化状态与 `Sprint 21` 的 layered context 对接

**做**：

- 让 `session_context.py` 可以优先读取持久化摘要/状态
- 保持：
  - `current_focus` 仍以本轮用户输入为准
  - `semantic_summary` 可从持久化状态恢复并增量更新
  - `stable_state` 与 profile / formulation / intervention 不冲突

**验收要点**：

- `Sprint 21` 不是被推翻，而是被持久化增强

### 5. 补测试与评估场景

**做**：

- 增加状态持久化读写测试
- 增加 phase timeline 记录测试
- 增加长会话恢复测试
- 增加“无持久化状态时的回退路径”测试

**验收要点**：

- 状态持久化不是只靠人工看日志判断

## 不在范围

- 新的业务工具
- 新数据库引擎
- 新向量数据库
- 更高级的外部缓存层
- 更复杂的多 Agent 状态共享

## 建议实现策略

1. **先补状态载体，再补读写逻辑**
   - 先确定状态落在哪里
   - 再补写入和恢复

2. **优先复用现有 trace / session 结构**
   - 先最小侵入落地
   - 避免一开始就引入新的复杂状态系统

3. **区分“持久化背景”和“当前回合目标”**
   - `current_focus` 仍应以当前用户输入更新
   - 不要让持久化状态压过本轮意图

## 验收标准

- `semantic_summary` 与关键长会话状态已可持久化和恢复
- 一轮对话内部的 `phase/state timeline` 可被结构化记录
- 长会话恢复逻辑具备明确优先级，而不是全量重算
- `Sprint 21` 的 layered context 已与持久化状态打通
- 至少存在自动化测试或可重复评估覆盖本次改造

## 影响范围

- [`session_context.py`](/E:/AI_XinQue_Agent/app/backend/app/session_context.py)
- [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)
- [`main.py`](/E:/AI_XinQue_Agent/app/backend/app/main.py)
- trace / session / model 相关模块
- 长会话与 trace 相关测试

## 风险与注意事项

- 不要把当前目标也做成“僵硬持久化背景”
- 不要让 phase timeline 变成难以消费的大量噪声
- 不要在一个 Sprint 里同时做状态持久化和新的压缩算法试验
- 要优先保证恢复逻辑清晰，而不是追求状态字段一次到位
