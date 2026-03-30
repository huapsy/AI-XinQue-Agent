**FlowModule**

它是这套系统里的**对话状态路由器 / 输出解析器**。职责不是生成内容，而是：

- 读取 `LanguageModel` 输出中的标记、字段、标签
- 判断当前对话该进入哪个下一阶段
- 把必要的数据传给下游模块

简单说：

- `PromptGenerationModule` 负责“把什么喂给 LLM”
- `FlowModule` 负责“看 LLM 回了什么控制信息，然后决定下一步去哪”

---

**1. 输入信息 / 变量**

`FlowModule` 的核心输入来自 `LanguageModel` 输出，以及当前上下文。

### 核心输入

1. `language_model_output`
   - 当前轮 LLM 输出的完整文本
   - 这是最核心输入

2. `output_flags / output_fields`
   - LLM 输出里携带的控制字段
   - 例如：
     - `[Explore]`
     - `[Intent]`
     - `[Finished]`
     - `[Asking]`
     - `chosen_intervention`

3. `current_prompt_stage`
   - 当前输出是由哪个 prompt generator 生成的
   - 例如：
     - first
     - second
     - third
     - fourth

4. `previous_system_response`
   - 某些情况下需要知道上一轮系统问了什么
   - 特别是 second stage 中，要根据问题标签给用户回答打标签

5. `user_input`
   - 当前用户输入
   - 在某些流程下，FlowModule 不只解析 LLM 输出，也会结合用户输入识别 intervention 名称

6. `predefined_intervention_list`
   - 当用户表达想做某个 intervention，或在第三阶段做选择时
   - 用于匹配具体 intervention

7. `output_parser_rules / regex_patterns`
   - 用于从 LLM 输出中解析 flags、字段、JSON、schema

8. `default_values`
   - 当某些输出字段缺失时用于补默认值

9. `knowledge_bank / stored_context`
   - 解析完后，有些数据要存进去，或取出下游需要的内容

**可以抽象成变量**

- `llm_output_text`
- `parsed_flags`
- `parsed_fields`
- `stage`
- `current_user_input`
- `previous_question_label`
- `available_interventions`
- `parser_patterns`
- `default_output_values`

---

**2. 中间运行机制**

`FlowModule` 的机制可以概括为：**解析 -> 判定 -> 路由 -> 存储/传递**

---

### 机制 A：解析 LLM 输出中的 flags 和结构化字段

专利里最明确的一点就是：

- LLM 输出里会包含 flag 信息
- FlowModule 在输出真正给用户前解析这些标记

例如：

- `"Explore": True`
- `"Intent": True`
- `"Finished": True`
- `[Asking] = Situation / Feeling / Thought / Other`
- `chosen_intervention = Cognitive Restructuring`

实现上，专利提到：

- 可以用正则表达式解析
- 可以用 output parser
- 缺失字段可填默认值

所以第一步是一个**output parsing layer**。

---

### 机制 B：根据 flag 决定下一个模块 / 下一阶段

这是它最核心的工作。

#### 在 first stage

如果检测到：

1. `Intent = true`
   - 说明用户想直接做某个 intervention
   - 跳到 `FourthPromptGenerator`

2. `Explore = true`
   - 说明用户提到了值得深入探索的心理问题
   - 跳到 `SecondPromptGenerator`

3. `Finished = true`
   - 说明开放对话应结束
   - 终止会话或回首页

#### 在 second stage

如果检测到：

1. `[Asking]`
   - 说明当前系统问题属于：
     - thought
     - feeling
     - situation
     - other
   - FlowModule 用它给用户下一轮回答打标签

2. `Finished = true`
   - 说明结构化探索已完成
   - 把控制权转给 `FirstModule`
   - 让 `SubjectUnderstandingModule` 和 `RecommenderModule` 开始处理

#### 在 third stage

如果检测到：

1. `chosen_intervention`
   - 识别用户选了哪个 intervention

2. `finished = true`
   - 说明 intervention 选择阶段结束
   - 跳到 `FourthPromptGenerator`

#### 在 fourth stage

专利对 FlowModule 在第四阶段描述少一些，但可推知它至少会检测：
- 干预是否完成
- 是否退出或继续后续流程

---

### 机制 C：根据 system question label 给 user input 打标签

这是 second stage 特有的关键机制。

流程是：

1. LLM 在第二阶段提问时，输出 `[Asking] = Thought/Feeling/Situation`
2. 用户回复后
3. FlowModule 根据前一轮问题标签，把该用户回复标成：
   - `thought`
   - `feeling`
   - `situation`

4. 然后把这条带标签的用户输入存进 `KnowledgeBank`
5. 形成后续 `structured information`

所以它实际上承担了**把自然对话转成结构化记录**的桥梁作用。

---

### 机制 D：识别具体 intervention

在两个场景下，FlowModule 可能识别 intervention：

