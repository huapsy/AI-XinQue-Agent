# 心雀 Agent Counsellor Harness Architecture v1

> 状态：v3 前置架构基线
>
> 目的：作为 `product-plan-v3` 的架构输入文档，定义心雀从当前 v2.1 方案升级为 `AI agent counsellor + harness` 系统时的目标结构、模块边界、运行机制与约束接口。

---

## 1. 背景与目标

心雀当前权威方案已经从“多 Agent 管道”演进到“单一核心 LLM + Tool Use”的智能体范式，但产品形态仍主要停留在通用心理支持智能体层。为了支撑 `product-plan-v3` 的重大升级，心雀需要进一步收口成一个更清晰的 `Counsellor agent + Harness` 系统，其中 Counsellor agent 的核心定义是：`LLM + Harness`。

该目标架构借鉴 Limbic 专利与逆向材料中体现出的几个关键思想：

- 将“自然语言生成”和“临床式理解/推荐”解耦
- 用模块化、可解释的理解层替代纯黑盒端到端对话
- 用显式的交互编排层驱动多阶段对话
- 在输入侧和输出侧设置独立安全闸门
- 用知识库、历史记录和结构化 profile 支撑长期关系与个性化干预

同时，心雀不直接复制 Limbic 的 CBT-only 方案，而是在以下方面保持产品差异：

- 心雀定位为 `non-diagnostic` 的心理支持与干预智能体，不做医学/心理诊断
- 心雀采用 `GPT-5.4 Responses API + tools + interventions` 作为核心运行时，而不是 prompt-only chatbot
- 心雀的干预范围是多流派的，包括 CBT、ACT、正念、积极心理学、情绪调节与危机协议
- 心雀保留现有 Harness Design 工作流，用于规格、契约、评估和持续升级

本文件回答以下问题：

1. 心雀 v3 的目标系统长什么样
2. 主要模块如何分层与协作
3. 对话如何从用户输入走到理解、推荐、干预与记录
4. GPT-5.4 Responses API 如何承载这一运行时
5. 现有心雀 v2.1 的代码与概念如何映射到新架构

---

## 2. 设计原则

### 2.1 单一主 Agent，模块化 Harness

心雀 v3 仍然坚持“单一主 Agent”范式。

- `GPT-5.4` 是唯一对用户负责的主决策与语言核心
- Counsellor agent 不是单独的 prompt，也不是多个子 agent 的集合，而是 `LLM + Harness` 的统一运行体
- Harness 提供工具、状态、记忆、安全、intervention 执行能力与观测能力
- 各模块不是彼此轮流接管用户的独立人格，而是主 Agent 可调用的运行时环境

更具体地说：

- `LLM` 负责理解用户、维持人格风格、生成自然语言、决定何时调用工具
- `Harness` 负责执行工具、维护状态、执行安全边界、记录 trace、提供可验证性
- 产品对外呈现的是一个统一的 `AI 心雀 Counsellor agent`，而不是“模型在说话，系统在旁边补丁式修正”

### 2.2 生成与理解解耦

主模型负责：

- 共情表达
- 多轮对话推进
- 工具调用决策
- 干预交付时的语言适配

机制化理解层负责：

- 结构化提取用户状态
- 维护可解释的 support formulation
- 提供推荐候选与干预匹配信号

### 2.3 非诊断性、支持性、可解释

心雀 v3 中所有“状态”都应优先表述为：

- support signal
- formulation hypothesis
- intervention fit signal
- user state summary

而不是诊断结论。

### 2.4 安全前置与后置双闸门

- 输入安全层：先判断是否存在危机、越界、攻击或不适合继续普通对话的输入
- 输出安全层：在对用户展示之前审查回复与卡片内容

### 2.5 结构化信息服务于长期关系

心雀 v3 不依赖单轮 prompt 内部“记住一切”，而是显式维护：

- 会话级结构化信息
- 跨会话 profile
- intervention 历史
- 技能执行结果
- 时间信息

### 2.6 Harness First

系统不围绕“写一个超级 prompt”构建，而围绕以下运行时构建：

- tool contracts
- structured outputs
- memory stores
- safety gates
- evaluation hooks
- observable traces

### 2.7 Prompt Governance First

心雀 v3 中所有运行时 prompt 设计都必须遵循显式的 prompt governance，而不是自由拼接长提示词。

- 所有系统 prompt、开发者 prompt、工具使用 prompt、结构化输出 prompt，默认参考 `docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md`
- prompt 必须显式定义输出合同、tool-use expectations、completion criteria、verification loop 和 instruction priority
- prompt 需要优先追求紧凑、结构化、可验证，而不是文学化或过度装饰
- 多阶段 prompt 必须明确每一阶段的目标、允许输出字段、切换条件和禁止行为

---

## 2A. Counsellor Agent Persona and Prompt Governance

### 2A.1 人格定位

AI 心雀在 v3 中不是一个中性的通用助手，而是一个具备稳定人格边界的 `Counsellor agent`。该人格应服务于以下目标：

- 稳定、可信、温和、专业的心理支持体验
- 长会话中的语气一致性与风格不漂移
- 在支持性、边界感和行动性之间取得平衡
- 与企业心理支持场景、非诊断性边界和危机协议保持一致

### 2A.2 人格设计来源

AI 心雀的人格设计默认参考：

- `docs/reference/gpt-5.4/prompt-personalities.md`

该参考文件用于指导以下人格维度的系统化设计：

- 语气与措辞
- 专业度与亲和度平衡
- 回应长度与结构习惯
- 纠偏方式与事实边界
- 在长任务、多工具、多阶段交互中的风格稳定性

心雀的人格应基于该参考做领域化定制，而不是直接复制其中某一种通用 personality。

### 2A.3 人格在系统中的注入位置

人格不应只存在于一个静态大 prompt 中，而应分层注入：

- 基础人格层：定义 AI 心雀是谁、如何说话、如何维持专业边界
- 阶段人格层：在 P1/P2/P3/P4 中对语气、推进方式和行动风格做轻量调整
- 产物人格层：在卡片、练习、总结、推荐解释中保持风格一致，但不破坏结构化输出

### 2A.4 人格的约束边界

人格只能影响“怎么表达”，不能覆盖以下高优先级约束：

- 安全规则
- 非诊断性产品边界
- 结构化输出合同
- tool 调用约束
- completion / verification 要求

也就是说，人格是运行时的行为风格控制层，不是可以覆盖系统规则的最高指令层。

### 2A.5 对 v3 的要求

`product-plan-v3` 需要进一步定义：

- AI 心雀的人格目标描述
- 基础人格指令块
- 阶段人格修饰块
- 人格与安全、格式、工具合同的优先级关系
- 人格 drift 的评估方法

---

## 3. 总体架构总览

### 3.1 分层视图

```text
XinQue Agent Counsellor System
├─ Channel / Experience Layer
│  ├─ Web Chat UI
│  ├─ Cards UI
│  ├─ Voice I/O (optional)
│  └─ Session UX State
├─ Input / Output Layer
│  ├─ Input Adapter
│  ├─ ASR Adapter (optional)
│  ├─ Response Renderer
│  └─ TTS Adapter (optional)
├─ Safety Layer
│  ├─ SubjectSafetyModule
│  ├─ OutputSafetyModule
│  └─ Crisis Routing / Escalation
├─ Interaction Orchestration Layer
│  ├─ InteractionModule
│  ├─ FlowModule
│  ├─ PromptGenerationModule
│  │  ├─ FirstPromptGenerator
│  │  ├─ SecondPromptGenerator
│  │  ├─ ThirdPromptGenerator
│  │  └─ FourthPromptGenerator
│  └─ Responses Runtime Controller
├─ Clinical Reasoning Layer
│  ├─ FirstModule
│  │  ├─ SubjectUnderstandingModule
│  │  ├─ SubjectRecommendationModule
│  │  ├─ RecommenderModule
│  │  └─ KnowledgeBank / HistoryModule
│  └─ Formulation / Alignment / Profile Tools
├─ Intervention Layer
│  ├─ Intervention Registry
│  ├─ Intervention Loader
│  ├─ Card Renderer
│  └─ Outcome Recorder
├─ Memory & Data Layer
│  ├─ Session Memory
│  ├─ Profile Store
│  ├─ Episodic Memory
│  ├─ Semantic Memory / Knowledge Bank
│  └─ Intervention History Store
└─ Harness / Operations Layer
   ├─ Tool Runtime
   ├─ Trace / Observation
   ├─ Evaluation Hooks
   ├─ Audit Log
   └─ Config / Policy / Guardrails
```

