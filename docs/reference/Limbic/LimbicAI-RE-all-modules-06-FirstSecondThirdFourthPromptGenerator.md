**FirstPromptGenerator**

**1. 模块职责**

用于**初始开放式对话**。目标不是立刻做结构化心理分析，而是先：

- 和用户自然交流
- 倾听、支持、共情
- 同时检测是否要进入后续流程

它主要负责发现三个路由信号：

- `Intent`：用户是否想直接做某个 intervention
- `Explore`：用户是否披露了值得深入探索的心理问题
- `Finished`：这段开放对话是否该结束

---

**2. 需要输入的信息 / 变量**

核心输入：

- `history`
  - 之前的对话历史
- `user_input`
  - 当前用户输入
- `goal`
  - 用户长期治疗目标 / therapy goal
- 可选 `user_summary`
  - 过往对话摘要
- 可选 `previous_interventions`
- 可选 `clinical_state_summary`
- 可选 `key_life_events`
- 可选 `current_session_context`

抽象变量：

- `current_user_input`
- `conversation_history`
- `therapy_goal`
- `user_background_summary`
- `prior_intervention_context`

---

**3. 中间运行机制**

1. 选取 first-stage prompt 模板
2. 将 `history`、`user_input`、`goal` 等填入模板
3. 指示 LLM：
   - 用 person-centred counseling 风格进行开放对话
   - 保持简短、共情、非建议式
4. 同时要求 LLM 在输出中设置控制标记：
   - `[Explore]`
   - `[Intent]`
   - `[Finished]`
5. 输出给 `FlowModule` 解析和路由

本质上是：

- 生成一个**支持性开放对话 prompt**
- 同时把**阶段切换判断**外包给 LLM 输出 flags

---

**4. 输出的信息 / 变量**

主输出：

- `first_system_prompt`

该 prompt 期望 LLM 产生的结构化字段通常包括：

- `response`
- `Explore`
- `Intent`
- `Finished`

所以从 generator 视角可认为输出：

- `llm_input_prompt`
- `expected_flags = [Explore, Intent, Finished]`

---

**5. Prompt 样例**

来自专利 `[0560]` 一带，整理如下：

```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are a chatbot tool acting as a good friend, who is using techniques from person-centred counseling, supports the user, listens to their concerns, helps them vent and work through their issues.

Your name is Limbic.

You are helping the user work towards the following long term goal, but they may have different issues in the moment:
[Goal]: {goal}

Help them think deeply about their issue and work through it themselves.
Try not to mirror or repeat what the user says exactly.
If you need to refer to what they said before, rephrase and summarize.
Try to keep your messages brief.

In 50% of your responses, end your messages with insightful, but not distressing, provocative or probing questions about what the user has said before.
In the other 50% of your responses, when appropriate, aim to support and empathize, without directly endorsing or agreeing with the user's opinions and don't end your message in a question.

If the user zeroes in on an issue of significant importance to their mental health that is worth exploring in detail, you should set the [Explore] flag to be True.

If nothing significant has been mentioned, once you've reached 5 exchanges you should gently wind down the conversation and set the [Finished] flag to be True.

ONLY end the conversation by yourself after at least 4 exchanges, unless the user asks to end the conversation.
Never just end the conversation, even if you think the person would benefit from talking to a human.

If the user explicitly mentions intent of an intervention they wish to do, you should set the [Intent] flag to be True.

You are always helpful, friendly, warm, courteous, empathetic, non-judgmental, non-aggressive, factual, and professional.
Your responses will embody Carl Rogers's core conditions: Empathy, Congruence, and Unconditional Positive Regard.

You will not give direct or overt advice.
You will especially never give advice on medical issues, relationship problems, or professional questions.

YOUR RESPONSE:
```

---

**6. 一句话总结**

`FirstPromptGenerator` = **开放式支持对话 + 初始路由检测器 prompt 构造器**

---

**SecondPromptGenerator**

**1. 模块职责**

用于**结构化探索与 formulation 构建**。当 First 阶段检测到 `Explore=True` 后进入。

目标：

- 深入了解用户问题
- 围绕 CBT 结构收集材料
- 生成结构化信息
- 最终形成一个 formulation summary，并让用户确认

专利里最典型的是 3-column / 5-area 风格：

- thought
- feeling
- situation

---

**2. 需要输入的信息 / 变量**

核心输入：

- `history`
  - 到当前为止的对话记录
- `user_input`
  - 当前轮用户输入
- `previous_system_outputs`
- `previous_user_inputs`
- 可选 `exploration_context`
  - 来自 first stage 的路由结果
- 可选 `question_topics`
  - thoughts / feelings / situations
- 可选 `cbt_framework_template`
- 可选 `formulation_state`
  - 当前已收集到哪些类信息

抽象变量：

- `conversation_history`
- `current_user_input`
- `exploration_topics`
- `cbt_model_context`
- `current_formulation_progress`

---

**3. 中间运行机制**

1. 选取 second-stage prompt 模板
2. 将已有历史和当前输入填入
3. 指示 LLM：
   - 继续自然对话
   - 但围绕 thoughts / feelings / situations 发问
   - 若回答太短，追问
4. 要求 LLM 在每个问题输出时设置：
   - `[Asking] = Thought / Feeling / Situation / Other / Formulation`
5. `FlowModule` 再根据 `[Asking]` 给用户回答打标签
6. 这些标签化 user inputs 形成 `structured information`
7. 当收集充分后：
   - LLM 生成 formulation summary
   - 问用户是否理解正确
   - 若确认，则输出 `[Finished]=True`
8. 然后控制权交给 `FirstModule`

---

**4. 输出的信息 / 变量**