1. 用户一开始就说想做某个 exercise/intervention
2. 用户在第三阶段从建议列表中选择了某个 intervention

做法包括：

- 解析 LLM 输出
- 或解析用户输入
- 和预定义 intervention 列表做匹配
- 可通过正则、词短语匹配完成

---

### 机制 E：补默认值并持久化输出

专利提到：

- 缺失输出字段可填默认值
- 完整语言模型输出可保存到 `KnowledgeBank`
- 输出会被打上来自哪个 prompt generator 的标签

所以它也有轻量的数据整理职责：

- 标准化输出
- 保存输出
- 传递给下游模块

---

### 机制 F：消息传递，保证“无缝切阶段”

专利里非常强调：

- 用户感知不到 prompt stage 切换
- 这是因为 FlowModule 通过 message-passing 把上游输出传给下游 prompt

所以它还承担一种**状态延续器**的角色：

- 把上一阶段的重要输出整理给下一阶段使用

---

**3. 中间决策变量**

你可以把它抽象成这些中间状态：

- `parsed_explore_flag`
- `parsed_intent_flag`
- `parsed_finished_flag`
- `parsed_asking_label`
- `parsed_chosen_intervention`
- `next_module`
- `next_prompt_stage`
- `structured_label_for_user_reply`
- `session_should_end`
- `data_to_store`
- `data_to_pass_downstream`

---

**4. 输出信息 / 变量**

`FlowModule` 的输出不是给用户看的自然语言，而是**控制和结构化信息**。

### 主要输出类型

1. `routing_decision`
   - 下一步走哪个模块 / prompt generator
   - 如：
     - `go_to_second_prompt_generator`
     - `go_to_fourth_prompt_generator`
     - `go_to_first_module`
     - `terminate_dialogue`

2. `structured_labels`
   - 给用户输入打的标签
   - 如：
     - `thought`
     - `feeling`
     - `situation`

3. `identified_intervention`
   - 用户选择的 intervention
   - 如：
     - `Cognitive Restructuring`

4. `parsed_output_object`
   - 从 LLM 输出中抽出的结构化对象
   - 如：
     - `response`
     - `finished`
     - `chosen_intervention`
     - `asking`

5. `stored_records`
   - 写入 `KnowledgeBank` 的结构化记录

6. `downstream_context`
   - 传给下一阶段 prompt generator 或 FirstModule 的上下文

**可抽象成变量**

- `next_stage`
- `route_action`
- `labelled_user_input`
- `selected_intervention`
- `parsed_output`
- `knowledge_bank_update`
- `downstream_payload`

---

**5. 一句话版运行链路**

`LanguageModel output`
-> `FlowModule`
-> 解析 flags / labels / chosen_intervention
-> 判断下一步路由
-> 给用户输入打标签、更新知识库
-> 把结果传给下一模块

---

**6. 建议你文档里直接用的结构化模板**

```text
Module: FlowModule

Inputs:
- language-model output text
- output flags / structured fields emitted by the language model
- current prompt stage
- current user input
- previous system-response label (e.g. Asking field)
- predefined intervention list
- parser / regex rules
- optional default values for missing fields

Mechanism:
- parse language-model output for control flags and structured fields
- detect routing signals such as Explore / Intent / Finished
- detect stage-specific fields such as Asking or chosen_intervention
- determine next module / next prompt generator / session termination
- label user replies based on the previous system-question label
- optionally identify a concrete intervention from model output or user input
- populate missing values with defaults if needed
- store parsed / labelled output in the knowledge bank
- pass relevant context to downstream modules

Outputs:
- routing decision
- next stage / next module identifier
- labelled user input for structured-information building
- identified intervention (if any)
- parsed structured output object
- knowledge-bank update payload
- downstream context payload
```

---

**7. 和别的模块的边界**

为了区分清楚：

- `LanguageModel`
  - 生成自然语言 + flags/字段

- `FlowModule`
  - 解析这些 flags/字段
  - 负责状态转移和路由

- `PromptGenerationModule`
  - 根据当前路由状态，生成下一阶段 prompt

- `KnowledgeBank`
  - 存储被 FlowModule 标注/整理后的结果

所以 `FlowModule` 本质上像一个**状态机控制器 + 输出解析器**。

---

**8. 原文关键依据**

你整理时建议重点引用这些位置：

- `[0445]-[0449]`
  - first stage flags 解析和路由
- `[0450]-[0453]`
  - intervention 识别、Intent、Finished
- `[0459]-[0461]`
  - `[Asking]` 与用户输入标签化
- `[0463]-[0465]`
  - second stage finished 后转入 first module
- `[0483]`
  - third stage intervention 选择的 flag 解析
- `[0488]-[0491]`
  - output parser、默认值、message passing、seamless routing

最关键的是：

- `[0445]-[0447]`：FlowModule 解析 flag
- `[0460]`：FlowModule 根据问题标签标注用户回答
- `[0488]-[0490]`：FlowModule 作为输出解析和路由核心
