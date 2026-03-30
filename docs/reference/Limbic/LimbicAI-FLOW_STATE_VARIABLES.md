# 流程各阶段输入/输出变量详细映射

## 概述

本文档详细列出 LimbicAI 对话系统 4 阶段（52a-52d）+ understanding + recommendation 各阶段的输入变量、输出变量及其作用，以及关键流转判断条件。

流程本质：通过**模型结构化输出字段**（intent, explore, formulation_confirmed, needs_more_exploration, intervention_complete）+ **本地状态路由**驱动，无单纯关键字触发，全是**字段值 + 条件判断**的级联。

---

## 阶段 1：`52a`（初步探索）

### 📥 输入（从 `PatentGraphState`）

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `user_text` | str | 用户输入 | 当前用户消息 |
| `history` | str | 累积 | 对话历史（human↔assistant） |
| `goal` | str \| None | session 初始化 | 用户长期治疗目标 |

### 📤 输出（写入 `PatentGraphState`）

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `assistant_text` | Phase52AResult | str | Limbic 回复 |
| `intent` | Phase52AResult | bool | 用户表达明确干预意愿 |
| `explore` | Phase52AResult | bool | 发现重大心理问题值深入 |
| `finished` | Phase52AResult | bool | 对话自然结束（5+ 轮无实质） |
| `conversation_phase` | route决策 | str | 下一阶段（52a/52b/52d/output_safety） |
| `flow_next_node` | route决策 | str | 路由目标node |
| `chosen_intervention` | resolve_direct_intent | str \| None | （仅 intent=True）直达干预名 |
| `selection_source` | resolve条件 | str \| None | direct_intent / user_choice |
| `transition_reason` | FlowDecisionEnvelope | str | intent_detected/explore_detected/... |
| `last_prompt_generator` | constant | str | "52a" |

### 路由决策

```python
route_after_52a_result(intent, explore, finished) -> FlowDecisionEnvelope:
  - intent=True       → 52d（chosen_intervention 由 resolve_direct_intent 填充）
  - explore=True      → 52b（开始 CBT 5-area 收集）
  - finished=True     → output_safety（对话自然结束）
  - 其他              → 52a（继续探索，经 output_safety 中转）
```

---

## 阶段 2：`52b`（CBT 5-Area 结构化）

### 📥 输入

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `user_text` | str | 用户输入 | 回答 5-area 问题或补充 |
| `history` | str | 累积 | 52b 或循环回来的对话 |
| `asking` | Literal[...] \| None | 上一轮 state | 当前在问什么：Situation/Feeling/Thought/Other/Formulation |

### 📤 输出

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `assistant_text` | Phase52BResult | str | 提问或 formulation 总结 |
| `asking` | Phase52BResult | str \| None | Situation/Feeling/Thought/Other/Formulation/null |
| `finished` | Phase52BResult | bool | **完成本阶段** |
| `formulation_summary` | Phase52BResult | str \| None | CBT formulation 文本（状态→情绪→行为链） |
| `formulation_confirmed` | Phase52BResult | bool \| None | 用户确认 formulation（True=已确认） |
| `conversation_phase` | 条件 | str | 52c（formulation_confirmed=True）否则保持 52b |
| `structured_information_ready` | 条件 | bool | True 仅当 finished∧confirmed |
| `flow_next_node` | route决策 | str | understanding / output_safety |
| `transition_reason` | route决策 | str | formulation_confirmed / awaiting_more_structure |
| `last_prompt_generator` | const | str | "52b" |

### 流程细节

**52b 的行为分两个阶段：**

1. **收集阶段**（asking: Situation/Feeling/Thought/Other）
   - formulation_summary: null
   - formulation_confirmed: null
   
2. **确认阶段**（asking: Formulation）
   - formulation_summary: 已生成总结
   - formulation_confirmed: false（等待用户确认

### 路由决策