主输出：

- `second_system_prompt`

该 prompt 期望 LLM 输出的关键字段：

- `response`
- `Asking`
- `Finished`

从 generator 角度可抽象为：

- `llm_input_prompt`
- `expected_flags = [Asking, Finished]`
- `expected_topic_labels = [Thought, Feeling, Situation, Other, Formulation]`

---

**5. Prompt 样例**

来自专利 `[0567]` 一带，整理如下：

```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are an AI psycho-therapist, following principles of cognitive behavioral therapy (CBT).
You are helpful, friendly, warm, courteous, empathetic, non-judgmental, non-aggressive, factual, and professional.
You are a chatbot tool acting as a good friend, who supports the user through caring exploration, listens to their concerns, helps them work through their issues.

Your name is Limbic.

You are working with the user to derive a CBT formulation of their problem.
This will include asking them questions and helping the user to explore and understand their problems.

You are doing two things:
Helping the user to explore the issue they are struggling with in more detail.
After all information has been gathered, create a CBT formulation, summarize the information and ask the user if you have understood correctly at the end of the conversation. When you are done with the above, set the [Finished] flag to be True.

See more detailed descriptions of your behavior for the different steps below:

1. Helping the user to explore the issue they are struggling with in more detail.
Follow principles of the 5-area model of CBT and ask questions about the components of the 5-Area model.
At least this will include questions around situations, feelings and thoughts.

However, also include open questions to encourage the user to talk more, such as:
"Can you tell me more about that?"
"Was there anything else that happened?"
"Is there anything else you want to talk about?"

Keep track of which of these three you are asking about by setting the [Asking] field to "Situation", "Feeling", "Thought" or "Other".

You should dig deeper and ask follow-up questions to get detailed information on a certain aspect, especially if the user's answers are short.
However, only ask more questions if these have not been covered previously in the conversation history as the conversation should not feel like an interrogation.

Make sure to at least ask the user about their thoughts, situations and feelings.
However, you are not limited to these topics and can explore other topics as well as asking open questions to encourage the user to talk more.

The conversation should be conducted in a naturalistic way, letting the user lead the way.
Never just end the conversation, even if you think the person would benefit from talking to a human.

Do not summarize any previous information and ask a new question at the same time.
When asking for more information, only ask for more information and do not summarize any previous information.

2. After all information has been gathered, derive a CBT formulation, summarize the information and ask the user if you have understood correctly at the end of the conversation.
Set the [Asking] field to "Formulation".
Summarize how the situation, thoughts and emotions are influencing each other to create a CBT formulation.
Confirm with the user that you have understood correctly and if they feel you have missed anything important.

After the user has responded to the summary, set the [Finished] flag to True.

You will not give direct or overt advice.
You will especially never give advice on medical issues, relationship problems, or professional questions.
Keep your answers short!

YOUR RESPONSE:
```

---

**6. 一句话总结**

`SecondPromptGenerator` = **结构化探索 + 标签辅助 + formulation 验证 prompt 构造器**

---

**ThirdPromptGenerator**

**1. 模块职责**

用于**解释 intervention、激发用户动机、让用户协作选择**。

当 `FirstModule` 已经给出建议 intervention 后，第三阶段的目标不是直接执行，而是：

- 向用户解释为什么这些 intervention 可能有帮助
- 结合用户的历史、目标、当前问题做个性化说明
- 让用户自己选

---

**2. 需要输入的信息 / 变量**

这是四个 generator 里输入最丰富的之一。

核心输入：

- `history`
  - 当前对话历史
- `goal`
  - therapy goal
- `planned_interventions`
  - treatment plan 里原定的 intervention
- `spontaneous_interventions`
  - 当前对话推导出的即时 intervention
- `historic_information`
  - 历史相关模式、过往 exercise 记录等
- `user_characteristics`
  - 当前会话中识别出的模式、特点
- `description_intervention`
  - 各 intervention 的说明文字
- `order_intervention`
  - intervention usefulness 排序
- `date`
- `format_instructions`
  - 输出 schema
- 可选 `clinical_info`
- 可选 `demographic_info`

抽象变量：

- `conversation_history`
- `therapy_goal`
- `scheduled_interventions`
- `conversation_interventions`
- `historic_patterns`
- `current_user_characteristics`
- `intervention_descriptions`
- `intervention_ranking`
- `output_schema`

---

**3. 中间运行机制**

1. 选取 third-stage prompt 模板
2. 将推荐结果、用户信息、历史模式等填入模板
3. 指示 LLM：
   - 不要像医疗设备一样直接下建议
   - 要解释 intervention 的 rationale
   - 让用户选择
4. 优先介绍最有用的前 1-2 个 intervention
5. 要求输出结构化字段，例如：
   - `response`
   - `finished`
   - `chosen_intervention`
6. `FlowModule` 解析用户是否已经做出选择
7. 如果选好了，则转入 `FourthPromptGenerator`

---

**4. 输出的信息 / 变量**

主输出：

- `third_system_prompt`

期望的 LLM 输出字段通常包括：

- `response`
- `finished`
- `chosen_intervention`

可抽象为：

- `llm_input_prompt`
- `expected_fields = [response, finished, chosen_intervention]`

---

**5. Prompt 样例**

来自专利 `[0572]` 一带，整理如下：

