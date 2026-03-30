下面继续整理 `InteractionModule`。

**InteractionModule**

它是系统里的**对话编排与用户交互总控层**。职责是：

- 接收用户输入
- 决定当前对话该处在哪个阶段
- 通过不同 `PromptGenerator` 驱动 `LanguageModel`
- 收集后续输入并形成 `structured information`
- 把解释、推荐、干预通过对话交付给用户

可以把它理解成：

- 上接用户输入
- 中间驱动 LLM 多阶段交互
- 下接 `FirstModule` 的理解与推荐

它比 `FlowModule` 更大，`FlowModule` 更像它内部的一个状态路由组件。

---

**1. 需要输入的信息 / 变量**

### A. 用户交互输入

1. `input_data`
   - 用户输入
   - 可以是 text / speech / numeric data
   - 但在例子里主要是 text

2. `dialogue_history`
   - 当前会话已有历史

3. `previous_system_outputs`
   - 先前系统生成的 utterances / responses

---

### B. 用户背景与上下文输入

4. `user_information`
   - 过往 intervention
   - clinical state summary
   - therapy goal
   - key life events
   - demographic / clinical data

5. `knowledge_bank_context`
   - 来自 `KnowledgeBank` 的上下文

6. `first_module_outputs`
   - 推荐 intervention
   - subject profile
   - explanation materials

---

### C. 模块内部控制输入

7. `flow_state`
   - 当前阶段 / 当前 prompt generator
   - 如：
     - open conversation
     - exploration
     - motivate intervention
     - deliver intervention

8. `flags_from_language_model`
   - `Intent`
   - `Explore`
   - `Finished`
   - `Asking`
   - `chosen_intervention`

9. `stored_text_templates`
   - 各 PromptGenerator 使用的模板集合

10. `format_instructions`
   - 对 LLM 输出的格式约束

---

### 可抽象变量

- `current_user_input`
- `conversation_history`
- `user_context`
- `knowledge_context`
- `first_module_context`
- `interaction_state`
- `routing_flags`
- `prompt_templates`

---

**2. 中间运行机制**

`InteractionModule` 的运行机制，本质上是一个**分阶段对话状态机**。

---

### 机制 A：初始接收输入并判断是否涉及 clinical state

专利中明确说：

1. `InteractionModule` 接收用户输入
2. 判断输入是否包含与用户 clinical state 有关的信息
3. 如果没有：
   - 继续开放式对话
4. 如果有：
   - 转入深入探索流程

这一步通常通过第一阶段 prompt + LLM flags 完成。

---

### 机制 B：通过 PromptGenerationModule + LanguageModel 实现多阶段交互

`InteractionModule` 内部包含：

- `PromptGenerationModule`
- `SecondModule(LanguageModel)`
- `FlowModule`

所以它并不是自己“说话”，而是：

1. 调相应的 PromptGenerator 生成 prompt
2. 把 prompt 送给 LanguageModel
3. 收到输出后交给 FlowModule 解析
4. 决定下个阶段

---

### 机制 C：阶段一，开放式对话

目的：
- 建立关系
- 让用户自然表达
- 探测：
  - `Explore`
  - `Intent`
  - `Finished`

结果：
- 若 `Explore=True` -> 进入阶段二
- 若 `Intent=True` -> 直接跳阶段四
- 若 `Finished=True` -> 结束会话

---

### 机制 D：阶段二，采集后续输入并生成 structured information

这是 `InteractionModule` 最核心的“结构化收集”能力。

流程：

1. 通过第二阶段 prompt 让 LLM 提问
2. 问题围绕：
   - thoughts
   - feelings
   - situations
3. LLM 输出 `[Asking]`
4. `FlowModule` 根据 `[Asking]` 给用户回答打标签
5. 这些带标签回答被存储为 `structured information`
6. 收集足够后生成 formulation summary
7. 用户确认后标记完成
8. 把 structured information 送到 `FirstModule`

