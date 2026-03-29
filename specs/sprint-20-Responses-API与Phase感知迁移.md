# Sprint 20 Spec — Responses API 与 Phase 感知迁移

## 目标

将心雀当前基于 Chat Completions 的单 LLM + Tool Use 对话主链路迁移到 Responses API，并引入 `phase-aware` 的消息状态管理，解决长流程中“中间更新被误当成最终答案”的潜在问题。

本 Sprint 的目标是完成运行时协议层迁移，而不是重新设计业务逻辑。迁移后，系统在保留现有工具集、安全层、画像、记忆与 trace 能力的前提下，具备更适合 GPT-5.4 长流程 agent 的对话协议基础。

## 背景

当前心雀后端的核心循环位于 [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)，通过：

- 手动拼接 `messages`
- 调用 `client.chat.completions.create(...)`
- 读取 `tool_calls`
- 将工具结果重新 append 到消息列表

这套方式在 MVP 阶段是可行的，但它有两个结构性问题：

1. 对长流程 agent 而言，协议语义过于扁平  
   现在所有 assistant 消息都被当作同一层消息处理，没有显式区分“工作中间态”和“最终回答”。

2. 无法自然承接 GPT-5.4 文档强调的 `phase-aware` 约束  
   GPT-5.4 文档建议在长流程和多工具场景中保留 `phase` 语义，避免中间 preamble、解释性更新或工作态输出在历史回放中劣化为最终答复。

因此，需要一个独立 Sprint，把调用层从 Chat Completions 迁移到 Responses API，并建立最小可用的 phase-aware 运行时协议。

## 本 Sprint 范围

### 1. 将核心调用从 Chat Completions 迁移到 Responses API

**做**：

- 将 [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 的核心 LLM 调用切换为 Responses API
- 保留现有工具循环能力：
  - 工具定义注册
  - 工具执行
  - 工具结果回传
  - 最终答复提取
- 保证迁移后外部 API 行为不变：
  - `/api/chat` 返回结构保持兼容
  - `card_data` 继续可用
  - trace 字段继续可记录

**不做**：

- 一并重写前端接口
- 一并更换业务工具协议
- 一次性接入全部 Responses 新能力

### 2. 建立 assistant `phase` 语义

**做**：

- 在运行时中显式区分至少三类 assistant 状态：
  - 中间工作态
  - 工具调用态
  - 最终回答态
- 若历史回放需要手动重建 assistant items，必须保留对应 `phase`
- 若使用 `previous_response_id`，则要明确采用该机制的边界与策略

**验收要点**：

- 中间说明不会在历史中被误当作最终答复
- 工具调用前后的 assistant 状态更清晰

### 3. 为 Responses API 迁移建立兼容的消息转换层

**做**：

- 增加从现有历史消息结构到 Responses 输入结构的转换层
- 增加从 Responses 输出结构回到当前系统内部格式的提取层
- 兼容：
  - 用户消息
  - assistant 最终回复
  - tool call / tool result
  - card_data 提取

**验收要点**：

- 迁移集中在协议转换层，不把业务逻辑散落到各处
- 当前 API、数据库和前端无需大幅跟着改

### 4. 为 trace / 观测补充 phase-aware 记录

**做**：

- 在 trace 中补充与 Responses API / phase 相关的关键字段
- 至少能区分：
  - 是否发生中间 assistant working phase
  - 是否发生工具调用 phase
  - 最终输出是否来自完整收束

**验收要点**：

- trace 能解释一轮对话内部的协议流
- 便于后续定位“中间态被误判”的问题

### 5. 补齐与 Responses 迁移相关的测试

**做**：

- 为协议转换层补测试
- 为 phase-aware 历史重放补测试
- 为工具循环在 Responses 下的正确性补测试
- 为 `/api/chat` 保持兼容补回归测试

**验收要点**：

- 至少有自动化测试证明迁移不是“改了接口但没验证”

## 不在范围

- 更高级语义 compaction
- 更复杂的长期状态图
- 外部向量数据库
- 新增业务工具
- 多模型路由

## 建议实现策略

1. **协议层先行**
   - 先写 Responses 输入输出适配层
   - 再迁移 `xinque.py` 主循环

2. **保留业务外观**
   - `/api/chat` 不改返回协议
   - 工具执行接口尽量不改

3. **phase-aware 最小化**
   - 先把 phase 做对，再考虑更多状态丰富度

## 验收标准

- 核心对话循环已经从 Chat Completions 迁移到 Responses API
- 系统能显式区分中间工作态、工具调用态和最终答复态
- 历史重放或延续请求时不会丢失 phase 语义
- `/api/chat` 行为对前端保持兼容
- trace 可观测到 phase-aware 协议流
- 至少存在自动化测试覆盖本次迁移

## 影响范围

- [`main.py`](/E:/AI_XinQue_Agent/app/backend/app/main.py)
- [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)
- trace / helpers 相关模块
- 与 Agent 回归相关的测试文件

## 风险与注意事项

- 不要在同一 Sprint 同时重构协议层和业务层
- 不要把 Responses API 迁移和长会话语义治理混在一起
- 要优先保证前端兼容和工具链稳定
- phase-aware 是协议问题，不是写几句 Prompt 就能替代