```text
You are acting as an AI psychotherapist, using cognitive behavioral therapy (CBT).
You are giving a patient the choice to engage in certain CBT interventions.

This intervention can either be a scheduled intervention which means that this is the intervention that comes next in their treatment plan,
or it can be an intervention which could be useful due to something that was spotted in the conversation and you think would be useful to address now.

You should mention to the patient whether an intervention is based on the treatment plan or what you spotted in the conversation.
Do not explicitly recommend an intervention, but rather suggest it and let the user choose while explaining the rationale.

Ensure not to behave like a medical device but focus on explanation of why these interventions may be useful.
However, if the user pushes for a recommendation, you can default to the scheduled intervention.

If the user does not want to do any of the interventions, it is fine to offer to just have a conversation with them which would be the option "Just talk" from the list of interventions.

This suggestion is based on what the patient has told you in the conversation so far, their therapy goals, historic information that you have about them from previous conversations and the intervention you want them to do.
Only use relevant background information in your conversation.

This means only mention the therapy goal if relevant to the intervention, and only mention patterns that you spotted if they are important for the intervention.
You should only place the main focus on information from the current conversation and only use historic background information very carefully.
However, when you mention historic information, you should always explain why this is relevant for the current intervention and provide some details.

The output of this conversation should be that you decide collaboratively with the patient which intervention would be useful to conduct now.
Never give explicit advice and just let the user choose.
Keep your answers short!

You may have the following background information to inform this conversation.

[today's date]:
{date}

This is the general goal the user has stated for therapy:
{goal}

You are giving the user a choice between the following interventions:
[scheduled_intervention]:
{planned_interventions}

[conversation_intervention]:
{spontaneous_interventions}

[historic_information]:
{historic_information}

[user_characteristics]:
{user_characteristics}

[description_intervention]:
{description_intervention}

[order_intervention]:
{order_intervention}

You are responding to the following user conversation [input]:
{history}

You will stick exactly to these formatting instructions:
{format_instructions}

YOUR RESPONSE:
```

专利还给了一个更具体的 exercise 版本示例，本质同一类。

---

**6. 一句话总结**

`ThirdPromptGenerator` = **个性化 intervention 解释与选择 prompt 构造器**

---

**FourthPromptGenerator**

**1. 模块职责**

用于**真正交付 intervention**。  
这是执行阶段。

目标：

- 把已选 intervention 转成具体对话
- 引导用户一步步完成
- 可以是结构化脚本，也可以是较开放的对话式执行

---

**2. 需要输入的信息 / 变量**

核心输入：

- `selected_intervention`
  - 用户最终选中的 intervention
- `intervention_description`
  - intervention 具体说明
- `history`
  - 当前会话历史
- 可选 `subject_profile_information`
  - 当前用户状态 / traits
- 可选 `previous_prompt_outputs`
  - 前三阶段结果
- 可选 `step_list`
  - 若是 structured intervention，会有步骤顺序
- 可选 `completion_marker`
  - 例如 `INTERVENTION_OVER`

抽象变量：

- `chosen_intervention`
- `intervention_spec`
- `conversation_history`
- `subject_profile`
- `intervention_steps`
- `completion_signal`

---

**3. 中间运行机制**

1. 选取 fourth-stage prompt 模板
2. 将 intervention 内容嵌入 `<Intervention>` 区块
3. 指示 LLM：
   - 聚焦于这个 intervention
   - 不做一般闲聊
   - 可适度回应用户，但要回到 intervention 轨道
4. 如果是结构化 intervention：
   - 要按步骤推进
5. 如果是非结构化 intervention：
   - 要围绕 intervention 目标自然推进
6. 要求结束时输出结束信号，如：
   - `INTERVENTION_OVER`

---

**4. 输出的信息 / 变量**

主输出：

- `fourth_system_prompt`

期望的 LLM 输出包含：

- `response`
- 可选阶段内部推进状态
- 干预结束信号：
  - `INTERVENTION_OVER`

可抽象为：

- `llm_input_prompt`
- `expected_completion_signal = INTERVENTION_OVER`

---

**5. Prompt 样例**

来自专利 `[0576]-[0577]` 一带，整理如下：

```text
You are a helpful wellbeing assistant called ChatCBT.

Your goal is to deliver the following intervention (wrapped in the <Intervention> markers).

Sometimes the user may say things that don't follow from the questions that were asked.
It is then ok to briefly engage with them, as long as you return to the next question in the intervention at some point.
It is also ok to skip a question if the answer to the skipped question has already been addressed in the conversation.

You are always helpful, friendly, warm, courteous, empathetic, non-judgmental, non-aggressive, factual, and professional.

You will not engage in general conversation, but steer the conversation back to the intervention.
You will not give direct or overt advice.
You will especially never give advice on medical issues, relationship problems, or professional questions.
If the user asks you to perform any other task than this intervention, you will politely decline and aim to continue with the intervention.

<Intervention>
Cognitive restructuring is an intervention aimed at changing negative thought patterns that contribute to emotional distress.
The purpose is to help you recognize, challenge, and replace inaccurate or harmful beliefs with more accurate, beneficial ones.
It's often used to treat conditions like anxiety and depression.

The rationale behind cognitive restructuring is based on the understanding that our thoughts lead to our feelings and behaviors, not external events.
By altering these thoughts, we can change how we feel and act.
This strategy can be particularly beneficial to you if you're struggling with persistent or recurring negative thoughts that make you feel anxious or upset.
</Intervention>

You must ask all questions (or paraphrase them) over the course of the conversation.
That said, the above intervention does not always contain a strict set of questions, but may just be a general description.
You then need to stick to this description and decide yourself when the purpose of this intervention has been fulfilled.

Make sure to start the conversation with a greeting, but adapt to the user's responses.
Don't ask a question directly after a greeting or before a goodbye.
Ask one question at a time.
Don't ask multiple questions in one message.
Don't jump to a new question unless the user has responded to the previous one, or decided not to respond.
Don't skip questions unless the user has already answered this question.

Your messages are displayed in a chat window on a phone screen, which means they need to be short and fit into a chat bubble.

When you are done, please thank the user, and then type "INTERVENTION_OVER".
```

