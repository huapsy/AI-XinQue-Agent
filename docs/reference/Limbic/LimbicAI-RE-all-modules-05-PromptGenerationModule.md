**PromptGenerationModule**

它是这套系统里非常关键的“输入编排器”。职责是：

- 收集来自各模块的上下文
- 选择/组装合适的 prompt 模板
- 生成给 `LanguageModel` 的 `system prompt` 或更广义的 `system input`

它解决的问题是：

- 不是让 LLM 裸聊
- 而是让 LLM 在**被约束、被引导、被补充背景**的情况下输出回复

---

**1. 输入信息 / 变量**

根据专利，`PromptGenerationModule` 的输入来源很多，核心包括：

1. `input_data / user_input`
   - 当前用户输入文本
   - 在基础版本里，这就是 prompt 的直接组成部分之一

2. `subject_profile_information`
   - 来自 `SubjectUnderstandingModule`
   - 例如：
     - `### DISTORTED ###`
     - `### NOT DISTORTED ###`
     - 或更丰富的 clinical labels / predictions

3. `subject_recommendation / identified_intervention`
   - 来自 `SubjectRecommendationModule / RecommenderModule`
   - 例如推荐某个 intervention、goal、exercise

4. `dialogue_history / user_history`
   - 过往用户 utterances
   - 过往 system responses
   - 可以是原始历史，也可以是 summary

5. `general_prompt_template / stored_text_template`
   - 存储的 prompt 模板
   - 专利里反复提到通过模板生成 system prompt

6. `background_knowledge / knowledge_bank_entries`
   - 从 `KnowledgeBank` 检索出来的相关知识
   - 可能是：
     - clinical knowledge
     - patient information
     - intervention descriptions

7. `patient_information`
   - 用户人口统计信息、历史治疗信息、诊断、问卷等
   - 在不同例子里有时来自 `KnowledgeBank`，有时来自其他模块

8. `history_module_output`
   - 经过过滤的历史信息
   - 如最近 N 条 utterances、相关 intervention history

9. `flow / routing context`
   - 当前所处阶段
   - 比如是：
     - first prompt
     - second prompt
     - third prompt
     - fourth prompt

10. `format_instructions / flags schema`
   - 某些 prompt 需要语言模型输出结构化字段
   - 例如：
     - `[Explore]`
     - `[Intent]`
     - `[Finished]`
     - `[Asking]`
     - JSON schema fields

11. 可选输入：numeric / physiological data
   - step count
   - number of activities
   - heart rate
   - 其他数值状态

**可以抽象成变量**

- `current_user_input`
- `subject_profile`
- `recommendation`
- `conversation_history`
- `prompt_template`
- `knowledge_context`
- `patient_context`
- `history_context`
- `prompt_stage`
- `format_schema`
- `numeric_context`

---

**2. 中间运行机制**

`PromptGenerationModule` 的核心机制可以分成几步。

### 机制 A：选择或检索模板

专利里最明确的机制之一：

1. 先从存储中取一个 `stored text template`
2. 基础例子里可能只有一个模板
3. 扩展例子里，可以在多个模板中选择
4. 模板的选择依据可能包括：
   - subject profile information
   - 当前阶段
   - 推荐 intervention
   - 用户输入内容

所以它首先是一个**template selector / retriever**。

---

### 机制 B：把多个输入拼接成 system prompt

这是最核心机制。

专利里多次说明 prompt 是由这些内容组合而成：

1. `general prompt`
   - 角色、上下文、目标、可用技术说明

2. `user input`
   - 当前轮用户文本

3. `subject profile information`
   - 例如 `# Distorted thought #`

4. 可选的 `recommendation`
   - 推荐 intervention / immediate action

5. 可选的 `history`
   - 先前的对话内容

6. 可选的 `background knowledge`
   - 检索出的知识库条目

7. 可选的 `patient-specific info`
   - therapy goal
   - prior interventions
   - demographics
   - historic patterns

8. 可选的 `format instructions`
   - 限制 LLM 输出格式

所以本质上是一个**multi-source context composer**。

---

### 机制 C：不同阶段生成不同类型的 prompt

