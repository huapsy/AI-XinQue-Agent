**SubjectUnderstandingModule**

它是整个系统里最核心的“机制化临床理解层”。职责是：

- 不让 LLM 直接从原始对话里自己推全部临床逻辑
- 而是先由一组较小、可解释的 understanding models
- 从用户输入或结构化信息中提取 `subject profile information`
- 再把这些结果供 `PromptGenerationModule`、`RecommenderModule`、`KnowledgeBank` 使用

它在专利里有两种主要工作形态：

1. **直接处理原始用户输入**
   - 早期版本：`input text -> understanding model -> subject profile`

2. **处理 interaction module 生成的 structured information**
   - 后期版本：`structured information(thought/feeling/situation...) -> multiple models -> subject profile`

---

**1. 需要输入的信息 / 变量**

根据专利，输入分两类：基础输入和扩展输入。

### 基础输入

1. `input_data / input_text`
   - 用户当前输入文本
   - 在基础版本中直接进入 understanding models

2. `structured_information`
   - 在交互式版本中，由 `InteractionModule + FlowModule` 先生成
   - 典型内容是被标注过的 user utterances，例如：
     - `thought`
     - `feeling`
     - `situation`

3. `labelled_user_utterances`
   - 从 structured information 中拆分出的分类列表
   - 如：
     - thought list
     - feeling list
     - situation list

### 模型运行所需输入

4. `vector_representation / embeddings`
   - 很多子模型先把文本转 embedding 再分类
   - 常见来源：
     - SentenceBERT
     - BERT
     - sentence embedder
     - bag-of-words / keyword representation

5. `threshold_values`
   - 某些模型输出概率，再用 threshold 决定是否触发状态

6. `predefined_classes / clinical labels`
   - 如：
     - distorted thought
     - positive sentiment
     - negative sentiment
     - activity
     - positive activity
     - negative activity

### 可选扩展输入

7. `patient_information`
   - demographics
   - questionnaire scores
   - diagnosis
   - therapist-entered info

8. `historical_information`
   - previous utterances
   - previous interventions
   - previous detected patterns

9. `knowledge_bank_context`
   - 某些版本中 general patient information 可被纳入 understanding context

### 可抽象变量

- `current_user_input`
- `structured_information`
- `thought_utterances`
- `feeling_utterances`
- `situation_utterances`
- `text_embeddings`
- `classification_thresholds`
- `patient_context`
- `historical_context`

---

**2. 中间运行机制**

`SubjectUnderstandingModule` 本质是一个**多模型推断管线**。

---

### 机制 A：单模型直接从原始输入提取 subject profile

这是较基础版本。

流程：

1. 用户输入文本进入某个 understanding model
2. 模型输出一个或多个 clinical classifications
3. classification 可为：
   - 是否 distorted
   - distortion 类型
   - core belief
   - 其他 clinical concept
4. 输出形成 `subject profile information`

典型例子：
- `"Everybody hates me"` -> cognitive distortion model -> `### DISTORTED ###`

---

### 机制 B：先把 structured information 按类别拆分，再送入多个 mechanistic models

这是后期、更完整版本。

流程：

1. `InteractionModule` 先通过第二阶段对话收集材料
2. `FlowModule` 依据 `[Asking]` 给用户回复打标签
3. 得到 structured information
4. `SubjectUnderstandingModule` 按标签拆成多个列表：
   - thoughts
   - feelings
   - situations
5. 各列表分别进入不同子模型
6. 各子模型的输出被汇总、注释、归纳成 `subject profile information`

---

### 机制 C：由多个具体子模型分别推断不同状态

专利中明确列出的核心子模型包括：

#### 1. `ThoughtDetectionModel`
- 输入：用户 utterance，尤其是被标为 thought/situation/feeling 的 utterance
- 机制：
  - embedding
  - 二分类 thought / non-thought
- 用途：
  - 验证某条 utterance 是否真是 thought
  - 发现 “situation asked but thought given” 这类 mismatch

#### 2. `DistortedThoughtDetectionModel`
- 输入：已识别为 thought 的 utterance
- 机制：
  - embedding
  - 二分类 distorted / not distorted
  - 或多分类 distortion type
- 输出：
  - distorted thoughts
  - probability
  - 可选 distortion label

#### 3. `SentimentAnalysisModel`
- 输入：feeling / situation utterances
- 机制：
  - sentiment classifier
- 输出：
  - positive / neutral / negative sentiment
  - probability vector

#### 4. `BehaviouralPatternDetectionModel`
- 输入：用户 utterances
- 机制：
  - 先判断是不是 activity
  - 再将 activity 映射到预定义 activity 类别
  - 再识别 positive / negative activity
- 输出：
  - positive activities
  - negative activities
  - activity probabilities

#### 5. 其他扩展模型
- `BehaviouralUnderstandingModule`
- `CoreBeliefsModel`
- `TopicModel`
- 还可用 prompted LLM 作为 mechanistic classifier

---

### 机制 D：embedding + 小模型分类

专利非常强调这点：

1. 文本先转成向量表示
2. 再由较小参数量模型分类
3. 这些小模型比 LLM 参数少很多，训练成本低、可解释性更强