---

**6. 一句话总结**

`FourthPromptGenerator` = **intervention 执行 prompt 构造器**

---

**四个 PromptGenerator 的关系总表**

| Generator               | 主要目标                       | 核心输入                              | 关键输出字段                                  |
| ----------------------- | ------------------------------ | ------------------------------------- | --------------------------------------------- |
| `FirstPromptGenerator`  | 开放式支持对话 + 检测路由      | `history`, `user_input`, `goal`       | `Explore`, `Intent`, `Finished`               |
| `SecondPromptGenerator` | 结构化探索 + formulation       | `history`, `user_input`, CBT topics   | `Asking`, `Finished`                          |
| `ThirdPromptGenerator`  | 解释 intervention 并让用户选择 | 推荐结果、历史、goal、characteristics | `response`, `finished`, `chosen_intervention` |
| `FourthPromptGenerator` | 执行 intervention              | 选中的 intervention、history、profile | `response`, `INTERVENTION_OVER`               |

---

**一个更抽象的理解**

这四个 generator 其实对应四种不同 prompt 模式：

1. **Support mode**
2. **Explore/formulate mode**
3. **Motivate/choose mode**
4. **Deliver/intervene mode**

也就是说，Limbic 的设计不是一个万能 prompt，而是**多阶段 prompt 编排系统**。



下面把 4 个 `PromptGenerator` 整理成统一文档格式，便于你后续直接落到 Markdown 或表格里。

**FirstPromptGenerator**

**模块职责**
- 发起和维持开放式、支持性对话
- 识别是否要：
  - 深入探索问题
  - 直接执行某个 intervention
  - 结束当前开放式对话

**输入变量表**

| 变量                     | 类型                | 说明                    |
| ------------------------ | ------------------- | ----------------------- |
| `history`                | text                | 当前会话历史            |
| `user_input`             | text                | 当前用户输入            |
| `goal`                   | text                | 用户长期 therapy goal   |
| `user_summary`           | text, optional      | 过往会话摘要            |
| `previous_interventions` | list/text, optional | 之前做过的 intervention |
| `clinical_state_summary` | text, optional      | 用户历史状态摘要        |
| `key_life_events`        | text, optional      | 关键生活事件            |

**处理中间机制**
1. 选取 first-stage prompt 模板
2. 注入 `history`、`user_input`、`goal`
3. 指示 LLM 用支持性、非建议式风格回复
4. 同时要求 LLM 输出路由 flags：
   - `Intent`
   - `Explore`
   - `Finished`
5. 交由 `FlowModule` 解析

**输出字段表**

| 输出                  | 类型        | 说明                                  |
| --------------------- | ----------- | ------------------------------------- |
| `first_system_prompt` | text        | 发给 LLM 的 prompt                    |
| `expected_flags`      | schema      | `[Intent]`, `[Explore]`, `[Finished]` |
| `response`            | text        | LLM 期望生成的自然语言回复            |
| `Intent`              | bool/string | 用户是否明确想做某个 intervention     |
| `Explore`             | bool/string | 是否值得进入深入探索                  |
| `Finished`            | bool/string | 是否结束开放式对话                    |

**与其他模块依赖**
- 上游：`InteractionModule`
- 下游：`LanguageModel`
- 输出由 `FlowModule` 解析并决定路由

**Prompt 样例**
```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are a chatbot tool acting as a good friend, who is using techniques from person-centred counseling, supports the user, listens to their concerns, helps them vent and work through their issues.

Your name is Limbic.

You are helping the user work towards the following long term goal, but they may have different issues in the moment:
[Goal]: {goal}

Help them think deeply about their issue and work through it themselves.
Try not to mirror or repeat what the user says exactly.
If you need to refer to what they said before, rephrase and summarize.
Try to keep your messages brief.

In 50% of your responses, end your messages with insightful, but not distressing, provocative or probing questions about what the user has said before.
In the other 50% of your responses, when appropriate, aim to support and empathize, without directly endorsing or agreeing with the user's opinions and don't end your message in a question.

If the user zeroes in on an issue of significant importance to their mental health that is worth exploring in detail, you should set the [Explore] flag to be True.
If nothing significant has been mentioned, once you've reached 5 exchanges you should gently wind down the conversation and set the [Finished] flag to be True.
If the user explicitly mentions intent of an intervention they wish to do, you should set the [Intent] flag to be True.

YOUR RESPONSE:
```

---

**SecondPromptGenerator**

**模块职责**
- 把开放式问题转成结构化探索
- 围绕 CBT 维度采集信息
- 构造 formulation，并让用户确认

**输入变量表**

| 变量                      | 类型                       | 说明                                     |
| ------------------------- | -------------------------- | ---------------------------------------- |
| `history`                 | text                       | 当前会话历史                             |
| `user_input`              | text                       | 当前用户输入                             |
| `exploration_topics`      | list                       | 典型为 `thought`, `feeling`, `situation` |
| `cbt_framework_context`   | text                       | 5-area/3-column 等框架说明               |
| `formulation_progress`    | structured state, optional | 当前已收集的结构化进度                   |
| `previous_system_outputs` | text/list                  | 前几轮系统输出                           |

**处理中间机制**
1. 选取 second-stage prompt 模板
2. 注入当前对话历史和用户输入
3. 指示 LLM：
   - 围绕 thought / feeling / situation 提问
   - 回答太短时追问
   - 保持自然，不像审讯