在专利的交互式版本里，`PromptGenerationModule` 不是只有一个 prompt builder，而是分成四个 prompt generator。

1. `FirstPromptGenerator`
   - 用于开放式初始对话
   - 目标：
     - 和用户自然交流
     - 检测 `Intent / Explore / Finished`

2. `SecondPromptGenerator`
   - 用于结构化探索
   - 目标：
     - 让 LLM 询问 thoughts / feelings / situations
     - 给问题打标签
     - 最后生成 formulation summary

3. `ThirdPromptGenerator`
   - 用于解释和激励 intervention
   - 目标：
     - 告诉用户有哪些 intervention
     - 解释为什么适合他
     - 让用户选择

4. `FourthPromptGenerator`
   - 用于交付 intervention
   - 目标：
     - 按结构化或非结构化方式执行干预

也就是说，它内部其实是**按对话阶段做 prompt specialization**。

---

### 机制 D：在 prompt 中嵌入控制字段和格式约束

专利里一个非常重要的做法是：

- prompt 不只告诉 LLM“怎么说”
- 还告诉 LLM“要输出哪些控制字段”

例如：

- `[Intent]`
- `[Explore]`
- `[Finished]`
- `[Asking]`
- `chosen_intervention`
- `response`

所以它还承担**给下游 FlowModule 预埋状态字段**的职责。

---

### 机制 E：可做后处理 / post-process

专利里提到：

- `system prompt may be post-processed before being provided to the language model`

这说明它还可能有一步轻量后处理，例如：

- 清洗格式
- 附加标签
- 调整顺序
- 插入安全或控制字段

---

### 机制 F：生成的不一定是文本 prompt，也可能是 state representation

专利还留了一个更泛化表述：

- 在主要例子里，输出是 `system prompt` 文本
- 但也可以输出为 `state representation`
- 例如某种 context embedding / 向量状态

所以从抽象上说，它的产出是 `system input`，不一定局限纯文本。

---

**3. 中间决策变量**

你可以把它整理成这些中间状态：

- `selected_template`
- `prompt_stage`
- `included_subject_profile`
- `included_recommendation`
- `included_history`
- `included_background_knowledge`
- `included_patient_context`
- `included_format_constraints`
- `post_processed_prompt`
- `system_input_type`

---

**4. 输出信息 / 变量**

核心输出只有一个主产物，但内部可拆。

### 主输出

1. `system_prompt`
   - 文本形式的 prompt
   - 最常见输出

或更一般：

2. `system_input`
   - 可能是文本 prompt
   - 也可能是状态表示 / embedding

### 附带输出特征

生成的 prompt 里通常会包含：

- 用户当前输入
- 角色说明
- 对话目标
- clinical / mechanistic labels
- intervention recommendation
- history
- retrieved knowledge
- output schema / flags

### 对下游的作用

这个输出会被送入：

- `SecondModule -> LanguageModel`

所以可以抽象成：

- `llm_input_text`
- `llm_input_context`
- `expected_output_schema`

---

**5. 一句话版运行链路**

`user input + subject profile + recommendation + history + knowledge + template`
-> `PromptGenerationModule`
-> 选择模板、拼接上下文、嵌入控制字段
-> 生成 `system prompt / system input`
-> 送给 `LanguageModel`

---

**6. 建议你文档里直接用的结构化模板**

```text
Module: PromptGenerationModule

Inputs:
- current user input
- subject profile information from subject understanding module
- optional subject recommendation / identified intervention
- dialogue history / summaries
- stored prompt templates
- optional knowledge-bank context
- optional patient / demographic / clinical context
- optional filtered history-module output
- prompt-stage / routing state
- optional format instructions / flags schema
- optional numeric / physiological context

Mechanism:
- retrieve or select a stored prompt template
- combine template with current user input
- inject subject-profile signals (e.g. distorted thought labels)
- optionally inject recommendation / intervention information
- optionally inject history, background knowledge, and patient context
- optionally inject output-format constraints and control flags
- optionally post-process the composed prompt
- generate a stage-specific system prompt or broader system input

Outputs:
- system prompt (text) or more general system input
- prompt content structured for the language model
- optional embedded flags / output schema expectations
```