### 3.2 总体工作流

```text
User Input
  ↓
Input Adapter
  ↓
SubjectSafetyModule
  ↓
InteractionModule
  ├─ PromptGenerationModule
  ├─ GPT-5.4 Responses API Runtime
  └─ FlowModule
         ↓
Structured Information / Routing Signals
         ↓
FirstModule
  ├─ SubjectUnderstandingModule
  ├─ RecommenderModule
  └─ KnowledgeBank
         ↓
Recommended Intervention / Context
         ↓
InteractionModule
  ├─ motivate choice
  └─ deliver intervention
         ↓
OutputSafetyModule
         ↓
Renderer / UI / Card
         ↓
User Output
```

---

## 4. 端到端主流程

### 4.1 标准主流程

```text
1. 用户输入一条消息
2. 输入安全层判断是否需要危机或规则流接管
3. InteractionModule 启动或继续当前会话状态
4. FirstPromptGenerator 生成开放式支持 prompt
5. 主 Agent 通过 Responses API 产生回复和路由字段
6. FlowModule 解析 Explore / Intent / Finished 等字段
7. 若需深入探索，则进入 SecondPromptGenerator
8. InteractionModule 收集 thought / feeling / situation 等结构化材料
9. SubjectUnderstandingModule 从结构化材料中生成 subject profile
10. RecommenderModule 基于 profile、历史和目标生成 intervention 候选
11. ThirdPromptGenerator 解释 intervention 并引导用户选择
12. FourthPromptGenerator 交付选中的 intervention
13. 结果写入 profile、memory、history 和 trace
14. 输出安全层审查后再展示给用户
```

### 4.2 Responses API 运行循环

```text
User message
  ↓
Build Responses input
  ↓
GPT-5.4 Responses API
  ├─ emits assistant content
  ├─ emits structured output fields
  └─ emits tool calls when needed
         ↓
Tool Runtime executes tools
  ├─ recall_context
  ├─ get_system_time
  ├─ formulate
  ├─ match_intervention
  ├─ load_intervention
  ├─ render_card
  ├─ record_outcome
  └─ profile / memory tools
         ↓
Tool results returned to Responses API
         ↓
Model continues reasoning
         ↓
Final assistant response
         ↓
Output safety + render
```

### 4.3 多阶段交互状态机

```text
Open Conversation
  ├─ if Intent=True → Deliver Intervention
  ├─ if Explore=True → Structured Exploration
  └─ if Finished=True → End / idle

Structured Exploration
  ├─ collect labelled user inputs
  ├─ build formulation summary
  ├─ if user confirms → Understanding + Recommendation
  └─ if not enough evidence → continue exploration

Understanding + Recommendation
  ├─ infer user state signals
  ├─ rank candidate interventions
  └─ hand off to motivate-choice stage

Motivate Choice
  ├─ explain recommended interventions
  ├─ user selects one
  └─ hand off to delivery stage

Deliver Intervention
  ├─ execute selected intervention
  ├─ collect response / completion
  └─ persist outcomes
```

---

## 5. 核心模块架构

## 5.1 Channel / Experience Layer

### 5.1.1 Web Chat UI

职责：

- 承载对话界面、消息列表、输入框、卡片展示
- 向后端发送用户消息
- 渲染回复、结构化卡片、技能练习 UI

输入：

- 用户文本输入
- 可选语音输入

输出：

- 规范化消息事件
- UI 上下文事件（点击 intervention、完成练习、反馈）

### 5.1.2 Cards UI

职责：

- 渲染技能卡片、练习表单、结构化作业
- 采集干预执行结果和简短反馈

---

## 5.2 Input / Output Layer

### 5.2.1 Input Adapter

职责：

- 将 Web / mobile / voice 输入规范化为统一消息对象
- 附带用户 ID、会话 ID、时间戳、输入模式

建议输入对象：

```json
{
  "user_id": "string",
  "session_id": "string",
  "message_id": "string",
  "timestamp": "ISO-8601",
  "content_type": "text|voice|event",
  "text": "string",
  "client_context": {}
}
```

### 5.2.2 Response Renderer

职责：

- 将 assistant 文本、卡片、路由结果转换为前端可渲染对象
- 隔离模型输出与 UI 协议

---

## 5.3 Safety Layer

### 5.3.1 SubjectSafetyModule

职责：

- 在正常对话开始前审查用户输入
- 检测危机、自伤、自杀、规则流接管条件

机制：

- trigger words / phrases / regex
- 可选二分类风险模型
- 命中后阻断普通对话，转危机模板或人工升级

输出：

- `safety_status`
- `block_normal_flow`
- `crisis_route`

### 5.3.2 OutputSafetyModule

职责：

- 在 assistant 输出展示给用户前进行最终审查

机制：

- 规则匹配
- 输出风险分类
- 必要时重新生成、切规则流、人工升级

输出：

- `allow_output`
- `blocked_response`
- `fallback_route`

#### 重新生成回路（参见 Appendix A.8）

当 OutputSafetyModule 检测到不安全输出时，不应仅 block——应支持 retry：

```text
LLM response
  ↓
OutputSafetyModule.check()
  ├─ pass → render to user
  └─ fail
      ├─ if retries < MAX_OUTPUT_SAFETY_RETRIES (建议 = 2)
      │   ├─ inject [SAFETY_FEEDBACK] 指出拦截原因
      │   ├─ re-call Responses API
      │   └─ → OutputSafetyModule.check() (loop)
      └─ if retries exhausted
          ├─ use fallback safe response template
          ├─ log to audit
          └─ optionally flag for human review
```

约束：

- 每次 retry 在 prompt 中追加 `[SAFETY_FEEDBACK]` 明确上一次被拦截的原因
- retry 不重置 tool call history，仅重新生成最后一轮 assistant output
- `MAX_OUTPUT_SAFETY_RETRIES` 应可配置（环境变量或 policy config）

### 5.3.3 Crisis Routing / Escalation

职责：

- 输出危机热线、紧急支持、真人转介
- 维护危机协议模板与升级路径

---

## 5.4 Interaction Orchestration Layer

### 5.4.1 InteractionModule

职责：

- 负责整段用户交互主流程
- 驱动多阶段 prompt、LLM 调用、结构化收集和干预交付

输入：

- 用户输入
- 对话历史
- KnowledgeBank 上下文
- FirstModule 输出

输出：

- 用户可见回复
- structured information
- 下一阶段状态

### 5.4.2 FlowModule

职责：

- 解析 LLM 输出中的 flags 与结构化字段
- 决定下一阶段路由
- 根据 `[Asking]` 为用户回复打标签
- 维护 `SessionFlowState`（全局会话流状态，等价于 Limbic `PatentGraphState`）

关键字段：

- `Intent`
- `Explore`
- `Finished`
- `Asking`
- `chosen_intervention`

输出：

- `next_stage`
- `labelled_user_input`
- `parsed_output`

