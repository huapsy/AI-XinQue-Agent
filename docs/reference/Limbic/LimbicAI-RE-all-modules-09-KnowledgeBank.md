**KnowledgeBank**

它是系统里的**持久化上下文与知识存储层**。职责不是做推理，而是：

- 存储用户相关信息、历史对话、历史 intervention、结构化信息、therapy-related knowledge
- 为 `PromptGenerationModule`、`RecommenderModule`、`FlowModule`、`InteractionModule` 提供可检索上下文
- 支持个性化、长期连续性和 explainability

你可以把它理解成：

- 一部分像用户档案库
- 一部分像 therapy 知识库
- 一部分像对话与 intervention 历史库

---

**1. 需要输入的信息 / 变量**

根据专利，`KnowledgeBank` 的输入主要来自三类。

### A. 来自用户与对话流程的输入

1. `input_text_data`
   - 用户输入文本
   - 专利里有一个版本会把用户输入同时送到 KnowledgeBank 做相似度检索

2. `dialogue_history`
   - 历史 user utterances
   - 历史 system responses

3. `structured_information`
   - 由 `InteractionModule + FlowModule` 生成
   - 比如带标签的：
     - thought
     - feeling
     - situation

4. `language_model_outputs`
   - 尤其是带 flags / labels / structured fields 的输出

---

### B. 来自理解与推荐模块的输入

5. `subject_profile_information`
   - 由 `SubjectUnderstandingModule` 生成
   - 包括各种 detected states / annotations

6. `recommendation_results`
   - 推荐出的 intervention
   - intervention ranking
   - chosen intervention

7. `feedback_after_intervention`
   - 用户对 intervention 的反馈
   - 是否完成、是否有帮助

---

### C. 知识库存储本体内容

8. `therapy_related_knowledge`
   - clinical knowledge
   - psychoeducation material
   - intervention descriptions

9. `patient_information`
   - demographics
   - diagnosis
   - questionnaire responses
   - therapist-entered info

10. `historical_information`
   - previous interventions
   - completed dates
   - frequency / recency
   - previous patterns

11. `relevant_background_information`
   - key life events
   - therapy goals
   - prior clinically relevant summaries

---

### 可抽象变量

- `raw_user_input`
- `conversation_records`
- `structured_records`
- `subject_profile_records`
- `recommendation_records`
- `intervention_feedback_records`
- `therapy_knowledge_entries`
- `patient_profile`
- `historical_profile`

---

**2. 中间运行机制**

`KnowledgeBank` 本身不是主要推理模块，但它有几种重要机制。

---

### 机制 A：存储 therapy-related knowledge

这是最基础的机制。

存储内容包括：

- intervention 描述
- psychoeducation 内容
- 临床知识
- 解释概念的背景材料

这些知识会被后续 prompt 检索和注入。

---

### 机制 B：存储 patient-specific information

专利明确指出 `KnowledgeBank` 可以包含用户信息，例如：

- demographics
- diagnosis
- questionnaire responses
- historical interventions
- prior detected patterns

这使系统能做个性化 prompt 和推荐。

---

### 机制 C：存储 dialogue outputs / structured outputs

系统运行时会不断把结果存进去，包括：

1. 用户带标签的回答
2. LLM 输出中的 flags / fields
3. structured information
4. subject profile information
5. chosen intervention
6. intervention completion history

这使系统具有连续会话能力和可审计性。

---

### 机制 D：基于相似度检索相关知识

这是专利里对 `KnowledgeBank` 最明确的“运行机制”。

流程：

1. 用户输入文本也送入 `KnowledgeBank`
2. 将用户输入 embedding 化
3. 将知识库条目也 embedding 化
4. 计算相似度
   - 例如 cosine similarity
5. 选出 top-N 最相关条目
   - 专利举例是 top 5
6. 把这些条目插入 system prompt

所以 `KnowledgeBank` 不只是静态存储，它还支持**retrieval augmentation**。

---

### 机制 E：支持 prompt generation 时的信息汇总

在不同 prompt stages 中，会从 `KnowledgeBank` 取不同内容：

#### 给 ThirdPromptGenerator
- 用户做过什么 intervention
- 核心 thoughts / feelings
- 当前 treatment plan
- recommender suggested interventions
- intervention short descriptions

