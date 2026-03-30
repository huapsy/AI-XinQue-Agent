**RecommenderModule**

它是系统里的**干预选择层**。职责是：

- 接收 `SubjectUnderstandingModule` 产生的 `subject profile information`
- 结合用户背景、历史、治疗计划、反馈等信息
- 选出当前最合适的一个或一组 intervention
- 把结果提供给 `PromptGenerationModule` / `InteractionModule`

它回答的问题是：

- “既然我们已经知道用户当前可能处于什么状态，接下来该做什么？”

---

**1. 需要输入的信息 / 变量**

根据专利，输入主要分 4 类。

### A. 来自 SubjectUnderstandingModule 的输入

这是最核心输入。

1. `subject_profile_information`
   - 各种 mechanistic model 输出的状态集合
   - 如：
     - distorted thought
     - negative activity
     - negative sentiment
     - positive sentiment
     - positive activity
     - situation asked but thought given

2. `state_probabilities`
   - 每个状态对应的概率值
   - 用于 threshold、排序、top-k

3. `uncertainty_measures`
   - 可选
   - 如 standard error、entropy、置信度不足等

专利里明确示例：
- thought detector 输出 discrepancy + probability
- distorted thought detector 输出 distorted thoughts + probability
- sentiment model 输出 sentiment + probability
- behavioral model 输出 positive/negative activities + probability

---

### B. 用户背景 / patient information

4. `patient_information`
   - demographics
   - diagnosis
   - questionnaire scores
   - therapist-entered information
   - treatment intensity / treatment length suggestions

典型字段：
- age
- gender
- ethnicity
- disability status
- receiving previous mental health support
- diagnosis
- PHQ-9 / GAD-7 / disorder-specific questionnaires

---

### C. 历史 / history module

5. `history_module_output`
   - 已完成 intervention
   - intervention 次数
   - recency
   - 当前治疗进程
   - 既往 course of treatment

6. `stored_historical_data`
   - previous interventions
   - feedback on prior interventions
   - intervention effectiveness history

---

### D. 其他可选输入

7. `current_user_utterance`
   - 当前轮原始文本
   - 专利说某些实现也可直接把 utterance 输给 recommender

8. `multiple_previous_utterances`
   - 例如最近 N 条

9. `treatment_plan`
   - 已有预设 course/manual 里的 scheduled intervention

10. `feedback_from_user`
   - 对之前 intervention 的接受度、完成情况、效用评价

11. `target_metrics`
   - therapeutic alliance
   - patient outcomes
   - information gain

12. `guardrail_metrics`
   - 安全/约束指标

---

### 可抽象变量

- `subject_profile`
- `state_probs`
- `state_uncertainty`
- `patient_context`
- `history_context`
- `previous_interventions`
- `intervention_feedback`
- `scheduled_interventions`
- `target_metrics`
- `guardrails`

---

**2. 中间运行机制**

`RecommenderModule` 的机制在专利里有两层：

1. **简单规则映射版**
2. **更一般的 ML / recommender system 版**

---

### 机制 A：对 subject profile 做 threshold

这是最关键的一步。

1. 对每个状态拿到概率
2. 与预设 threshold 比较
3. 只有超过阈值的状态才进入后续推荐逻辑

专利强调：
- 每个 state 可有一个 threshold
- threshold 可固定
- 也可由模型学习

---

### 机制 B：对通过阈值的状态进行排序 / top-k

1. 所有超过阈值的状态按概率或强度排序
2. 形成 top-k most likely states
3. 再进入 intervention mapping

这是 claims 里写得很明确的结构：
- threshold
- rank
- top-k
- map to interventions

---

### 机制 C：把 state 映射到 intervention

这是规则版 recommender 的核心。

专利给的典型 state -> intervention 映射：

- `distorted thought` -> `thought restructuring`
- `negative activity` -> `behavioural activation`
- `negative sentiment` -> `emotion regulation`
- `positive sentiment + positive activity` -> `positive reinforcement`
- `situation asked but thought given` -> `situation analysis`

所以在简单版本里，本质是：

- 规则表 / lookup table / decision logic mapper

---

### 机制 D：对 intervention 再做过滤

即使某个 intervention 被映射出来，也不一定最终保留。

专利提到过滤时可考虑：

1. 是否以前做过
2. 是否适合该用户
3. 是否与 diagnosis / treatment plan 冲突
4. 是否存在现实风险
   - 如 abusive relationship
   - heart disease 不宜鼓励运动

所以它有一个**candidate generation -> filtering** 过程。

---

### 机制 E：对 intervention 结果排序

过滤后，推荐结果还会按 usefulness 排序。

结果可能是：

- 单个 intervention
- 一个短列表
- 一个 sequence / short treatment plan

然后把排序结果给后续第三阶段使用。

---

### 机制 F：如果信息不足，触发继续探索

这是专利里一个很重要的闭环设计。

