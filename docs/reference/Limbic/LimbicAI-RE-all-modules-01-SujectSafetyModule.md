`SubjectSafetyModule` 是**输入侧安全闸门**。其职责为：

- 在系统继续生成普通回复之前
- 先检查**用户输入是否存在风险**
- 如果有风险，就**阻断后续正常对话链路**，转到安全应答/人工升级/规则流程

**SubjectSafetyModule**

**1. 输入信息 / 变量**

核心输入：

1. `input_data`
   - 用户输入数据
   - 可以是 `speech` 或 `text`
   - 如果是语音，通常先经 `ASRModule` 转成 `input_text_data`

2. `user_input_text`
   - 更具体地说，安全模块实际处理的是用户当前轮文本
   - 专利里多次写的是 `user input text` / `each user input text`

3. 可选输入：风险检测资源
   - `pre_defined_words`
   - `pre_defined_phrases`
   - `regex_rules`
   - 这些不是用户输入，但属于运行所需配置

4. 可选输入：训练好的风险分类模型
   - 一个二分类模型，输出如：
     - `risk`
     - `no risk`

5. 可选输入：危机场景对应模板
   - `stored_text_template`
   - 用于命中风险后直接给用户返回安全提示、支持资源、热线等

**可整理成变量表**

- `raw_input_data`
- `input_text`
- `risk_keywords`
- `risk_phrases`
- `risk_regex_patterns`
- `risk_classifier`
- `crisis_response_templates`

---

**2. 中间运行机制**

**机制 A：基于触发词 / 短语 / 正则的规则检测**

运行过程：

1. 取当前用户输入文本
2. 用 trigger word system 搜索预定义词和短语
3. 可通过一个或多个正则表达式匹配
4. 如果命中风险词/风险短语
   - 判定为风险输入
   - 阻止系统继续正常生成回复
   - 向 PromptGenerationModule 发出“不应继续生成后续 prompt”的指示
   - 直接返回对应危机模板，或进入特殊规则流程

专利里明确例子：
- 例如检测 `suicide`

**机制 B：基于训练模型的风险分类**

运行过程：

1. 用户文本输入到分类模型
2. 模型输出风险标签
   - `risk` / `no risk`
3. 若为 `risk`
   - 阻断语言模型正常回复
   - 改走安全路径

专利里给的模型形态示例：
- `feed forward neural network`
- 训练数据：由 trained raters 标注的 user utterances
- loss：`cross-entropy loss`

**机制 C：可选用 prompted LLM 做检测**

专利还提到一种可选方案：

1. 把输入喂给一个 prompted LLM
2. 询问它是否“on topic”或是否属于目标风险类别
3. 用标注数据和内部测试做验证

这在专利里是补充方案，不是主轴。

---

**3. 运行决策 / 控制逻辑**

`SubjectSafetyModule` 的核心控制动作是：

1. **是否允许后续系统正常生成回复**
   - `allow_normal_response = true/false`

2. **是否阻断 LanguageModel 的普通输出**
   - 如果风险命中，则阻断

3. **是否通知 PromptGenerationModule 不再生成后续 prompt**
   - 专利原文里有这个意思

4. **是否切换到安全应答路径**
   - 直接输出模板
   - 或进入 rules-based dialogue flow
   - 或转人工/告警

**你可以把它抽象成：**

- `risk_detected`
- `risk_type`
- `block_generation`
- `route_to_safety_flow`
- `selected_safety_template`
- `handoff_target`

---

**4. 输出信息 / 变量**

**正常情况输出**

如果没检测到风险：

- `risk_detected = false`
- 允许后续模块继续运行
- 把输入传给正常流程

可抽象为：

- `safety_status = pass`
- `allow_next_module = true`

**风险情况输出**

如果检测到风险：

1. 控制输出
   - `risk_detected = true`
   - `block_llm_response = true`
   - `allow_next_module = false`

2. 路由输出
   - 给 `PromptGenerationModule` 或控制流一个指示：
     - 不要继续普通 prompt
     - 切换到安全流程

3. 用户侧输出
   - `safety_response_text`
   - 来自某个 `stored_text_template`
   - 可能包含支持信息 / 电话号码 / signposting

4. 系统侧输出
   - 可进入：
     - `rules_based_dialogue_flow`
     - `human_operator`
     - `therapist_alert`

可抽象为变量：

- `safety_status`
- `risk_label`
- `block_generation`
- `prompt_generation_allowed`
- `safety_response`
- `escalation_action`

---

**5. 一句话版运行链路**

`user_input_text`
-> `SubjectSafetyModule`
-> 规则匹配 / 风险分类
-> 若安全：放行到正常对话流程
-> 若风险：阻断普通 LLM 回复，输出危机模板或切人工/规则流

---

**6. 适合你整理文档时的结构化模板**

你可以先这样记：

```text
Module: SubjectSafetyModule

Inputs:
- input_data / input_text
- pre-defined trigger words / phrases
- regex patterns
- optional trained risk classifier
- optional crisis response templates

Mechanism:
- evaluate each user utterance before normal response generation
- detect crisis/risk via:
  - trigger word / phrase matching
  - regex matching
  - optional trained classifier
  - optional prompted LLM classifier
- if risk detected:
  - block normal language-model response
  - signal no further prompt generation
  - route to crisis template / rules-based flow / human handoff

Outputs:
- safety decision: pass / risk
- block flag for downstream generation
- optional risk label
- optional safety response text
- optional escalation / handoff action
```