4. 要求每个问题附带 `[Asking]` 标签
5. `FlowModule` 根据 `[Asking]` 给用户回复打标签
6. 收集完成后，LLM 生成 formulation summary
7. 用户确认后输出 `[Finished]=True`

**输出字段表**

| 输出                          | 类型        | 说明                                                         |
| ----------------------------- | ----------- | ------------------------------------------------------------ |
| `second_system_prompt`        | text        | 发给 LLM 的 prompt                                           |
| `response`                    | text        | 当前问题/总结                                                |
| `Asking`                      | enum/string | `Thought` / `Feeling` / `Situation` / `Other` / `Formulation` |
| `Finished`                    | bool/string | 是否完成结构化探索                                           |
| `structured_information_seed` | schema      | 用于后续构造结构化信息的标签机制                             |

**与其他模块依赖**
- 上游：`FlowModule`（在 `Explore=True` 后进入）
- 下游：`LanguageModel`
- 解析：`FlowModule`
- 后续：`SubjectUnderstandingModule`

**Prompt 样例**
```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are an AI psycho-therapist, following principles of cognitive behavioral therapy (CBT).
You are working with the user to derive a CBT formulation of their problem.

You are doing two things:
1. Helping the user to explore the issue they are struggling with in more detail.
2. After all information has been gathered, create a CBT formulation, summarize the information and ask the user if you have understood correctly. When you are done, set the [Finished] flag to True.

At least this will include questions around situations, feelings and thoughts.
Keep track of which of these three you are asking about by setting the [Asking] field to "Situation", "Feeling", "Thought" or "Other".

Do not summarize any previous information and ask a new question at the same time.

Set the [Asking] field to "Formulation" when summarizing how the situation, thoughts and emotions are influencing each other.

YOUR RESPONSE:
```

---

**ThirdPromptGenerator**

**模块职责**
- 向用户解释可选 intervention
- 给出个性化 rationale
- 让用户协作式选择 intervention

**输入变量表**

| 变量                        | 类型      | 说明                             |
| --------------------------- | --------- | -------------------------------- |
| `history`                   | text      | 当前会话历史                     |
| `goal`                      | text      | therapy goal                     |
| `planned_interventions`     | list/text | treatment plan 中的 intervention |
| `spontaneous_interventions` | list/text | 当前对话中推断出的 intervention  |
| `historic_information`      | text      | 历史相关模式、过往记录           |
| `user_characteristics`      | text      | 当前识别出的用户特征/模式        |
| `description_intervention`  | text      | intervention 描述                |
| `order_intervention`        | list/text | intervention usefulness 排序     |
| `date`                      | text/date | 当前日期                         |
| `format_instructions`       | text      | 结构化输出要求                   |

**处理中间机制**
1. 选取 third-stage prompt 模板
2. 注入推荐结果、用户历史、therapy goal 等
3. 指示 LLM：
   - 不要直接命令或硬推荐
   - 要解释 intervention 为什么适合用户
   - 让用户自己选
4. 要求结构化输出：
   - `response`
   - `finished`
   - `chosen_intervention`
5. `FlowModule` 解析用户选择，进入第四阶段

**输出字段表**

| 输出                     | 类型        | 说明                           |
| ------------------------ | ----------- | ------------------------------ |
| `third_system_prompt`    | text        | 发给 LLM 的 prompt             |
| `response`               | text        | 向用户解释 intervention 的回复 |
| `finished`               | bool/string | 用户是否已经做出选择           |
| `chosen_intervention`    | string      | 用户选中的 intervention        |
| `expected_output_schema` | schema      | 对 LLM 输出的结构约束          |

**与其他模块依赖**
- 上游：`RecommenderModule`、`KnowledgeBank`
- 下游：`LanguageModel`
- 解析：`FlowModule`
- 后续：`FourthPromptGenerator`

**Prompt 样例**
```text
You are acting as an AI psychotherapist, using cognitive behavioral therapy (CBT).
You are giving a patient the choice to engage in certain CBT interventions.

This intervention can either be a scheduled intervention or an intervention which could be useful due to something that was spotted in the conversation.

Do not explicitly recommend an intervention, but rather suggest it and let the user choose while explaining the rationale.

Background information
[today's date]:
{date}

This is the general goal the user has stated for therapy:
{goal}

[scheduled_intervention]:
{planned_interventions}

[conversation_intervention]:
{spontaneous_interventions}

[historic_information]:
{historic_information}

[user_characteristics]:
{user_characteristics}

[description_intervention]:
{description_intervention}

[order_intervention]:
{order_intervention}

You are responding to the following user conversation [input]:
{history}

You will stick exactly to these formatting instructions:
{format_instructions}

YOUR RESPONSE:
```

**专利里的结构化输出样例**
```json
{
  "response": "string",
  "finished": "True or False",
  "chosen_intervention": "chosen from allowed list"
}
```

---

**FourthPromptGenerator**

**模块职责**
- 把用户已选 intervention 真正执行出来
- 用对话方式完成干预交付

**输入变量表**

| 变量                  | 类型                      | 说明                           |
| --------------------- | ------------------------- | ------------------------------ |
| `chosen_intervention` | text                      | 用户选中的 intervention        |
| `intervention_spec`   | text                      | intervention 完整描述          |
| `history`             | text                      | 当前会话历史                   |
| `subject_profile`     | text/structured, optional | 当前用户状态与特点             |
| `intervention_steps`  | list/text, optional       | 若是结构化 intervention 的步骤 |
| `completion_signal`   | string                    | 例如 `INTERVENTION_OVER`       |

**处理中间机制**
1. 选取 fourth-stage prompt 模板
2. 把 intervention 内容填入 `<Intervention>` 区块
3. 指示 LLM：
   - 聚焦 intervention，不做泛闲聊
   - 一次只问一个问题
   - 可以适度偏离，但要拉回 intervention