常见实现方式：
- sentence embedder
- word-count embedder
- feed-forward network
- tree-based model
- transformer-based small classifier

---

### 机制 E：用概率 + threshold 决定最终状态

很多子模型输出不是直接硬标签，而是概率。

例如：
- `probability(thought)`
- `probability(distorted thought)`
- `probability(positive sentiment)`
- `probability(activity class)`

然后：
1. 与 threshold 比较
2. 超过阈值的状态才进入后续 profile
3. 概率也可能被保留给 recommender 使用

---

### 机制 F：处理问答标签与真实语义不一致的问题

专利里一个很关键的点：

- 用户回答不一定真的符合问题标签
- 所以理解模块要二次校验

例子：
- 系统问的是 `situation`
- 用户答的是 “I am a bad person”
- 虽然被流程标签标成 `situation`
- 但 thought detector 会把它识别成 thought
- 最终 profile 可记为：
  - `situation asked but thought given`

这是它的重要可解释性设计点。

---

### 机制 G：汇总多个模型结果形成 subject profile information

所有子模型运行后，模块会把结果汇总成高层 profile。

专利里的 profile 可能包括：

- distorted thought detected
- reduced activity detected
- positive activity detected
- negative sentiment detected
- automatic thoughts detected
- situation/thought discrepancy
- 其他 clinical constructs

有时是标签列表，有时也带原始 utterance 和概率。

---

**3. 输出的信息 / 变量**

主输出是：

1. `subject_profile_information`

这是理解模块最核心的产物。

---

### 输出可能包含的内容

#### 基础版
- `### DISTORTED ###`
- `### NOT DISTORTED ###`

#### 丰富版
- `distorted thought detected: ["I am a failure"]`
- `reduced activity detected: ["struggle to get out of bed"]`
- `positive activity detected: [...]`
- `negative sentiment detected: [...]`
- `situation asked but thought given: [...]`

#### 也可能包含
- class labels
- probabilities
- ranked states
- uncertainty indicators

---

### 供下游使用的输出方向

1. 给 `PromptGenerationModule`
   - 用于生成 prompt
   - 例如把 `distorted thought` 注入 prompt

2. 给 `RecommenderModule`
   - 作为 intervention mapping 输入

3. 给 `KnowledgeBank`
   - 存储 profile 和记忆

4. 给报告 / audit
   - 用于 explainability

---

### 可抽象变量

- `subject_profile`
- `detected_states`
- `classified_utterances`
- `state_probabilities`
- `uncertainty_measures`
- `annotated_profile_summary`

---

**4. 建议你文档里直接用的结构化模板**

```text
Module: SubjectUnderstandingModule

Inputs:
- raw user input text and/or structured information generated from dialogue
- labelled user utterances (e.g. thought / feeling / situation)
- embeddings / vector representations of utterances
- optional threshold values for state detection
- optional patient / demographic / historical context

Mechanism:
- receive either raw text or structured information
- split structured user utterances into category-specific lists
- run one or more mechanistic models over the relevant utterances
- examples of mechanistic models:
  - thought detection model
  - distorted thought detection model
  - sentiment analysis model
  - behavioural pattern detection model
  - optional core-beliefs / topic models
- convert text into vector representations before classification when needed
- produce probabilities or labels for specific clinical states
- apply thresholds where relevant
- correct mismatches between prompted label and actual user meaning
- aggregate model outputs into subject profile information

Outputs:
- subject profile information
- detected states / labels
- utterance-level annotations
- optional probabilities / uncertainty measures
- profile summary for prompt generation, recommendation, storage, and audit
```

---

**5. 可直接放文档的子模型清单**

```text
SubjectUnderstandingModule
├─ ThoughtDetectionModel
│  ├─ Input: labelled utterances
│  ├─ Output: thought / non-thought + probability
│  └─ Use: validate thought category, detect mismatches
├─ DistortedThoughtDetectionModel
│  ├─ Input: thought utterances
│  ├─ Output: distorted / not distorted (+ optional distortion type) + probability
│  └─ Use: detect cognitive distortions
├─ SentimentAnalysisModel
│  ├─ Input: feeling / situation utterances
│  ├─ Output: positive / neutral / negative + probabilities
│  └─ Use: detect emotional valence
├─ BehaviouralPatternDetectionModel
│  ├─ Input: user utterances
│  ├─ Output: activity / non-activity, then positive / negative activity
│  └─ Use: infer behavioural patterns
├─ BehaviouralUnderstandingModule
├─ CoreBeliefsModel
└─ TopicModel
```

---

**6. 原文关键依据**

你整理时建议重点引用这些位置：

- `[0011]-[0029]`
- `[0154]-[0160]`
- `[0184]-[0204]`
- `[0319]-[0327]`
- `[0495]-[0521]`
- claims:
  - `[132-135页]`

最关键的段落是：

- `[0184]-[0185]`：基础版理解模块
- `[0190]-[0204]`：cognitive distortion 示例
- `[0495]-[0499]`：structured information 进入 understanding module
- `[0500]-[0519]`：thought / distorted thought / sentiment / behavior 各子模型
- `[0521]`：最终生成 subject profile information