#### SessionFlowState（全局会话流状态）

FlowModule 维护以下统一 state，所有模块通过该 state 读写会话级流转信息（参见 Appendix A.3）：

```json
{
  "session_id": "string",
  "user_id": "string",
  "conversation_phase": "P1 | P2 | P3 | P4",
  "transition_reason": "string — 最近一次阶段切换原因",
  "last_prompt_generator": "First | Second | Third | Fourth",
  "formulation_readiness": "exploring | sufficient | solid",
  "structured_items": [
    { "asking_label": "feeling", "user_utterance": "我觉得很焦虑", "turn_index": 3 }
  ],
  "subject_profile": "dict — formulate 最新返回的 formulation 快照",
  "recommendation": "dict — match_intervention 最新返回的 plans",
  "chosen_intervention": "string | null",
  "intervention_status": "not_started | in_progress | completed | declined",
  "flow_next_node": "string — 下一步应进入的模块/阶段",
  "needs_more_exploration": false,
  "explore_more_targets": [],
  "direct_intent_resolved": false,
  "timestamp": "ISO-8601 — 最后更新时间"
}
```

约束：

- 该 state 由 Harness 维护，不由模型直接修改
- 工具调用的返回值和 FlowModule 的路由结果写入此 state
- `formulate` 返回后自动更新 `formulation_readiness`、`subject_profile`
- `match_intervention` 返回后自动更新 `recommendation`、`needs_more_exploration`、`explore_more_targets`
- 阶段切换时记录 `transition_reason`

### 5.4.3 PromptGenerationModule

职责：

- 选择 prompt 模板
- 将用户输入、profile、推荐、历史、知识库内容组装为 `system prompt` 或更一般的 `system input`

输入：

- 当前用户输入
- 对话历史
- subject profile
- recommendation
- knowledge context
- format instructions

输出：

- `system_prompt`
- `expected_output_schema`

### 5.4.4 FirstPromptGenerator

职责：

- 开放式支持对话
- 检测是否值得深入探索或直接进入 intervention

关键输出期望：

- `response`
- `Intent`
- `Explore`
- `Finished`

### 5.4.5 SecondPromptGenerator

职责：

- 进行 thoughts / feelings / situations 结构化探索
- 生成 formulation summary

关键输出期望：

- `response`
- `Asking`
- `Finished`

### 5.4.6 ThirdPromptGenerator

职责：

- 向用户解释 intervention 候选
- 让用户进行协作式选择

关键输出期望：

- `response`
- `finished`
- `chosen_intervention`

### 5.4.7 FourthPromptGenerator

职责：

- 执行被选中的 intervention

关键输出期望：

- `response`
- completion signal，例如 `INTERVENTION_OVER`

### 5.4.8 Responses Runtime Controller

职责：

- 负责和 GPT-5.4 Responses API 交互
- 维护 tool loop
- 注入 system prompt、conversation items、tool results
- 处理 structured outputs 与 tool calls

---

## 5.5 Clinical Reasoning Layer

### 5.5.1 FirstModule

这是心雀 v3 中借鉴 Limbic 最深、但要重新产品化定义的模块。

职责：

- 接收原始输入或结构化信息
- 生成 support formulation 与 user state summary
- 推荐当前最适合的 intervention 候选

它由 3 个核心子模块组成：

- `SubjectUnderstandingModule`
- `RecommenderModule`
- `KnowledgeBank`

### 5.5.2 SubjectUnderstandingModule

职责：

- 从用户输入或结构化信息中提取用户状态信号
- 形成可解释的 `subject profile information`

建议的状态类型：

- 情绪强度与情绪走向
- 反刍 / 灾难化 / 全或无思维等认知信号
- 行为收缩 / 回避 / 激活信号
- 关系主题 / 工作主题 / 自我价值主题
- 技能接受度与对齐状态

可包含的子模型：

```text
SubjectUnderstandingModule
├─ ThoughtDetectionModel
├─ DistortedThoughtDetectionModel
├─ SentimentAnalysisModel
├─ BehaviouralPatternDetectionModel
├─ CoreBeliefsModel
├─ TopicModel
└─ AlignmentStateEstimator
```

注意：

- 心雀 v3 中这些结果应表述为 `support signals` 和 `formulation hypotheses`
- 避免在产品层直接使用“诊断”叙事

### 5.5.3 SubjectRecommendationModule / RecommenderModule

职责：

- 接收 subject profile
- 结合历史、目标、用户特征与 intervention 记录
- 输出一个排序后的 intervention 候选集

推荐机制建议：

1. 先做 rule-based baseline
2. 后续升级到 learned policy

推荐优化目标：

- therapeutic alliance
- short-term user relief / stability
- information gain
- intervention adherence

### 5.5.4 KnowledgeBank / HistoryModule

职责：

- 存储 therapy knowledge、用户背景、历史 intervention、结构化对话记录
- 支持 retrieval augmentation
- 支持推荐过滤与可解释性

存储内容：

- 用户 profile
- intervention history
- session summaries
- frequent thoughts / feelings / patterns
- intervention 说明与 psychoeducation 文本

---

## 5.6 Intervention Layer

### 5.6.1 Intervention Registry

职责：

- 注册所有可执行 intervention 包
- 维护 intervention metadata、适用场景、约束条件、输入输出接口

### 5.6.2 Intervention Loader

职责：

- 根据 recommendation 或用户选择加载 intervention
- 提供 intervention.md / manifest / card schema

### 5.6.3 Card Renderer

职责：

- 将 intervention 或 exercise 渲染成卡片、步骤、表单或互动组件

### 5.6.4 Outcome Recorder

职责：

- 记录 intervention 是否执行
- 收集即时反馈
- 更新 profile 和记忆

---

## 5.7 Memory & Data Layer

### 5.7.1 Session Memory

保存当前会话上下文，包括：

- 最近对话轮次
- 当前阶段
- 当前 exploration 进展
- 当前 intervention 候选

### 5.7.2 Profile Store

保存跨会话稳定信息，包括：

- 昵称
- therapy goals
- 长期主题
- 高层支持性 profile

### 5.7.3 Episodic Memory

保存可回忆事件：

- 某次工作冲突
- 某次 panic episode
- 某次 intervention completion

### 5.7.4 Semantic Memory / Knowledge Bank

保存用户长期模式与平台知识。

### 5.7.5 Intervention History Store

保存：

- 推荐过什么
- 做过什么
- 哪些有帮助
- 哪些被拒绝
- 时间信息

---

## 5.8 Harness / Operations Layer

### 5.8.1 Tool Runtime

建议将现有工具收口为以下运行时能力：

- `recall_context`
- `get_system_time`
- `formulate`
- `match_intervention`
- `resolve_direct_intent` — P1 直接意图快捷路径（见 Appendix A.6）
- `load_intervention`
- `render_card`
- `record_outcome`
- `profile_read`
- `profile_write`
- `memory_search`
- `memory_store`
- `handoff_to_human`

其中 `get_system_time` 用于在运行时显式获取系统当前时间，并为对话轮次、记忆记录、intervention 执行结果与关键事件打上统一时间戳，帮助主 Agent 正确理解用户历史轨迹、事件先后关系与时间跨度。

建议的标准 tool schema 草案如下：

```json
{
  "name": "get_system_time",
  "description": "Get the current system time and timezone-aware timestamp for conversation state, memory records, and audit events.",
  "parameters": {
    "type": "object",
    "properties": {
      "purpose": {
        "type": "string",
        "description": "Why the current time is needed, such as timestamping a message, recording an intervention outcome, or grounding a historical summary."
      }
    },
    "required": [],
    "additionalProperties": false
  }
}
```

建议的返回对象草案如下：