4. 若 intervention 有固定步骤，则按步骤推进
5. 完成时输出结束信号

**输出字段表**

| 输出                            | 类型            | 说明                             |
| ------------------------------- | --------------- | -------------------------------- |
| `fourth_system_prompt`          | text            | 发给 LLM 的 prompt               |
| `response`                      | text            | 当前执行 intervention 的对话内容 |
| `completion_signal`             | string          | 如 `INTERVENTION_OVER`           |
| `intervention_delivery_context` | text/structured | 对干预执行的约束说明             |

**与其他模块依赖**
- 上游：`ThirdPromptGenerator` / `FlowModule`
- 下游：`LanguageModel`
- 后续：可进入记录、反馈、下次推荐流程

**Prompt 样例**
```text
You are a helpful wellbeing assistant called ChatCBT.
Your goal is to deliver the following intervention (wrapped in the <Intervention> markers).

You will not engage in general conversation, but steer the conversation back to the intervention.
You will not give direct or overt advice.

<Intervention>
Cognitive restructuring is an intervention aimed at changing negative thought patterns that contribute to emotional distress.
The purpose is to help you recognize, challenge, and replace inaccurate or harmful beliefs with more accurate, beneficial ones.
</Intervention>

You must ask all questions (or paraphrase them) over the course of the conversation.
Ask one question at a time.
Don't jump to a new question unless the user has responded to the previous one.

When you are done, please thank the user, and then type "INTERVENTION_OVER".
```

---

**四个 Generator 总表**

| Generator               | 主要目标                 | 关键输入                                                     | 关键输出                                      |
| ----------------------- | ------------------------ | ------------------------------------------------------------ | --------------------------------------------- |
| `FirstPromptGenerator`  | 开放式支持对话与初始路由 | `history`, `user_input`, `goal`                              | `response`, `Intent`, `Explore`, `Finished`   |
| `SecondPromptGenerator` | 结构化探索与 formulation | `history`, `user_input`, `thought/feeling/situation topics`  | `response`, `Asking`, `Finished`              |
| `ThirdPromptGenerator`  | intervention 解释与选择  | `planned/spontaneous interventions`, `history`, `goal`, `user_characteristics` | `response`, `finished`, `chosen_intervention` |
| `FourthPromptGenerator` | intervention 执行        | `chosen_intervention`, `intervention_spec`, `history`        | `response`, `INTERVENTION_OVER`               |

---

**可直接放进文档的统一模板版**

```text
PromptGenerators
├─ FirstPromptGenerator
│  ├─ Inputs: history, user_input, goal, optional summaries
│  ├─ Mechanism: supportive open conversation + route detection
│  └─ Outputs: first_system_prompt, response, Intent, Explore, Finished
├─ SecondPromptGenerator
│  ├─ Inputs: history, user_input, CBT exploration topics
│  ├─ Mechanism: structured exploration + asking labels + formulation
│  └─ Outputs: second_system_prompt, response, Asking, Finished
├─ ThirdPromptGenerator
│  ├─ Inputs: interventions, history, goal, historic info, user characteristics
│  ├─ Mechanism: explain and motivate intervention choice collaboratively
│  └─ Outputs: third_system_prompt, response, finished, chosen_intervention
└─ FourthPromptGenerator
   ├─ Inputs: chosen intervention, intervention description/spec, history
   ├─ Mechanism: deliver intervention through constrained chat flow
   └─ Outputs: fourth_system_prompt, response, INTERVENTION_OVER
```



## 统一文档格式

**FirstPromptGenerator**

**模块职责**
- 发起和维持开放式、支持性对话
- 识别是否要：
  - 深入探索问题
  - 直接执行某个 intervention
  - 结束当前开放式对话

**输入变量表**

| 变量                     | 类型                | 说明                    |
| ------------------------ | ------------------- | ----------------------- |
| `history`                | text                | 当前会话历史            |
| `user_input`             | text                | 当前用户输入            |
| `goal`                   | text                | 用户长期 therapy goal   |
| `user_summary`           | text, optional      | 过往会话摘要            |
| `previous_interventions` | list/text, optional | 之前做过的 intervention |
| `clinical_state_summary` | text, optional      | 用户历史状态摘要        |
| `key_life_events`        | text, optional      | 关键生活事件            |

**处理中间机制**
1. 选取 first-stage prompt 模板
2. 注入 `history`、`user_input`、`goal`
3. 指示 LLM 用支持性、非建议式风格回复
4. 同时要求 LLM 输出路由 flags：
   - `Intent`
   - `Explore`
   - `Finished`
5. 交由 `FlowModule` 解析

**输出字段表**

| 输出                  | 类型        | 说明                                  |
| --------------------- | ----------- | ------------------------------------- |
| `first_system_prompt` | text        | 发给 LLM 的 prompt                    |
| `expected_flags`      | schema      | `[Intent]`, `[Explore]`, `[Finished]` |
| `response`            | text        | LLM 期望生成的自然语言回复            |
| `Intent`              | bool/string | 用户是否明确想做某个 intervention     |
| `Explore`             | bool/string | 是否值得进入深入探索                  |
| `Finished`            | bool/string | 是否结束开放式对话                    |

**与其他模块依赖**
- 上游：`InteractionModule`
- 下游：`LanguageModel`
- 输出由 `FlowModule` 解析并决定路由