所以它不只是聊天，还负责把聊天转成**可供理解模块处理的结构化输入**。

---

### 机制 E：阶段三，解释 intervention 并促成用户选择

当 `FirstModule` 已经给出一个或多个 intervention 后：

1. `InteractionModule` 取到推荐结果
2. 取到用户相关背景
3. 用第三阶段 prompt 让 LLM 解释 intervention
4. 让用户协作式选择
5. 一旦选定 intervention，进入第四阶段

---

### 机制 F：阶段四，交付 intervention

1. `InteractionModule` 取到用户选中的 intervention
2. 用第四阶段 prompt 驱动 LLM 执行干预
3. 干预以对话形式展开
4. 可结构化或非结构化
5. 结束后输出 completion signal

---

### 机制 G：如果信息不足，支持重新探索

专利里强调：
- 如果 `RecommenderModule` 发现证据不足
- 可以反过来 instruct `InteractionModule`
- 继续跟用户探索 top-K 未达阈值状态

所以它支持一个反馈闭环：

- exploration -> understanding -> recommendation
- 如果不足 -> back to exploration

---

### 机制 H：解释 intervention 给用户听

专利特别指出：

- InteractionModule 不只是 deliver intervention
- 还负责 `output information explaining the intervention to the user`

这意味着它覆盖两类用户可见输出：

1. 解释为什么做这个 intervention
2. 真正执行这个 intervention

---

### 机制 I：可生成 sequence of interventions

专利里还说：
- system responses 可以 deliver a sequence of interventions
- treatment plan 可以是多个 intervention 的序列

所以 InteractionModule 也可被视为一个**短期治疗流程交付器**，不仅是单步对话器。

---

**3. 输出的信息 / 变量**

`InteractionModule` 输出分两类：

### A. 面向用户的输出

1. `system_responses`
   - 作为对话内容发给用户

2. `information_explaining_intervention`
   - 解释某 intervention 为什么有帮助

3. `intervention_delivery_dialogue`
   - 具体执行 intervention 的对话

---

### B. 面向系统的输出

4. `structured_information`
   - 从后续用户输入中整理出的结构化材料
   - 供 `FirstModule` 使用

5. `routing_transitions`
   - 当前阶段切换到下一阶段的信息

6. `chosen_intervention`
   - 用户最终选了哪个 intervention

7. `dialogue_status`
   - 会话是否结束 / 是否进入下一阶段

---

### 可抽象变量

- `user_visible_response`
- `intervention_explanation`
- `structured_information`
- `next_interaction_state`
- `selected_intervention`
- `session_status`

---

**4. 建议你文档里直接用的结构化模板**

```text
Module: InteractionModule

Inputs:
- current user input (text / speech / numeric data)
- dialogue history
- previous system outputs
- user-specific context (therapy goal, prior interventions, key events, clinical summaries)
- knowledge-bank context
- outputs from the first module (subject profile / intervention recommendation)
- internal routing state and language-model flags
- prompt templates and output-format instructions

Mechanism:
- receive user input and manage the overall dialogue flow
- determine whether the user input contains information relating to a clinical state
- drive a multi-stage interaction through prompt generation + language model + flow parsing
- stage 1: open supportive conversation and route detection
- stage 2: gather subsequent input and generate structured information
- stage 3: explain and motivate intervention choice
- stage 4: deliver the chosen intervention through dialogue
- label user replies during exploration to build structured information
- pass structured information to the first module
- support looping back into further exploration when recommendation evidence is insufficient

Outputs:
- user-facing system responses
- information explaining the intervention
- intervention-delivery dialogue
- structured information for the first module
- routing / stage-transition signals
- selected intervention
- session / dialogue status
```

---

**5. 可直接放文档的阶段式子结构**