```python
route_after_52b_result(formulation_confirmed) -> FlowDecisionEnvelope:
  - formulation_confirmed=True  → understanding（进入主体理解）
  - 其他                        → 52b（继续收集或重新确认，经 output_safety 中转）
```

---

## 阶段 3：`understanding`（主体理解 - 第 31 模块）

### 📥 输入

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `structured_items` | list[dict] | 累积 | 52b 收集的 Q&A 对，每项含 asking_label、assistant_question、user_answer |
| `recommendation_context` | dict | state/知识库 | 治疗目标、历史干预、治疗计划等上下文 |

**structured_items 结构：**
```json
[
  {
    "asking_label": "Situation|Feeling|Thought|Other|Formulation",
    "assistant_question_text": "提问内容",
    "user_answer_text": "用户答复"
  }
]
```

### 📤 输出

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `subject_profile` | SubjectUnderstandingResult | dict | CBT 构念证据：包含 detected_states、evidence（思维/情绪/情况）、underlying_beliefs、avoidance_patterns、maintaining_factors 等 |
| `last_prompt_generator` | constant | str | "understanding" |
| `conversation_phase` | 固定 | str | "recommendation"（无分叉） |

**subject_profile 关键字段：**
- `detected_states`: list[str] — ["distorted_thought", "negative_sentiment", "negative_activity", ...]
- `evidence`: dict — { "situation": "...", "feeling": "...", "thought": "..." }
- `underlying_beliefs`: list[str] — 潜在信念
- `avoidance_patterns`: list[str] — 回避模式
- `maintaining_factors`: list[str] — 维持因素

---

## 阶段 4：`recommendation`（干预推荐 - 第 32 模块）

### 📥 输入

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `subject_profile` | dict | understanding 输出 | 含检测到的 CBT 状态、证据、信念等 |
| `structured_items` | list[dict] | 累积 | 结构化信息（5-area Q&A） |
| `recommendation_context` | dict | 知识库 | 目标文本、历史干预、治疗计划 |

### 📤 输出

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `recommendation` | build_recommendation(...) | dict | 含 ranked_interventions、mapped_interventions、needs_more_exploration 等字段 |
| `needs_more_exploration` | recommendation | bool | **关键判断**：信息不足则 True |
| `conversation_phase` | 条件 | str | 52c（needs_more=False）或 52b（=True，循环） |
| `chosen_intervention` | recommendation[0] | str | 推荐的一阶干预（cognitive_restructuring / five_areas_model） |
| `recommendation_loop` | 条件 | bool | True 表示循环回 52b 再问 |
| `flow_next_node` | route决策 | str | 52c / output_safety |
| `asking` | loopback计算 | str \| None | （循环回 52b 时）继续问什么标签 |
| `assistant_text` | loopback_message | str | （循环回时）提示需更多信息的回复 |
| `transition_reason` | route决策 | str | recommendation_ready / needs_more_exploration |
| `last_prompt_generator` | constant | str | "recommendation" |

### 流程细节

**当 needs_more_exploration=True 时：**
- 计算 `loopback_asking_label` — 询问哪个 5-area 维度
- 生成 `loopback_message` — 提示继续对话的自然语言
- 回到 52b（conversation_phase: "52b"）继续收集

**当 needs_more_exploration=False 时：**
- 直接进入 52c（conversation_phase: "52c"）
- 提取 recommendation.mapped_interventions[0] 作为 chosen_intervention

---

## 阶段 5：`52c`（干预选择）

### 📥 输入

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `recommendation` | dict | recommendation 输出 | ranked/mapped interventions，用于展示选项 |
| `goal` / `therapy_goal` | str \| None | session | 长期目标 |
| `history` | str | 累积 | 对话上下文 |
| `user_text` | str | 用户 | 对干预选项的反应 |
| `subject_profile` | dict | understanding | CBT profile（含证据、信念） |
| `subject_profile_summary` | str | _subject_profile_summary(...) | 概括版 CBT profile |
| （可选）`knowledge_bank_guidance` | list[str] | 知识库 | 阐释选项的指导文本 |
| （可选）`candidate_explanations` | list[str] | 知识库 | 每个干预候选的解释 |
| （可选）`why_now_rationale` | list[str] | 知识库 | 为什么现在推荐这些干预 |
| （可选）`patient_tailored_hints` | list[str] | 知识库 | 个性化措辞提示 |