```json
{
  "iso_timestamp": "2026-03-30T10:15:20+08:00",
  "utc_timestamp": "2026-03-30T02:15:20Z",
  "timezone": "Asia/Shanghai",
  "unix_ms": 1774836920000,
  "local_date": "2026-03-30",
  "local_time": "10:15:20",
  "weekday": "Monday"
}
```

约束建议：

- 该 tool 为只读工具，不写库、不触发外部副作用
- 需要记录时间的关键动作优先调用该 tool，而不是由模型自行生成时间文本
- 若会话跨时区或未来需要多地区部署，应以 `iso_timestamp + timezone + utc_timestamp` 作为最小返回集合
- 任何写入 memory、profile、intervention history、audit log 的记录，都应优先复用最近一次 `get_system_time` 的结果，而不是重复生成不一致时间戳

---

#### `formulate` — P2 渐进式个案概念化

**定位**：P2 探索阶段的核心工具。在探索过程中，每识别到有临床意义的新信息时由主 Agent 调用。工具内部将增量观察合并到当前会话的个案概念化（support formulation），并自动计算 readiness 与缺失维度。

**调用时机**：

- 用户披露了情绪、认知模式、行为模式或问题情境等有临床意义的新信息时
- 用户仅回复"嗯""好的"等低信息量内容时**不调用**

**Tool schema 草案**：

```json
{
  "name": "formulate",
  "description": "P2 探索阶段核心工具。每识别到有临床意义的新信息时调用，传入增量观察，工具内部合并到当前 formulation。返回完整 formulation 与 readiness 状态。readiness 为 sufficient 或 solid 时可进入 P3。",
  "parameters": {
    "type": "object",
    "properties": {
      "emotions": {
        "type": "array",
        "description": "本轮识别到的情绪",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string", "description": "情绪名称，如焦虑、无力感、愤怒" },
            "intensity": { "type": "string", "description": "强度：mild / moderate / severe" },
            "trigger": { "type": "string", "description": "触发情境" }
          },
          "required": ["name"],
          "additionalProperties": false
        }
      },
      "cognitions": {
        "type": "array",
        "description": "本轮识别到的认知模式 / 自动化思维",
        "items": {
          "type": "object",
          "properties": {
            "content": { "type": "string", "description": "思维内容，如 '我永远做不完'" },
            "type": { "type": "string", "description": "认知扭曲类型：catastrophizing / dichotomous / negative_filtering / fortune_telling / mind_reading / personalising" }
          },
          "required": ["content"],
          "additionalProperties": false
        }
      },
      "behaviors": {
        "type": "object",
        "description": "本轮识别到的行为模式",
        "properties": {
          "maladaptive": { "type": "array", "items": { "type": "string" }, "description": "非适应性行为" },
          "adaptive": { "type": "array", "items": { "type": "string" }, "description": "适应性行为" }
        },
        "additionalProperties": false
      },
      "context": {
        "type": "object",
        "description": "问题情境信息",
        "properties": {
          "domain": { "type": "string", "description": "领域：workplace / family / relationship / health / education / other" },
          "duration": { "type": "string", "description": "持续时间" },
          "precipitant": { "type": "string", "description": "诱因 / 触发事件" },
          "generalization": { "type": "string", "description": "泛化情况" }
        },
        "additionalProperties": false
      },
      "alliance_signal": {
        "type": "string",
        "description": "本轮对齐信号：aligned / confusion / disagreement / dissatisfaction / distrust / refusal / uncertainty"
      },
      "primary_issue": {
        "type": "string",
        "description": "核心问题描述（当主 Agent 能概括时填写）"
      },
      "structured_items": {
        "type": "array",
        "description": "本轮收集到的结构化信息对。保留用户原始表述与标签，用于审计和后续子模型处理。参见 Appendix A.4。",
        "items": {
          "type": "object",
          "properties": {
            "asking_label": { "type": "string", "description": "标签：situation / feeling / thought / behavior / other / formulation" },
            "user_utterance": { "type": "string", "description": "用户原始表述" }
          },
          "required": ["asking_label", "user_utterance"],
          "additionalProperties": false
        }
      }
    },
    "required": [],
    "additionalProperties": false
  }
}
```

**返回对象草案**：

```json
{
  "status": "ok",
  "schema": "formulation_v1",
  "formulation": {
    "readiness": "exploring | sufficient | solid",
    "primary_issue": "string | null",
    "mechanism": "string | null — 自动生成的维持机制假设，如 '诱因 → 认知模式 → 情绪 → 行为 → 强化循环'",
    "emotions": [
      { "name": "焦虑", "intensity": "moderate", "trigger": "项目截止日", "detection_source": "llm_extraction | classifier | rule" }
    ],
    "cognitive_patterns": [
      { "content": "我永远做不完", "type": "catastrophizing", "detection_source": "llm_extraction | classifier | rule" }
    ],
    "behavioral_patterns": {
      "maladaptive": ["回避任务", "熬夜拖延"],
      "adaptive": ["和朋友聊天"]
    },
    "context": {
      "domain": "workplace",
      "duration": "三周",
      "precipitant": "岗位调整",
      "generalization": "开始影响睡眠"
    },
    "severity": "string | null",
    "alliance_quality": "aligned | confusion | …",
    "missing": ["行为模式待探索", "问题领域待明确"]
  }
}
```

**readiness 计算规则**：

| readiness | 条件 |
|-----------|------|
| `exploring` | 情绪、认知、行为、核心问题中有缺失 |
| `sufficient` | 情绪 + 认知 + 行为 + 核心问题全部存在 |
| `solid` | sufficient + 维持机制已生成 + missing 为空 |

**约束建议**：

- formulation 的所有结论性表述在产品层应显示为 **support signal / formulation hypothesis**，不得使用医学诊断表述
- 增量合并：同一会话内多次调用时，工具内部自动合并情绪、认知、行为列表（去重），情境字段新值覆盖旧值
- primary_issue 更新后同步 patch 到 UserProfile.clinical_profile
- `structured_items` 累积保存至 `SessionFlowState`（见 §5.4.2 和 Appendix A.3），为审计与子模型预留输入
- `detection_source` 初期全部为 `llm_extraction`，后续插入独立子模型时切换为 `classifier` 或 `rule`

---

#### `match_intervention` — P3 干预方案匹配

**定位**：当 `formulate` 的 readiness 达到 `sufficient` 或 `solid` 时，由主 Agent 调用。基于当前 formulation、用户画像和历史干预记录，从 Skill 库中匹配并排序 1–2 个最合适的干预方案候选。

**调用时机**：

- formulation readiness 为 `sufficient` 或 `solid` 时
- 若 readiness 仍为 `exploring`，**Harness preflight 将拦截调用**并要求继续探索
- 若近 48 小时内有尚未收口的 intervention，preflight 优先要求 follow-up

**Tool schema 草案**：

```json
{
  "name": "match_intervention",
  "description": "当 formulation readiness 为 sufficient 或 solid 时调用。基于当前个案概念化、用户画像和历史干预记录，匹配 1–2 个最合适的干预方案。返回方案列表，每个包含 skill_name、rationale、user_friendly_intro 和时间 / 冷却元数据，供主 Agent 向用户自然介绍。",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": [],
    "additionalProperties": false
  }
}
```

**返回对象草案**：