如果：

- 没有状态超过阈值
- 或证据不足以推荐 intervention

则 recommender 可以：

1. 判断 `insufficient information`
2. 让 `InteractionModule` 继续问
3. 重点探索 top-K sub-threshold states
4. 新数据回来后再次运行 recommender

所以它不是一次性静态决策，而是可驱动“再收集一点信息”。

---

### 机制 G：一般化 recommender system / ML 版本

专利还给了更泛化的版本，不局限规则映射。

可能实现包括：

1. `trained neural network`
2. `tree-based classifier`
3. `supervised learning`
4. `reinforcement learning`
5. `contextual bandit`
6. 更一般的 recommender system

优化目标可包括：

- `therapeutic alliance`
- `patient outcomes`
- `information gain`

还可结合：

- patient similarity
- item similarity
- exploration vs exploitation
- uncertainty-aware recommendation

---

### 机制 H：输入可先做降维 / representation learning

专利还提到：
- inputs 可先经 PCA / autoencoder / variational autoencoder
- 以降低维度、提升泛化

这属于更一般系统设计，不是最核心但可记上。

---

**3. 输出的信息 / 变量**

核心输出是：

1. `subject_recommendation`
   - 面向用户当前状态的 intervention recommendation

---

### 具体输出形式

#### 基础版
- 单个 intervention
- 例如：
  - `thought restructuring`

#### 丰富版
- 排序后的 intervention 列表
- 如：
  1. Cognitive Restructuring
  2. 5 Areas Model

#### 更一般版
- `sequence of interventions`
- 短期计划 / one-off treatment plan
- planned next steps

---

### 还可能输出的附加信息

2. `intervention_ranking`
3. `usefulness_order`
4. `selected_goal`
5. `insufficient_information_flag`
6. `request_further_questions`
7. `top_k_states_to_explore`

---

### 下游用途

这些输出会被用于：

- `PromptGenerationModule` 生成第三阶段 prompt
- `InteractionModule` 解释和激励 intervention
- `FourthPromptGenerator` 交付已选 intervention
- `KnowledgeBank` 存储 recommendation history

---

### 可抽象变量

- `recommended_interventions`
- `ranked_interventions`
- `selected_intervention`
- `selected_goal`
- `insufficient_info`
- `explore_more_targets`
- `recommendation_metadata`

---

**4. 建议你文档里直接用的结构化模板**

```text
Module: RecommenderModule

Inputs:
- subject profile information from the subject understanding module
- state probabilities and optional uncertainty measures
- patient / demographic / diagnosis / questionnaire information
- historical data about prior interventions
- user feedback on prior interventions
- optional current utterance or recent utterance history
- optional scheduled treatment-plan interventions
- target metrics such as therapeutic alliance, patient outcomes, and information gain
- optional guardrail metrics

Mechanism:
- receive subject-profile states and associated probabilities
- apply thresholds to determine which states are strong enough
- rank states and optionally select top-k most likely states
- map states to interventions using decision logic / lookup rules / mapper
- optionally use trained recommender models instead of fixed rules
- filter candidate interventions based on history, suitability, diagnosis, treatment plan, and safety constraints
- rank remaining interventions by usefulness / predicted effectiveness
- if evidence is insufficient, request further exploration via the interaction module
- optionally optimize recommendation policy for therapeutic alliance, patient outcomes, and information gain

Outputs:
- subject recommendation / recommended intervention(s)
- ranked intervention list
- optional selected goal
- optional sequence of interventions
- optional insufficient-information flag
- optional request for further questions / exploration targets
```

---

**5. 可直接放文档的规则映射版**

```text
Example state -> intervention mapping
- distorted thought -> thought restructuring
- negative activity -> behavioural activation
- negative sentiment -> emotion regulation
- positive sentiment + positive activity -> positive reinforcement
- situation asked but thought given -> situation analysis
```

---

**6. 专利中的 intervention 集合示例**

专利给出的 pre-determined list of interventions 包括：

- Thought restructuring
- Behavioural activation
- Emotion regulation
- Positive reinforcement
- Situation analysis

以及更一般的 action set / exercise categories：

- Behavioural activation
- Mood Logs
- Thought Logs
- Thought Challenging
- Psychoeducation
- About cognitive distortions
- About core beliefs

---

**7. 原文关键依据**

你整理时建议重点引用这些段落：

- `[0022]`
- `[0088]-[0103]`
- `[0266]-[0300]`
- `[0283]-[0299]`
- `[0328]-[0369]`
- `[0495]`
- `[0524]-[0558]`
- claims `[132-135页]`

最关键的是：

- `[0088]`：decision logic 映射到 pre-determined interventions
- `[0092]`：不满足 threshold 时请求继续提问
- `[0268]-[0269]`：输入来源
- `[0294]`：优化目标 metrics
- `[0526]-[0552]`：具体状态、threshold、ranking、mapping、filtering