### 📤 输出

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `response` | Phase52CResult | str | 提议干预选项的人性化说法 |
| `finished` | Phase52CResult | str | "True"/"False"（**字符串类型**，注意！） |
| `chosen_intervention` | Phase52CResult | str | Cognitive Restructuring / 5 Areas Model / "" |
| `conversation_phase` | 条件 | str | 52d（finished∧chosen）/ 52c（loop）/ 52a（re-eval） |
| `flow_next_node` | route | str | 52d / output_safety / 52c |
| `transition_reason` | route | str | intervention_chosen / continue_choice_discussion / choice_state_updated |
| `last_prompt_generator` | const | str | "52c" |

### Path 决策

```python
if finished=True && chosen_intervention:
  → 52d（conversation_phase: "52d"）
elif not finished && not chosen:
  → 52c or 52a（re-eval 之前阶段）
else:
  → 52c（loop）
```

---

## 阶段 6：`52d`（干预执行）

### 📥 输入

| 变量 | 类型 | 来自 | 说明 |
|------|------|------|------|
| `chosen_intervention` | str | 52c 或 52a direct_intent | Cognitive Restructuring / Five Areas Model |
| `intervention` | str | INTERVENTION_TEXT map | 干预的详细步骤/描述（注入 prompt） |
| `history` | str | 累积 | 对话上下文 |
| `user_text` | str | 用户 | 对干预步骤的响应 |
| `subject_profile_summary` | str \| None | _subject_profile_summary(...) | CBT 概括（patterns、beliefs） |
| （可选）`knowledge_bank_guidance` | list[str] | 知识库 | 阐释干预的指导 |
| （可选）`delivery_guidance` | list[str] | 知识库 | 如何交付该干预 |
| （可选）`step_constraints` | list[str] | 知识库 | 步骤/进度约束 |
| （可选）`adaptation_notes` | list[str] | 知识库 | 针对患者上下文的适配备注 |

### 📤 输出

| 变量 | 来自结果 | 类型 | 说明 |
|------|---------|------|------|
| `response` | Phase52DResult | str | 干预步骤对话（自然语言） |
| `intervention_complete` | Phase52DResult | bool | 干预完成 |
| `completion_reason` | Phase52DResult | str \| None | 完成原因说明 |
| `conversation_phase` | 条件 | str | 52a（intervention_over=True）否则保持 52d |
| `intervention_over` | 计算 | bool | intervention_complete ∣ "INTERVENTION_OVER" in response |
| `assistant_text` | cleaned response | str | 移除 INTERVENTION_OVER 标记的回复 |
| `chosen_intervention` | 继承 | str | 保持当前干预 |
| `last_prompt_generator` | const | str | "52d" |
| `transition_reason` | 条件 | str | intervention_completed / intervention_in_progress |

### 完成判定

```python
intervention_over = result.intervention_complete or "INTERVENTION_OVER" in result.response

if intervention_over:
  → conversation_phase: "52a"（返回初探，继续新对话）
else:
  → conversation_phase: "52d"（继续当前干预）
```

---

## 🔄 关键流转中的状态变化

### 核心流转矩阵