```json
{
  "plans": [
    {
      "skill_name": "cognitive_restructuring",
      "display_name": "认知重构",
      "match_strength": "high | medium | low",
      "rationale": "用户存在 catastrophizing + dichotomous 认知扭曲，认知重构直接针对思维模式",
      "approach": "dialogue | card | dialogue+card",
      "user_friendly_intro": "我们一起看看那些自动冒出来的想法，检验一下它们是不是完全符合事实",
      "estimated_duration": "5-10 分钟",
      "estimated_turns": 6,
      "cooldown_hours": 48,
      "follow_up_rules": ["24h 后询问是否在生活中尝试过", "下次会话开场时主动提及"],
      "completion_signals": ["用户完成替代想法", "用户表示有新认识"],
      "cooling_applied": false,
      "cooling_reasons": [],
      "continuity_reason": "direct_match"
    },
    {
      "skill_name": "breathing_478",
      "display_name": "4-7-8 呼吸法",
      "match_strength": "medium",
      "rationale": "用户焦虑程度较高，呼吸练习提供即时躯体放松，降低唤醒水平",
      "approach": "card",
      "user_friendly_intro": "一个简单的呼吸练习，只需要几分钟，帮你在压力大的时候让身体先放松下来",
      "estimated_duration": "3 分钟",
      "estimated_turns": 3,
      "cooldown_hours": 24,
      "follow_up_rules": [],
      "completion_signals": ["用户完成 3 轮呼吸", "用户反馈身体有放松"],
      "cooling_applied": true,
      "cooling_reasons": ["same_category_recent"],
      "continuity_reason": "alternative_due_to_recent_cooling"
    }
  ]
}
```

**匹配机制概述**：

| 步骤 | 说明 |
|------|------|
| 1. 加载 Skill registry | 读取所有已注册 skill 的 manifest 元数据 |
| 2. 禁忌排除 | 排除用户不喜欢的技术、排除当前 risk_level 下有禁忌的 skill |
| 3. 信号评分 | 根据 formulation 的认知扭曲类型、情绪关键词、行为特征、领域等做加权匹配 |
| 4. 用户偏好加分 | 对 preferred_techniques 类别额外加分 |
| 5. 新鲜度冷却 | 对近期做过 / 推荐过 / 反馈"没帮助"的 skill 降权 |
| 6. 排序取前 N | 按总分降序，取前 1–2 个候选 |
| 7. 构建输出 | 对每个入选 skill 生成 rationale、intro、冷却与连续性元数据 |

**冷却（cooling）规则**：

- 同名 skill 在 `cooldown_hours`（默认 48h）内做过：**−6 分**
- 同 category 在冷却窗口内做过：**−2 分**
- 用户反馈 `unhelpful` 的同名 skill：**再 −6 分**
- 用户反馈 `unhelpful` 的同 category skill：**再 −8 分**

**约束建议**：

- 该工具**不接受**模型侧传参（`parameters` 为空对象）；所有匹配输入均来自 Harness 侧状态（formulation、profile、history）
- 返回的 `rationale` 供主 Agent 参考与转述，不直接展示给用户；`user_friendly_intro` 为面向用户的自然语言
- 若匹配结果为空或所有候选 `match_strength` 均为 `low`，返回回探信号（见 Appendix A.5）：`{ "plans": [], "needs_more_exploration": true, "explore_more_targets": [...], "message": "..." }`
- 该信号应被 Harness 写入 `SessionFlowState.needs_more_exploration` 和 `explore_more_targets`，由 FlowModule 路由回 P2
- Harness preflight 在 readiness 不满足时返回 `{ "status": "blocked", "reason": "formulation_not_ready", "missing": [...] }`

### 5.8.2 Trace / Observation

记录：

- 输入与输出
- tool calls
- route transitions
- selected interventions
- blocked safety events
- profile updates

### 5.8.3 Evaluation Hooks

为 Evaluator 和未来自动评估准备：

- structured conversation logs
- intervention success signals
- safety incident labels
- alliance / adherence proxies

### 5.8.4 Audit Log

用于解释：

- 为什么进入某阶段
- 为什么推荐某 intervention
- 哪个安全模块阻断了输出

---

## 6. 对话阶段与运行状态机

## 6.1 四阶段运行轮廓

心雀 v3 保留并强化现有四阶段，但将其从“概念性阶段”升级为“运行时 profile + prompt + tool strategy”三位一体。

| 阶段 | 目标 | 主体机制 | 主要输出 |
|---|---|---|---|
| P1 共情倾听 | 建立关系、承接情绪、判断是否深入 | FirstPromptGenerator + open conversation | 支持性回复、Explore/Intent |
| P2 探索与概念化 | 结构化理解问题与形成 formulation | SecondPromptGenerator + structured exploration + formulate tool | structured information、subject profile |
| P3 推荐与激发 | 解释候选 intervention，促成选择 | Recommender + ThirdPromptGenerator | intervention shortlist、user choice |
| P4 干预执行 | 实际开展 intervention | FourthPromptGenerator + load_intervention + render_card + record_outcome | intervention dialogue、outcome |

## 6.2 阶段切换逻辑

- `P1 -> P2`：用户披露值得深入探索的心理问题（`explore=true`）
- `P1 -> P4`：用户明确要求做某个 intervention（`intent=true`，通过 `resolve_direct_intent` tool 匹配，见 Appendix A.6）
- `P2 -> P3`：structured information 足够形成 profile 与 recommendation（`formulation_readiness ≥ sufficient`）
- `P2 -> P2`：证据不足，继续探索（`needs_more_exploration=true`，由 RecommenderModule 触发回路）
- `P3 -> P4`：用户选择 intervention（`chosen_intervention` 非空）
- `P3 -> P2`：推荐结果置信度不足（`match_strength` 全部为 `low`），回退继续探索
- `P4 -> P1/P2`：干预结束后回到支持或继续探索（`intervention_over=true`）

---

## 7. GPT-5.4 Responses API 映射

## 7.1 核心原则

心雀 v3 的主运行时以 `GPT-5.4 Responses API` 为核心，而不是 Chat Completions 风格的“单次 prompt -> 单次回复”。

原因：

- 原生支持 tool loop
- 更适合长程 agent runtime
- 更适合结构化输出和多阶段控制

## 7.1.1 Prompt 设计依据

心雀 v3 中所有基于 `GPT-5.4 Responses API` 的 prompt 设计，默认以 `docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md` 为依据。

这意味着运行时 prompt 应至少满足以下要求：

- 输出紧凑且结构化
- 显式声明输出合同
- 明确 follow-through policy
- 明确 instruction priority
- 明确 tool persistence 与 dependency checks
- 明确 completeness contract
- 在高影响动作前有 verification loop

这些约束应被视为 Counsellor agent 的核心运行时规范，而不是可选优化项。

## 7.2 Responses Runtime 结构

建议后端抽象如下：

```text
ResponsesRuntime
├─ build_system_input()
├─ build_tools_schema()
├─ call_responses_api()
├─ parse_structured_output()
├─ execute_tool_calls()
├─ append_observations()
└─ finalize_user_response()
```

## 7.3 每轮调用建议输入

每轮调用建议包含：

- `system_instructions`
- `conversation_items`
- `memory/context blocks`
- `tool schemas`
- `response format / structured output schema`
- `safety / style guardrails`

## 7.4 结构化输出建议

在不同阶段定义不同 schema，例如：

### P1 schema

```json
{
  "response": "string",        // content_field — 展示给用户
  "explore": true,             // routing_field — FlowModule 依据
  "intent": false,             // routing_field — FlowModule 依据
  "finished": false            // routing_field — FlowModule 依据
}
```

FlowModule 路由规则：`intent=true` → P4（direct intent，见 Appendix A.6）；`explore=true` → P2；`finished=true` → END / idle。

### P2 schema

```json
{
  "response": "string",                                        // content_field
  "asking": "thought|feeling|situation|other|formulation",     // routing_field — FlowModule 用于标签化
  "finished": false                                            // routing_field
}
```

FlowModule 路由规则：`asking` 非空 + `finished=false` → 继续 P2；`asking=formulation` + `finished=true` → Understanding + Recommendation。

### P3 schema