**Prompt 样例**
```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are a chatbot tool acting as a good friend, who is using techniques from person-centred counseling, supports the user, listens to their concerns, helps them vent and work through their issues.

Your name is Limbic.

You are helping the user work towards the following long term goal, but they may have different issues in the moment:
[Goal]: {goal}

Help them think deeply about their issue and work through it themselves.
Try not to mirror or repeat what the user says exactly.
If you need to refer to what they said before, rephrase and summarize.
Try to keep your messages brief.

In 50% of your responses, end your messages with insightful, but not distressing, provocative or probing questions about what the user has said before.
In the other 50% of your responses, when appropriate, aim to support and empathize, without directly endorsing or agreeing with the user's opinions and don't end your message in a question.

If the user zeroes in on an issue of significant importance to their mental health that is worth exploring in detail, you should set the [Explore] flag to be True.
If nothing significant has been mentioned, once you've reached 5 exchanges you should gently wind down the conversation and set the [Finished] flag to be True.
If the user explicitly mentions intent of an intervention they wish to do, you should set the [Intent] flag to be True.

YOUR RESPONSE:
```

---

**SecondPromptGenerator**

**模块职责**
- 把开放式问题转成结构化探索
- 围绕 CBT 维度采集信息
- 构造 formulation，并让用户确认

**输入变量表**

| 变量                      | 类型                       | 说明                                     |
| ------------------------- | -------------------------- | ---------------------------------------- |
| `history`                 | text                       | 当前会话历史                             |
| `user_input`              | text                       | 当前用户输入                             |
| `exploration_topics`      | list                       | 典型为 `thought`, `feeling`, `situation` |
| `cbt_framework_context`   | text                       | 5-area/3-column 等框架说明               |
| `formulation_progress`    | structured state, optional | 当前已收集的结构化进度                   |
| `previous_system_outputs` | text/list                  | 前几轮系统输出                           |

**处理中间机制**
1. 选取 second-stage prompt 模板
2. 注入当前对话历史和用户输入
3. 指示 LLM：
   - 围绕 thought / feeling / situation 提问
   - 回答太短时追问
   - 保持自然，不像审讯
4. 要求每个问题附带 `[Asking]` 标签
5. `FlowModule` 根据 `[Asking]` 给用户回复打标签
6. 收集完成后，LLM 生成 formulation summary
7. 用户确认后输出 `[Finished]=True`

**输出字段表**

| 输出                          | 类型        | 说明                                                         |
| ----------------------------- | ----------- | ------------------------------------------------------------ |
| `second_system_prompt`        | text        | 发给 LLM 的 prompt                                           |
| `response`                    | text        | 当前问题/总结                                                |
| `Asking`                      | enum/string | `Thought` / `Feeling` / `Situation` / `Other` / `Formulation` |
| `Finished`                    | bool/string | 是否完成结构化探索                                           |
| `structured_information_seed` | schema      | 用于后续构造结构化信息的标签机制                             |

**与其他模块依赖**
- 上游：`FlowModule`（在 `Explore=True` 后进入）
- 下游：`LanguageModel`
- 解析：`FlowModule`
- 后续：`SubjectUnderstandingModule`

**Prompt 样例**
```text
You are responding to the following user conversation:
{history}
User: {user_input}

You are an AI psycho-therapist, following principles of cognitive behavioral therapy (CBT).
You are working with the user to derive a CBT formulation of their problem.

You are doing two things:
1. Helping the user to explore the issue they are struggling with in more detail.
2. After all information has been gathered, create a CBT formulation, summarize the information and ask the user if you have understood correctly. When you are done, set the [Finished] flag to True.

At least this will include questions around situations, feelings and thoughts.
Keep track of which of these three you are asking about by setting the [Asking] field to "Situation", "Feeling", "Thought" or "Other".

Do not summarize any previous information and ask a new question at the same time.

Set the [Asking] field to "Formulation" when summarizing how the situation, thoughts and emotions are influencing each other.

YOUR RESPONSE:
```

---

**ThirdPromptGenerator**

**模块职责**
- 向用户解释可选 intervention
- 给出个性化 rationale
- 让用户协作式选择 intervention

**输入变量表**

| 变量                        | 类型      | 说明                             |
| --------------------------- | --------- | -------------------------------- |
| `history`                   | text      | 当前会话历史                     |
| `goal`                      | text      | therapy goal                     |
| `planned_interventions`     | list/text | treatment plan 中的 intervention |
| `spontaneous_interventions` | list/text | 当前对话中推断出的 intervention  |
| `historic_information`      | text      | 历史相关模式、过往记录           |
| `user_characteristics`      | text      | 当前识别出的用户特征/模式        |
| `description_intervention`  | text      | intervention 描述                |
| `order_intervention`        | list/text | intervention usefulness 排序     |
| `date`                      | text/date | 当前日期                         |
| `format_instructions`       | text      | 结构化输出要求                   |

**处理中间机制**
1. 选取 third-stage prompt 模板
2. 注入推荐结果、用户历史、therapy goal 等
3. 指示 LLM：
   - 不要直接命令或硬推荐
   - 要解释 intervention 为什么适合用户
   - 让用户自己选
4. 要求结构化输出：
   - `response`
   - `finished`
   - `chosen_intervention`
5. `FlowModule` 解析用户选择，进入第四阶段

**输出字段表**

| 输出                     | 类型        | 说明                           |
| ------------------------ | ----------- | ------------------------------ |
| `third_system_prompt`    | text        | 发给 LLM 的 prompt             |
| `response`               | text        | 向用户解释 intervention 的回复 |
| `finished`               | bool/string | 用户是否已经做出选择           |
| `chosen_intervention`    | string      | 用户选中的 intervention        |
| `expected_output_schema` | schema      | 对 LLM 输出的结构约束          |