| 当前阶段 | 驱动条件 | 下一阶段 | 输出关键变量 |
|---------|--------|--------|------------|
| 52a | intent=True | 52d | chosen_intervention, selection_source |
| 52a | explore=True | 52b | asking=Situation/Other |
| 52a | finished=True | output_safety | - |
| 52a | 其他循环 | 52a | flow_next_node="output_safety" |
| 52b | formulation_confirmed=True && finished=True | understanding | structured_information_ready=True |
| 52b | 其他循环 | 52b | flow_next_node="output_safety" |
| understanding | （固定） | recommendation | subject_profile |
| recommendation | needs_more_exploration=False | 52c | chosen_intervention=mapped_interventions[0] |
| recommendation | needs_more_exploration=True | 52b（循环） | recommendation_loop=True, asking=loopback_label |
| 52c | finished=True && chosen | 52d | conversation_phase="52d" |
| 52c | not finished ∣∣ not chosen | 52c/52a（re-eval） | flow_next_node="output_safety" |
| 52d | intervention_over=True | 52a | conversation_phase="52a" |
| 52d | intervention_over=False | 52d（loop） | flow_next_node="52d" |

---

## 📊 流程拓扑图（纯文本）

```
START
  ↓
input_safety
  ├─ crisis → END
  └─ normal → 52a
  
52a [intent, explore, finished]
  ├─ intent=True → 52d
  ├─ explore=True → 52b
  ├─ finished=True → output_safety → END
  └─ else → output_safety → 52a (loop)

52b [asking, formulation_confirmed, finished]
  ├─ formulation_confirmed=True && finished → understanding
  └─ else → output_safety → 52b (loop)

understanding [structured_items]
  ↓ (fixed)
recommendation [needs_more_exploration]
  ├─ needs_more_exploration=False → 52c
  └─ needs_more_exploration=True → 52b (循环回)

52c [chosen_intervention, finished]
  ├─ finished && chosen → 52d
  ├─ not finished/chosen → output_safety → 52c (loop) or 52a (re-eval)

52d [intervention_complete/INTERVENTION_OVER]
  ├─ intervention_over=True → 52a (continue session)
  └─ intervention_over=False → 52d (loop)

output_safety (universal exit point)
  ↓
END
```

---

## 🧠 核心架构设计

### 状态机驱动原理

1. **LLM 结构化输出驱动** — 模型返回固定 Pydantic schema（Phase52AResult 等）
2. **本地决策路由** — route_after_52a_result(...) 等函数基于这些字段做条件分叉
3. **没有单纯字符串关键字触发** — 所有流转基于布尔/枚举字段+逻辑判断
4. **知识库注入补强** — first_module 可在 52c/52d 阶段注入 candidate_explanations、delivery_guidance 等

### 关键补充：Direct Intent（快捷路径）

当 52a 模型输出 `intent=True` 时：
- 调用 `resolve_direct_intent(user_text, fallback_choice="cognitive_restructuring")`
- 扫描 `DIRECT_INTENT_NAME_MAP`：
  - "认知重建" / "cognitive restructuring" → cognitive_restructuring
  - "5 areas" / "5 areas model" → five_areas_model
  - 未命中 → fallback = "cognitive_restructuring"
- 结果写入 `chosen_intervention`，跳过推荐（52c）直奔 52d

---

## 📝 变量初始化与累积

### session 初始化

```python
# PatentGraphState 的初值
state = {
    "session_id": uuid4().hex,
    "user_text": "",
    "history": "",
    "goal": user_goal,  # 从 create_session 传入
    "conversation_phase": "52a",
    "structured_items": [],       # 累积
    "subject_profile": None,      # understaning 填充
    "recommendation": None,       # recommendation 填充
    # ... 其他字段
}
```

### 历史累积

`history` 字符串按 turn 通过 `InteractionModule56Service.orchestrate_user_turn` 不断拼接，格式通常为：
```
Assistant: 上轮回复
User: 用户输入
```

---

## 总结要点

✅ **无单纯关键字驱动** — 所有流转基于模型字段 + 本地逻辑
✅ **两层决策机制** — LLM 输出 + 规则路由（route_after_52* 函数）
✅ **支持循环与重评估** — 52b ↔ recommendation ↔ 52b，52c self-loop，52d self-loop
✅ **知识库可选注入** — 52b/52c/52d 阶段可补充 knowledge_bank 上下文
✅ **安全检查点** — output_safety 是通用出口，每轮对话都会经过