```json
{
  "response": "string",                   // content_field
  "finished": false,                      // routing_field
  "chosen_intervention": "string|null"    // routing_field — 用户选择结果
}
```

FlowModule 路由规则：`chosen_intervention` 非空 + `finished=true` → P4；`finished=false` → 继续 P3。

### P4 schema

```json
{
  "response": "string",                   // content_field
  "intervention_over": false,             // routing_field — 干预完成信号
  "outcome_signal": "string|null"         // content_field — 可选结果描述
}
```

FlowModule 路由规则：`intervention_over=true` → 写入 outcome → 回到 P1/P2。

## 7.5 Tool 调用建议

建议用 Responses tool calling 将现有心雀能力显式化：

```text
P1
- recall_context
- resolve_direct_intent (当 intent=true 时，跳到 P4)

P2
- formulate
- profile_read
- memory_search

P3
- match_intervention
- load_intervention (metadata only)

P4
- load_intervention (含 knowledge_context，见 Appendix A.7)
- render_card
- record_outcome
- profile_write
- memory_store
```

## 7.6 非目标

- 不将 Responses API 当作“超级 prompt 包装器”
- 不把所有临床逻辑都塞进 system prompt
- 不让 model 在没有 harness 约束时直接承担全部安全与推荐职责

---

## 8. 记忆与数据层设计

## 8.1 记忆分层

```text
Memory Stack
├─ Working Memory
│  └─ current prompt window
├─ Session Memory
│  └─ current session state and short summaries
├─ Episodic Memory
│  └─ event-based retrieval across sessions
└─ Semantic Memory
   └─ stable profile, themes, preferences, goals
```

## 8.2 时间信息必须显式进入上下文

每条被写入记忆的重要记录都必须包含：

- 发生时间
- 记录时间
- 会话 ID
- 来源模块

否则模型容易误判新旧信息的重要性。

为降低模型对“当前时间”的猜测，时间相关上下文应优先通过 `get_system_time` tool 获取，而不是依赖 prompt 中静态写死的时间字符串。该 tool 的结果应可被写入：

- 当前会话轮次元数据
- session summaries
- episodic memory 事件记录
- intervention history
- 审计日志与 trace

## 8.3 建议保存的结构化对象

### 用户画像

```json
{
  "nickname": "string",
  "therapy_goals": ["string"],
  "stable_themes": ["string"],
  "preferred_interventions": ["string"],
  "sensitivity_notes": ["string"]
}
```

### 会话摘要

```json
{
  "session_id": "string",
  "summary": "string",
  "main_topics": ["string"],
  "detected_support_signals": ["string"],
  "recommended_interventions": ["string"],
  "completed_interventions": ["string"],
  "timestamp": "ISO-8601"
}
```

### intervention 结果

```json
{
  "intervention": "string",
  "status": "suggested|selected|started|completed|declined",
  "user_feedback": "string|null",
  "observed_effect": "string|null",
  "timestamp": "ISO-8601"
}
```

---

## 9. 安全与合规层

## 9.1 输入安全

- 危机词与短语检测
- prompt injection 与 jailbreak 基础拦截
- 明确不进入普通心理支持对话的场景转危机流

## 9.2 输出安全

- 危险建议拦截
- 非法诊断化表述拦截
- 违反产品红线的输出拦截

## 9.3 产品红线映射

心雀 v3 必须继续 enforce 以下边界：

- 不做诊断
- 不推荐药物
- 不提供自伤方法
- 不鼓励停药或放弃专业治疗
- 检测到自伤/自杀风险时必须提供危机资源与转介路径

## 9.4 审计要求

所有安全触发事件应写入审计日志：

- 触发时间
- 触发模块
- 规则或标签
- 是否阻断
- 是否升级

---

## 10. Harness 层设计

## 10.1 Harness 的定义

在心雀 v3 中，Harness 指的是：

- tool runtime
- memory runtime
- safety runtime
- observation runtime
- policy/config runtime

而不是某一个 prompt 或某一个 agent。

## 10.2 Harness 的职责边界

模型负责：

- 理解与表达
- 选择何时调用工具
- 组合对话策略

Harness 负责：

- 执行工具
- 维护状态
- enforce guardrails
- 记录 traces
- 提供可验证性

## 10.3 Harness 与 Meta-Harness 的关系

运行时 Harness 负责产品运行。  
Meta-Harness 负责产品开发与升级：

- `specs/`
- `contracts/`
- `evaluations/`

`product-plan-v3` 应建立在本架构文档之上，再通过 Meta-Harness 拆成可交付能力。

---

## 11. 与现有心雀 v2.1 的映射

## 11.1 现有目录映射

| 现有心雀模块 | v3 架构对应 | 说明 |
|---|---|---|
| `app/backend/app/agent/xinque.py` | `Responses Runtime Controller` | 主 Agent 运行入口应继续保留，但升级为更清晰的 Responses loop runtime |
| `system_prompt.py` | `PromptGenerationModule` 部分能力 | 从单体 prompt builder 演进为多阶段 prompt generation |
| `tools/recall_context.py` | `Tool Runtime / Memory Recall` | 保留并纳入标准工具集 |
| `tools/formulate.py` | `SubjectUnderstandingModule / Formulation Tool` | 扩充为结构化 formulation 生成能力 |
| `tools/match_intervention.py` | `RecommenderModule / SubjectRecommendation` | 升级为候选排序与过滤器 |
| `tools/intervention.py` | `Intervention Layer` | 拆分为 `load_intervention`、`render_card`、`record_outcome` 更清晰 |
| `tools/profile.py` | `Profile Store` | 作为长期用户画像接口保留 |
| `tools/memory.py` | `Episodic / Semantic Memory Runtime` | 保留并补强时间与来源字段 |
| `analysis/` | `Clinical Reasoning Layer` | 可承接 mechanistic / structured analysis |
| `safety/` | `Safety Layer` | 输入与输出安全显式分离 |
| `session/` | `Session Memory / Session State` | 显式支持多阶段状态机 |
| `intervention_loader/` | `Intervention Loader` | 直接纳入 v3 核心架构 |

## 11.2 现有四阶段模型映射

| v2.1 阶段 | v3 架构位置 |
|---|---|
| P1 共情倾听 | `FirstPromptGenerator + open conversation runtime` |
| P2 探索与概念化 | `SecondPromptGenerator + SubjectUnderstandingModule + formulate tool` |
| P3 推荐与激发 | `RecommenderModule + ThirdPromptGenerator` |
| P4 干预执行 | `FourthPromptGenerator + Intervention Layer + Outcome Recorder` |

---

## 12. 对 Limbic 风格架构的借鉴与差异

## 12.1 借鉴点

- 输入安全与输出安全分离
- InteractionModule + FlowModule + 多 PromptGenerator 的交互编排思路
- FirstModule 作为“理解 + 推荐”的组合层
- KnowledgeBank 作为检索和历史上下文中台
- 将结构化信息作为理解层输入，而不是完全依赖原始自由对话

## 12.2 心雀的差异化设计

- 心雀不使用“自动诊断/治疗”表述，而使用 `support formulation` 与 `intervention fit`
- 心雀以 `GPT-5.4 Responses API + tools + interventions` 为核心，不是 prompt-only chatbot
- 心雀的 intervention 是多流派的，而不是单一 CBT action map
- 心雀强调 Harness 与 Meta-Harness 的双层工程体系
- 心雀保留企业员工心理支持产品的隐私、审计与危机转介边界

## 12.3 专利风险规避原则

- 避免将系统整体定义为自动诊断系统
- 避免把 state 命名直接落为医学 diagnosis
- 避免在文档和实现上固定为 `CBT state -> fixed intervention` 的单一路径
- 强调 tool-based orchestration、intervention runtime、multi-paradigm intervention、non-diagnostic support positioning

---