```text
InteractionModule
├─ Stage 1: Open Conversation
│  ├─ Goal: support user, detect Explore / Intent / Finished
│  └─ Output: first-stage response + routing flags
├─ Stage 2: Exploration / Structured Information Gathering
│  ├─ Goal: collect thought / feeling / situation information
│  └─ Output: structured information + formulation confirmation
├─ Stage 3: Motivate Intervention
│  ├─ Goal: explain why interventions may help and let user choose
│  └─ Output: selected intervention
└─ Stage 4: Deliver Intervention
   ├─ Goal: execute chosen intervention via dialogue
   └─ Output: intervention dialogue + completion signal
```

---

**6. 原文关键依据**

你整理时建议重点引用这些位置：

- `[0091]-[0094]`
- `[0098]`
- `[0429]-[0437]`
- `[0438]-[0491]`
- `[0559]-[0577]`
- claims `[130-135页]`

最关键的是：

- `[0430]`：InteractionModule 的总职责
- `[0432]-[0437]`：内部包含 PromptGenerationModule 与 LanguageModel
- `[0441]-[0454]`：第一阶段与路由
- `[0455]-[0465]`：第二阶段结构化探索
- `[0466]-[0483]`：第三阶段 intervention explanation / choice
- `[0484]-[0487]`：第四阶段 intervention delivery

---

**7. 和其它模块的关系**

**最短理解**

- `InteractionModule` = **总控编排层**
- `FlowModule` = **总控里面的路由/解析子模块**
- `PromptGenerationModule` = **总控里面的输入构造子模块**
- `LanguageModel` = **总控调用的生成引擎**
- `FirstModule` = **总控调用的理解与推荐后端**

---

**InteractionModule 是什么**

它负责整条“和用户互动”的主流程，包含：

1. 接收用户输入
2. 决定当前处于哪个对话阶段
3. 调用哪个 `PromptGenerator`
4. 调用 `LanguageModel`
5. 收集后续输入
6. 形成 `structured information`
7. 接收 `FirstModule` 的推荐结果
8. 再继续解释/交付 intervention

所以它是一个**大模块 / orchestration layer**。

---

**FlowModule 是什么**

`FlowModule` 只负责其中一小段但很关键的事：

1. 解析 LLM 输出里的 flags/字段
2. 判断下一步该去哪个阶段
3. 给用户回答打标签
4. 把结构化结果传给下游

所以它是一个**状态机路由器 + 输出解析器**。

它不负责：
- 选 prompt 模板
- 调用理解模型
- 推荐 intervention
- 组织完整交互闭环

---

**可以类比成一个 Web 应用**

如果把整套系统类比成一个 Web 后端：

- `InteractionModule`
  - 像 controller / application service
  - 负责整体请求流程

- `FlowModule`
  - 像 router + response parser
  - 负责看当前返回值，然后决定下一步跳哪

- `PromptGenerationModule`
  - 像 request builder
  - 负责构造发给 LLM 的输入

- `LanguageModel`
  - 像外部推理服务
  - 负责生成文本

- `FirstModule`
  - 像业务决策服务
  - 负责理解用户状态和推荐动作

---

**它们的边界再说直白一点**

**InteractionModule**
- “整个对话怎么跑”

**FlowModule**
- “LLM 这次输出里的控制信号是什么意思，下一步去哪”

**PromptGenerationModule**
- “这一步应该给 LLM 什么 prompt”

**LanguageModel**
- “根据 prompt 生成回复和标记”

**FirstModule**
- “根据结构化信息判断用户状态并推荐 intervention”

---

**按专利里的包含关系看**

专利其实已经暗示了这种层级：

- `InteractionModule`
  - 包含 / 联动 `PromptGenerationModule`
  - 包含 / 联动 `SecondModule(LanguageModel)`
  - 包含 `FlowModule`
  - 和 `FirstModule` 交互

所以 `FlowModule` 更像是 `InteractionModule` 内部的一个组件，而不是和它同级的大总控。