**与其他模块依赖**
- 上游：`RecommenderModule`、`KnowledgeBank`
- 下游：`LanguageModel`
- 解析：`FlowModule`
- 后续：`FourthPromptGenerator`

**Prompt 样例**
```text
You are acting as an AI psychotherapist, using cognitive behavioral therapy (CBT).
You are giving a patient the choice to engage in certain CBT interventions.

This intervention can either be a scheduled intervention or an intervention which could be useful due to something that was spotted in the conversation.

Do not explicitly recommend an intervention, but rather suggest it and let the user choose while explaining the rationale.

Background information
[today's date]:
{date}

This is the general goal the user has stated for therapy:
{goal}

[scheduled_intervention]:
{planned_interventions}

[conversation_intervention]:
{spontaneous_interventions}

[historic_information]:
{historic_information}

[user_characteristics]:
{user_characteristics}

[description_intervention]:
{description_intervention}

[order_intervention]:
{order_intervention}

You are responding to the following user conversation [input]:
{history}

You will stick exactly to these formatting instructions:
{format_instructions}

YOUR RESPONSE:
```

**专利里的结构化输出样例**
```json
{
  "response": "string",
  "finished": "True or False",
  "chosen_intervention": "chosen from allowed list"
}
```

---

**FourthPromptGenerator**

**模块职责**
- 把用户已选 intervention 真正执行出来
- 用对话方式完成干预交付

**输入变量表**

| 变量                  | 类型                      | 说明                           |
| --------------------- | ------------------------- | ------------------------------ |
| `chosen_intervention` | text                      | 用户选中的 intervention        |
| `intervention_spec`   | text                      | intervention 完整描述          |
| `history`             | text                      | 当前会话历史                   |
| `subject_profile`     | text/structured, optional | 当前用户状态与特点             |
| `intervention_steps`  | list/text, optional       | 若是结构化 intervention 的步骤 |
| `completion_signal`   | string                    | 例如 `INTERVENTION_OVER`       |

**处理中间机制**
1. 选取 fourth-stage prompt 模板
2. 把 intervention 内容填入 `<Intervention>` 区块
3. 指示 LLM：
   - 聚焦 intervention，不做泛闲聊
   - 一次只问一个问题
   - 可以适度偏离，但要拉回 intervention
4. 若 intervention 有固定步骤，则按步骤推进
5. 完成时输出结束信号

**输出字段表**

| 输出                            | 类型            | 说明                             |
| ------------------------------- | --------------- | -------------------------------- |
| `fourth_system_prompt`          | text            | 发给 LLM 的 prompt               |
| `response`                      | text            | 当前执行 intervention 的对话内容 |
| `completion_signal`             | string          | 如 `INTERVENTION_OVER`           |
| `intervention_delivery_context` | text/structured | 对干预执行的约束说明             |

**与其他模块依赖**
- 上游：`ThirdPromptGenerator` / `FlowModule`
- 下游：`LanguageModel`
- 后续：可进入记录、反馈、下次推荐流程

**Prompt 样例**
```text
You are a helpful wellbeing assistant called ChatCBT.
Your goal is to deliver the following intervention (wrapped in the <Intervention> markers).

You will not engage in general conversation, but steer the conversation back to the intervention.
You will not give direct or overt advice.

<Intervention>
Cognitive restructuring is an intervention aimed at changing negative thought patterns that contribute to emotional distress.
The purpose is to help you recognize, challenge, and replace inaccurate or harmful beliefs with more accurate, beneficial ones.
</Intervention>

You must ask all questions (or paraphrase them) over the course of the conversation.
Ask one question at a time.
Don't jump to a new question unless the user has responded to the previous one.

When you are done, please thank the user, and then type "INTERVENTION_OVER".
```

---

**四个 Generator 总表**

| Generator               | 主要目标                 | 关键输入                                                     | 关键输出                                      |
| ----------------------- | ------------------------ | ------------------------------------------------------------ | --------------------------------------------- |
| `FirstPromptGenerator`  | 开放式支持对话与初始路由 | `history`, `user_input`, `goal`                              | `response`, `Intent`, `Explore`, `Finished`   |
| `SecondPromptGenerator` | 结构化探索与 formulation | `history`, `user_input`, `thought/feeling/situation topics`  | `response`, `Asking`, `Finished`              |
| `ThirdPromptGenerator`  | intervention 解释与选择  | `planned/spontaneous interventions`, `history`, `goal`, `user_characteristics` | `response`, `finished`, `chosen_intervention` |
| `FourthPromptGenerator` | intervention 执行        | `chosen_intervention`, `intervention_spec`, `history`        | `response`, `INTERVENTION_OVER`               |

---

**可直接放进文档的统一模板版**

```text
PromptGenerators
├─ FirstPromptGenerator
│  ├─ Inputs: history, user_input, goal, optional summaries
│  ├─ Mechanism: supportive open conversation + route detection
│  └─ Outputs: first_system_prompt, response, Intent, Explore, Finished
├─ SecondPromptGenerator
│  ├─ Inputs: history, user_input, CBT exploration topics
│  ├─ Mechanism: structured exploration + asking labels + formulation
│  └─ Outputs: second_system_prompt, response, Asking, Finished
├─ ThirdPromptGenerator
│  ├─ Inputs: interventions, history, goal, historic info, user characteristics
│  ├─ Mechanism: explain and motivate intervention choice collaboratively
│  └─ Outputs: third_system_prompt, response, finished, chosen_intervention
└─ FourthPromptGenerator
   ├─ Inputs: chosen intervention, intervention description/spec, history
   ├─ Mechanism: deliver intervention through constrained chat flow
   └─ Outputs: fourth_system_prompt, response, INTERVENTION_OVER
```