## 13. 非目标与边界

以下内容不在本架构文档范围内：

- sprint 切分
- 实施排期
- 数据迁移细节
- UI 视觉规范
- 训练新模型的具体 MLOps pipeline

本架构也不等同于：

- 一个完全自治、无人监管的临床治疗系统
- 一个只靠 prompt 的心理聊天机器人
- 一个多独立 agent 轮流接管用户的复杂编排系统

---

## 14. 对 `product-plan-v3` 的约束接口

`product-plan-v3` 在撰写时应至少覆盖以下内容，并以本文件为架构基线：

1. 明确定义 v3 的产品目标与差异化定位
2. 指定 v3 首批上线的模块与非目标模块
3. 指定 Responses API 运行时约束与 tool contracts
4. 指定 memory schema 与 profile schema
5. 指定 safety policy、crisis routing 与 audit requirements
6. 指定 intervention manifest、selection logic 与 intervention taxonomy
7. 指定 evaluation 指标：alliance、adherence、safety、usefulness、completion
8. 指定从 v2.1 到 v3 的兼容与迁移边界

---

## 15. 总结

心雀 v3 的目标不是把现有聊天机器人“换个更强的 prompt”，而是构建一个真正的 `Counsellor agent + Harness` 系统，其中 Counsellor agent 的核心就是 `LLM + Harness`：

- 以 `GPT-5.4 Responses API` 为主智能体运行时
- 以 `InteractionModule + FlowModule + PromptGenerationModule` 承载多阶段交互编排
- 以 `SubjectUnderstandingModule + RecommenderModule + KnowledgeBank` 承载可解释的理解与推荐
- 以 `interventions + cards + outcome recording` 承载干预执行闭环
- 以 `input/output safety + audit + memory + evaluation` 承载产品级安全与可持续演进能力

这份文档定义的是心雀 v3 的长期架构骨架。后续 `product-plan-v3`、具体 specs、contracts 与 evaluations 都应在这一骨架上展开，而不是重新发明运行时模型。

---

## Appendix A. 基于 Limbic 逆向材料的交叉审核

> 审核依据：`docs/reference/Limbic/` 目录下全部 12 份逆向文件，包括 `LimbicAI-RE-all-modules*.md`、`LimbicAI-FLOW_STATE_VARIABLES.md` 和 `04-LimbicAI-Module-System.md`。
>
> 审核对象：本文件 v1 初稿（含 `get_system_time`、`formulate`、`match_intervention` 三份 tool schema 草案）。

### A.1 整体判断

本架构文档对 Limbic 的核心思路——生成与理解解耦、多阶段 prompt + flow routing、输入/输出安全分离、KnowledgeBank 作中台——已做到结构性借鉴并完成了产品差异化定义。以下按维度展开差距与修补建议。

### A.2 差距清单

| # | 维度 | 级别 | Limbic 做法 | 心雀现状 | 修补建议 |
|---|------|------|------------|---------|---------|
| 1 | 全局 Flow State 数据结构 | **缺失** | `PatentGraphState` 统一对象：`session_id`、`conversation_phase`、`structured_items`、`subject_profile`、`recommendation`、`chosen_intervention`、`flow_next_node`、`transition_reason`、`last_prompt_generator` 等 | §4.3 / §6 有概念状态机但无统一数据结构 | 定义 `SessionFlowState`（见 A.3） |
| 2 | `formulate` 结构化标签输入 | **弱** | SecondPromptGenerator 产生 `[Asking]` 字段，FlowModule 为用户回复打标签，形成 `structured_items: [{asking_label, user_answer}]`，再按标签分发给子模型 | `formulate` 直接接收模型已提取好的 emotions/cognitions/behaviors，无独立标签化步骤，不保存"用户原始回答 + 标签"对 | 在 `formulate` 参数中增加可选 `structured_items` 字段（见 A.4） |
| 3 | `match_intervention` 回探信号 | **缺失** | RecommenderModule 输出 `needs_more_exploration` + `explore_more_targets`，不硬推低置信度结果，loop back 到 SecondPromptGenerator 继续收集 | 空结果时只返回 `{ "plans": [], "message": "建议继续探索" }`，无显式回探信号和方向 | 返回对象增加 `needs_more_exploration` + `explore_more_targets`（见 A.5） |
| 4 | 匹配置信度 / 阈值空间 | **弱** | RecommenderModule 接收 state_probabilities（0–1 概率），用阈值过滤后排序，低于阈值全部进入 explore | 硬编码加减分（+10、+9...），只要 score > 0 即入选，无法表达"信号弱不应硬推" | 返回对象预留 `match_strength` 字段（见 A.5） |
| 5 | Direct Intent 快捷路径 | **文档有、schema 无** | FirstPromptGenerator 检测 `Intent=True` 后通过 `DIRECT_INTENT_NAME_MAP` 直接解析 intervention，跳过 P2/P3 到 P4 | §4.3 / §6.2 有 `P1→P4` 路径，但 tool schema 无支撑 | 增加 `resolve_direct_intent` tool 或在 `match_intervention` 中增加 `force_direct` 模式（见 A.6） |
| 6 | 理解层信号来源标注 | **弱** | 每个维度由独立子模型处理（ThoughtDetection、SentimentAnalysis、BehaviouralPatternDetection 等），有独立置信度 | 全部交给 GPT-5.4 一次性完成，无信号来源标注 | `formulate` 返回对象预留 `detection_source` 字段（见 A.4） |
| 7 | KnowledgeBank 检索注入 P3/P4 | **缺失** | KnowledgeBank 在不同阶段做相似性检索 top-N 并注入 prompt（P3 注入 psychoeducation 文本、P4 注入执行步骤） | §5.5.4 定义了 KB 存储内容，但 tool schema 和 prompt generation 流程中没有"检索→注入"机制 | `load_intervention` 返回对象应包含 `knowledge_context`（见 A.7） |
| 8 | 输出安全重新生成回路 | **弱** | OutputSafetyModule 可以修改 prompt 并重新生成，再走一轮检查 | §5.3.2 只提到"必要时重新生成"，无 retry 路径设计 | 增加 `output_safety_retry` 路径和最大重试次数（见 A.8） |
| 9 | Phase schema 路由字段标注 | **弱** | 四个 PromptGenerator 各自定义独立 schema，FlowModule 解析逻辑完全基于指定字段 | §7.4 有四组 schema 但未区分哪些字段是路由依据、哪些是内容 | 标注 `routing_fields` vs `content_fields`（见 A.9） |
| 10 | 冷却与连续性机制 | **正面差异** | Limbic 仅通过 history 做简单过滤，无量化降权 | 心雀有 cooldown_hours、cooling_reasons、continuity_reason | 保留，不需回退 |

### A.3 补充：SessionFlowState 数据结构

Limbic 的 `PatentGraphState` 是所有模块读写的全局会话状态。心雀 v3 应在 Harness 层维护等价的统一 flow state。

建议的数据结构：

```json
{
  "session_id": "string",
  "user_id": "string",
  "conversation_phase": "P1 | P2 | P3 | P4",
  "transition_reason": "string — 最近一次阶段切换原因",
  "last_prompt_generator": "First | Second | Third | Fourth",
  "formulation_readiness": "exploring | sufficient | solid",
  "structured_items": [
    { "asking_label": "feeling", "user_utterance": "我觉得很焦虑", "turn_index": 3 }
  ],
  "subject_profile": "dict — formulate 最新返回的 formulation 快照",
  "recommendation": "dict — match_intervention 最新返回的 plans",
  "chosen_intervention": "string | null",
  "intervention_status": "not_started | in_progress | completed | declined",
  "flow_next_node": "string — 下一步应进入的模块/阶段",
  "needs_more_exploration": false,
  "explore_more_targets": [],
  "direct_intent_resolved": false,
  "timestamp": "ISO-8601 — 最后更新时间"
}
```