#### 给 FourthPromptGenerator
- 选中的 intervention
- conversation history
- optional subject profile

#### 给初始 prompt
- previous engagements summary
- key life events
- prior clinical state
- therapy goal

---

### 机制 F：支持过滤与 explainability

因为它保存：

- 检测到的状态
- 为什么推荐某 intervention
- 过往做过什么
- 用户反馈如何

所以它支持：

1. recommender 的过滤
   - 避免重复
   - 根据历史适配

2. 审计 / explainability
   - 为什么系统做了这个选择
   - 哪些内部标签被触发

---

**3. 输出的信息 / 变量**

`KnowledgeBank` 的输出主要是**被检索和读取的上下文数据**。

### 主输出类型

1. `retrieved_knowledge_entries`
   - 与当前输入最相关的知识条目

2. `patient_information`
   - demographics
   - diagnosis
   - questionnaires
   - goals

3. `historical_information`
   - previous interventions
   - completed interventions
   - dates / frequency / recency
   - prior patterns

4. `stored_structured_information`
   - 之前的 thought/feeling/situation records

5. `stored_subject_profile_information`
   - 之前识别出的 states / annotations

6. `stored_intervention_descriptions`
   - 给第三阶段解释 intervention 使用

7. `stored_recommendation_history`
   - 推荐过什么、执行了什么、效果如何

---

### 下游使用方向

- 给 `PromptGenerationModule`
  - 做 prompt augmentation
- 给 `RecommenderModule`
  - 做历史过滤和个性化推荐
- 给 `FlowModule`
  - 保存与读取结构化输出
- 给报告 / 审计
  - 回溯内部逻辑

---

### 可抽象变量

- `knowledge_context`
- `patient_context`
- `historical_context`
- `retrieved_entries`
- `intervention_history`
- `stored_profile`
- `stored_structured_dialogue`

---

**4. 建议你文档里直接用的结构化模板**

```text
Module: KnowledgeBank

Inputs:
- user input text
- dialogue history
- structured information generated from labelled dialogue
- language-model outputs with flags / labels / structured fields
- subject profile information from the subject understanding module
- recommendation outputs from the recommender module
- intervention feedback / completion history
- therapy-related knowledge entries
- patient information and historical information

Mechanism:
- store therapy-related knowledge
- store patient-specific demographic / diagnosis / questionnaire data
- store structured dialogue records and subject-profile outputs
- store intervention history and user feedback
- support similarity-based retrieval by embedding current user input and knowledge entries
- compute similarity scores and return top relevant entries
- provide relevant patient / historical / intervention context to downstream modules
- support explainability, filtering, and longitudinal personalization

Outputs:
- retrieved knowledge entries relevant to current input
- patient information context
- historical information context
- stored structured information
- stored subject-profile information
- stored intervention descriptions and history
- downstream context payload for prompt generation and recommendation
```

---

**5. 可直接放文档的子内容划分**

```text
KnowledgeBank
├─ TherapyRelatedKnowledge
│  ├─ intervention descriptions
│  ├─ psychoeducation material
│  └─ clinical background knowledge
├─ PatientInformation
│  ├─ demographics
│  ├─ diagnosis
│  ├─ questionnaire responses
│  └─ therapy goals
├─ HistoricalInformation
│  ├─ previous interventions
│  ├─ completion history
│  ├─ dates / recency / counts
│  └─ prior clinically relevant patterns
├─ StructuredDialogueRecords
│  ├─ labelled user utterances
│  ├─ asking labels
│  └─ formulation-related records
└─ SubjectProfileRecords
   ├─ detected states
   ├─ probabilities
   └─ recommendation history
```

---

**6. 原文关键依据**

你整理时建议重点引用这些位置：

- `[0251]-[0252]`
- `[0372]`附近不是，忽略
- `[0398]-[0400]`
- `[0460]`
- `[0468]-[0481]`
- `[0488]-[0490]`
- `[0522]-[0523]`

最关键的是：

- `[0252]`：knowledge bank 检索与 prompt 注入
- `[0399]-[0400]`：system prompt 可加入 database / background knowledge / recommender outputs
- `[0460]`：带标签的用户输入存入 knowledge bank
- `[0468]-[0481]`：第三阶段从 knowledge bank 取 intervention/history/user characteristics
- `[0522]-[0523]`：patient info 与 historical info 的定义