该 state 由 Harness 维护，不由模型直接修改。工具调用的返回值和 FlowModule 的路由结果写入此 state。

### A.4 补充：`formulate` schema 增强

#### 新增参数：`structured_items`

```json
{
  "structured_items": {
    "type": "array",
    "description": "本轮收集到的结构化信息对。保留用户原始表述与标签，用于审计和后续子模型处理。",
    "items": {
      "type": "object",
      "properties": {
        "asking_label": { "type": "string", "description": "标签：situation / feeling / thought / behavior / other / formulation" },
        "user_utterance": { "type": "string", "description": "用户原始表述" }
      },
      "required": ["asking_label", "user_utterance"],
      "additionalProperties": false
    }
  }
}
```

#### 返回对象增强：`detection_source` 字段

在 `emotions`、`cognitive_patterns` 的每个条目中预留：

```json
{
  "name": "焦虑",
  "intensity": "moderate",
  "trigger": "项目截止日",
  "detection_source": "llm_extraction | classifier | rule"
}
```

初期全部为 `llm_extraction`，后续插入独立子模型时切换为 `classifier` 或 `rule`。

### A.5 补充：`match_intervention` 返回对象增强

#### 空结果时的回探信号

当匹配结果为空或所有候选的匹配强度低于阈值时，返回：

```json
{
  "plans": [],
  "needs_more_exploration": true,
  "explore_more_targets": ["行为模式", "认知扭曲类型"],
  "message": "当前 formulation 的行为与认知证据不足，建议继续探索"
}
```

该信号应被 Harness 写入 `SessionFlowState.needs_more_exploration` 和 `explore_more_targets`，由 FlowModule 路由回 P2。

#### 每个 plan 增加 `match_strength`

```json
{
  "skill_name": "cognitive_restructuring",
  "match_strength": "high | medium | low",
  "...": "其余字段不变"
}
```

`match_strength` 基于当前评分系统量化：

| 范围 | match_strength |
|------|---------------|
| score ≥ 15 | `high` |
| 8 ≤ score < 15 | `medium` |
| 0 < score < 8 | `low` |

当所有候选均为 `low` 时，即使有结果也应考虑触发 `needs_more_exploration`。

### A.6 补充：Direct Intent 快捷路径

Limbic 的 `DIRECT_INTENT_NAME_MAP` 允许 P1 阶段直接解析"我想做呼吸练习"→ `breathing_478`，跳过 P2/P3。

心雀 v3 建议两种实现方式（择一）：

**方案 A**：独立轻量 tool `resolve_direct_intent`

```json
{
  "name": "resolve_direct_intent",
  "description": "P1 阶段检测到用户直接请求某个 intervention 时调用。基于用户表述匹配 Skill 库，返回候选 intervention。若匹配成功，主 Agent 可跳过 P2/P3 直接进入 P4。",
  "parameters": {
    "type": "object",
    "properties": {
      "user_intent_text": { "type": "string", "description": "用户表达的意图文本" }
    },
    "required": ["user_intent_text"],
    "additionalProperties": false
  }
}
```

**方案 B**：在 `match_intervention` 中增加 `force_direct` 模式

```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "force_direct": {
        "type": "boolean",
        "description": "当用户在 P1 直接请求 intervention 时设为 true，绕过 readiness 检查"
      },
      "intent_text": {
        "type": "string",
        "description": "用户表达的意图文本（仅 force_direct=true 时使用）"
      }
    }
  }
}
```

建议 v3 初期采用方案 A（独立 tool），保持 `match_intervention` 的单一职责。

### A.7 补充：KnowledgeBank 检索注入 P3/P4

Limbic 在 P3 和 P4 prompt 中注入从 KnowledgeBank 检索到的 top-N 相关内容。心雀应在以下位置实现等价机制：

- `match_intervention` 返回的每个 plan 中增加可选字段 `psychoeducation_snippet`（从 skill manifest 或 KB 检索）
- `load_intervention`（P4 tool）的返回对象中增加 `knowledge_context` 字段：

```json
{
  "skill_name": "cognitive_restructuring",
  "steps": ["..."],
  "knowledge_context": {
    "psychoeducation": "认知重构是 CBT 的核心技术之一……",
    "relevant_examples": ["……"],
    "retrieval_source": "skill_manifest | knowledge_bank | both"
  }
}
```

该 `knowledge_context` 应被注入 FourthPromptGenerator 的 prompt 中，使主 Agent 在交付 intervention 时能引用权威内容而非自由编造。

### A.8 补充：输出安全重新生成回路

§5.3.2 OutputSafetyModule 应支持以下 retry 路径：

```text
LLM response
  ↓
OutputSafetyModule.check()
  ├─ pass → render to user
  └─ fail
      ├─ if retries < MAX_OUTPUT_SAFETY_RETRIES (建议 = 2)
      │   ├─ inject safety feedback into prompt
      │   ├─ re-call Responses API
      │   └─ → OutputSafetyModule.check() (loop)
      └─ if retries exhausted
          ├─ use fallback safe response template
          ├─ log to audit
          └─ optionally flag for human review
```

约束：

- 每次 retry 应在 prompt 中追加明确的 `[SAFETY_FEEDBACK]` 指出上一次回复被拦截的原因
- retry 不重置 tool call history，仅修改最后一轮 assistant output
- `MAX_OUTPUT_SAFETY_RETRIES` 应可配置（环境变量或 policy config）

### A.9 补充：Phase Schema 路由字段标注

§7.4 中每个 phase schema 应明确区分路由字段和内容字段：

#### P1 schema

```json
{
  "response": "string",        // content_field — 展示给用户
  "explore": true,             // routing_field — FlowModule 依据
  "intent": false,             // routing_field — FlowModule 依据
  "finished": false            // routing_field — FlowModule 依据
}
```

FlowModule 路由规则：`intent=true` → P4（direct intent）；`explore=true` → P2；`finished=true` → END / idle。

#### P2 schema

```json
{
  "response": "string",                              // content_field
  "asking": "thought|feeling|situation|other|formulation",  // routing_field — FlowModule 用于标签化
  "finished": false                                   // routing_field
}
```

FlowModule 路由规则：`asking` 非空 + `finished=false` → 继续 P2；`asking=formulation` + `finished=true` → Understanding + Recommendation。

#### P3 schema

```json
{
  "response": "string",              // content_field
  "finished": false,                 // routing_field
  "chosen_intervention": "string|null"  // routing_field — 用户选择结果
}
```

FlowModule 路由规则：`chosen_intervention` 非空 + `finished=true` → P4；`finished=false` → 继续 P3。

#### P4 schema

```json
{
  "response": "string",              // content_field
  "intervention_over": false,        // routing_field — 干预完成信号
  "outcome_signal": "string|null"    // content_field — 可选结果描述
}
```

FlowModule 路由规则：`intervention_over=true` → 写入 outcome → 回到 P1/P2。

### A.10 正面差异（保留项）

以下心雀设计超出 Limbic 范围，属于正面差异化，不需要回退：

- **冷却与连续性机制**：cooldown_hours、cooling_reasons、continuity_reason 量化降权系统
- **多流派 intervention**：CBT + ACT + 正念 + 积极心理学 + 情绪调节 + 危机协议，而非 Limbic 的 CBT-only
- **Harness + Meta-Harness 双层工程体系**：specs / contracts / evaluations 的开发闭环
- **GPT-5.4 Responses API native tool loop**：而非 Limbic 的 prompt-only chatbot
- **非诊断性产品定位**：support formulation / intervention fit，而非医学诊断
- **企业级隐私与审计边界**：加密存储、对话内容不向企业暴露、审计日志
