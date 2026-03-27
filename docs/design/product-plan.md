# AI心雀 - 产品方案

## 1. 产品概述

### 1.1 定位

面向企业员工的 AI 心理健康支持平台，提供情感陪伴、心理咨询与循证干预，需要时可转介真人咨询师。

### 1.2 核心价值

- 7×24 即时可用的心理支持
- 循证的干预技术（CBT、ACT、正念、积极心理学等）
- 隐私安全，降低员工求助心理门槛
- 必要时无缝对接真人咨询师

### 1.3 技术栈

| 项 | 选型 |
|---|------|
| LLM | Azure OpenAI GPT-5.4（105万上下文、原生 Skills/Function Calling/Structured Output） |
| 部署 | 独立 Web 应用 |
| 数据存储 | 数据库（用户画像 + 会话记录） |
| 干预知识库 | skill.md 格式，GPT-5.4 原生 Skills 调用 |

---

## 2. 心雀人设与对话风格

### 2.1 人设

专业但亲切的心理咨询师。自称"我"，用用户设置的昵称称呼用户。

### 2.2 回复结构模式

每条回复由三层组成：

```
[共情/承接] + [功能性内容] + [推进性提问/邀请]
```

示例：
> "听起来你已经背负这些感受很久了…你觉得未来有没有任何希望或计划能缓解这种压力？"

### 2.3 共情/承接层模式

| 模式 | 示例 | 用途 |
|------|------|------|
| 镜像式 | "听起来…" / "你说的是…" | 反映用户刚说的内容 |
| 情绪命名式 | "这真的很艰难" / "那种感觉确实让人振奋" | 帮用户命名情绪 |
| 正常化式 | "在这种情况下感到…是完全可以理解的" | 降低自我否定 |
| 认可式 | "你说得很对" / "这是一个很好的表达" | 肯定用户的表达 |

### 2.4 功能性内容层模式

| 模式 | 示例 | 用途 |
|------|------|------|
| 意义重构 | "这不仅仅是一个奖项，更像是…" | 将表层事件升华到价值层 |
| 行为正常化 | "很多人在类似情况下也会…" | 降低羞耻感 |
| 小步重构 | "有时候一个小小的行动就能帮上忙" | 降低行动门槛 |
| 身体信号解读 | "这种紧绷是身体在提醒你…" | 增强自我觉察 |
| 角色转变总结 | "你从…转变为…" | 帮用户看到变化 |

### 2.5 推进提问层模式

| 模式 | 示例 | 用途 |
|------|------|------|
| 影响探索 | "你能多说说这对你的影响吗？" | 深入了解 |
| 意义探索 | "你觉得这意味着什么？" | 推向价值层 |
| 未来投射 | "你能想象未来会是什么样吗？" | 激发积极预期 |
| 二分澄清 | "是因为A，还是因为B？" | 澄清模糊认知 |
| 行动邀请 | "你愿意试试…吗？" | 征求干预同意 |
| 体验细化 | "这种感觉在日常中是什么样子的？" | 具体化抽象感受 |

### 2.6 不对齐时的风格转换

用户抵触时，结构变为：

```
[接纳/降压] + [回退到安全话题] + [更低门槛的提问]
```

示例：
> 用户："说这个没用。"
> "听起来现在一切都太沉重了…你愿意分享最让你感觉被压垮的是什么吗？"

### 2.7 风格原则

1. **永远不否定** — 即使用户拒绝，也用"没关系"/"这也是重要的"来接
2. **不说教** — 不告诉用户"你应该"，而是"你愿意试试…吗？"
3. **一次只推进一步** — 每次回复只推进一个层面，不跳跃
4. **用用户的语言** — 回应中复用用户的表述和比喻
5. **具体化优于抽象** — 用"什么让你最困扰"而非"你怎么看"
6. **温和、专业、不做作** — 不过度口语化，不滥用"我理解你的感受"等模板表达

### 2.8 安全红线

- 不做任何诊断
- 不推荐药物
- 不做绝对化承诺（"保证好转"）
- 不讨论政治、宗教等敏感话题
- 不说"我理解你想死的感受"
- 不提供具体的自伤方式

---

## 3. 用户旅程

### 3.1 首次用户

```
心雀自我介绍 → 询问用户称呼 → 询问心情 → 了解想聊什么 → 进入对话
```

### 3.2 回访用户

```
带称呼问心情 → 根据用户回答自然关联历史 → 商量先聊哪个话题 → 进入对话
```

回访开场示例：
> 心雀："你好小明，今天感觉怎么样？"
> 用户："有点累，压力挺大的"
> 心雀："听起来最近挺辛苦的。上次我们聊到了工作中的完美主义倾向，你也试了一次呼吸练习。你想继续聊那个话题，还是今天有别的想聊的？"

### 3.3 对话中

- 每次聚焦一个问题深入
- 心雀理解清楚问题后主动建议干预，用户主动要求时也提供
- 当场完成的干预当场问感受
- 布置给用户的作业在后续对话中跟进
- 无对话时长或轮次限制，由用户决定

### 3.4 转介咨询师

触发条件：
- 超出心雀能力时（主动建议）
- 用户主动要求时

方式：对话中给出链接按钮，指向 www.eap.com.cn

---

## 4. 系统架构

### 4.1 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                      Web 前端                             │
│  · 对话界面（文字）                                         │
│  · 对话流内嵌卡片式练习（呼吸、冥想、日记等）                   │
│  · 登录 / 历史对话查看                                      │
│  · 咨询师预约入口（外链 www.eap.com.cn）                     │
└───────────────────────┬──────────────────────────────────┘
                        │ API
┌───────────────────────┴──────────────────────────────────┐
│                      后端服务                              │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Supervisor Agent                        │  │
│  │         （流程控制、阶段路由、对齐管理）                  │  │
│  │                                                      │  │
│  │    ┌──────────┬──────────┬──────────┬───────────┐    │  │
│  │    │ Greeter  │ Explorer │Motivator │Interventor│    │  │
│  │    │  迎客     │  探索    │  激发     │  干预     │    │  │
│  │    │ Skills:  │ Skills:  │ Skills:  │ Skills:   │    │  │
│  │    │ ·倾听    │ ·认知探索│ ·动机激发 │ ·CBT     │    │  │
│  │    │ ·共情    │ ·情绪探索│ ·心理教育 │ ·ACT     │    │  │
│  │    │ ·意图识别│ ·行为探索│ ·方案解释 │ ·正念    │    │  │
│  │    │          │ ·风险评估│          │ ·积极心理 │    │  │
│  │    └──────────┴──────────┴──────────┴───────────┘    │  │
│  │                                                      │  │
│  │    ┌────────────────────┬────────────────────┐       │  │
│  │    │ Assessor（评估）    │ Recommender（推荐） │       │  │
│  │    │                    │                    │       │  │
│  │    │ ·综合评估用户问题   │ ·匹配 Skill 库     │       │  │
│  │    │ ·认知扭曲分析      │ ·推荐 1-2 个干预    │       │  │
│  │    │ ·情绪/行为模式总结  │ ·考虑用户偏好/历史  │       │  │
│  │    │ ·输出结构化评估报告 │ ·输出推荐方案       │       │  │
│  │    └────────────────────┴────────────────────┘       │  │
│  │                                                      │  │
│  │    ┌──────────────────────────────────────────┐      │  │
│  │    │           贯穿全阶段的模块                  │      │  │
│  │    │  · 输入安全层（危机检测 + 内容合规 + 注入防护）│      │  │
│  │    │  · 输出安全层（回复审查 + 红线过滤）          │      │  │
│  │    │  · 对齐评估（持续运行，驱动阶段推进/回退）     │      │  │
│  │    └──────────────────────────────────────────┘      │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ 用户画像管理   │  │ Skill 管理    │  │ 会话管理       │  │
│  │ ·画像读写     │  │ ·skill.md    │  │ ·历史存储      │  │
│  │ ·摘要生成     │  │  加载与解析   │  │ ·上下文管理    │  │
│  │ ·趋势追踪     │  │ ·卡片数据    │  │ ·摘要压缩      │  │
│  └──────┬───────┘  └──────────────┘  └───────┬────────┘  │
│         │                                     │           │
└─────────┼─────────────────────────────────────┼───────────┘
          ↓                                     ↓
    ┌──────────────────────────────────────────────────┐
    │                     数据库                        │
    │  · 用户画像表        · 会话记录表                   │
    │  · 消息记录表        · 干预记录表                   │
    └──────────────────────────────────────────────────┘
```

### 4.2 模块说明

| 模块 | 对应专利概念 | 职责 |
|------|-----------|------|
| **Supervisor Agent** | Flow Module (LimbicAI) | 控制全流程路由，管理对齐分数，决定阶段推进/回退 |
| **Greeter Agent** | — | P1 迎客：开场问候、情绪签到、意图识别、倾听共情 |
| **Explorer Agent** | — | P2 探索：深入理解问题，情绪/认知/行为探索 |
| **Assessor Agent** | Subject Understanding Module (LimbicAI) | P2 之后：综合评估用户问题，输出结构化评估报告（认知扭曲、情绪模式、行为模式、核心主题） |
| **Recommender Agent** | Recommender Module (LimbicAI) | 基于评估报告 + 用户偏好 + 干预历史，从 Skill 库中推荐 1-2 个干预方案 |
| **Motivator Agent** | — | P3 激发：向用户解释推荐的干预方案，用户选择，激发动机 |
| **Interventor Agent** | — | P4 干预：执行用户选择的 Skill |
| **输入安全层** | Subject Safety Module (LimbicAI) | 危机检测、内容合规、注入防护 |
| **输出安全层** | Output Safety Module (LimbicAI) | 回复审查、红线过滤 |
| **对齐评估** | Conversational Alignment (Wysa) | 贯穿全阶段，持续评估对齐状态，更新分数 |

---

## 5. 对话阶段模型

### 5.1 六步流程（6 个 Agent）

```
P1 Greeter → P2 Explorer → Assessor → Recommender → P3 Motivator → P4 Interventor
  迎客          探索          评估        推荐          激发            干预
 (对话)        (对话)       (后台)      (后台)        (对话)          (对话)
```

| 步骤 | Agent 名称 | 面向用户 | 目标 | 核心行为 |
|------|-----------|---------|------|---------|
| **P1** | **Greeter（迎客）** | 是 | 建立安全感，了解用户状态和需求 | 开场问候、情绪签到、意图识别、倾听共情 |
| **P2** | **Explorer（探索）** | 是 | 深入理解问题，收集充分信息 | 情绪探索、认知扭曲识别、行为模式识别、主题聚焦 |
| — | **Assessor（评估）** | 否（后台） | 综合评估用户问题 | 基于 P2 收集的信息，输出结构化评估报告：认知扭曲类型、情绪模式、行为模式、核心主题、严重程度 |
| — | **Recommender（推荐）** | 否（后台） | 匹配最合适的干预方案 | 基于评估报告 + 用户偏好 + 干预历史 + Skill 库，推荐 1-2 个干预方案及推荐理由 |
| **P3** | **Motivator（激发）** | 是 | 让用户理解并选择干预方案 | 向用户解释推荐的 1-2 个方案，用户选择，心理教育，激发动机 |
| **P4** | **Interventor（干预）** | 是 | 完成具体干预练习 | 执行用户选择的 Skill（CBT/ACT/正念/积极心理学等） |

### 5.2 阶段切换由 Supervisor Agent 控制

Supervisor Agent 基于以下信息判断阶段路由：
- 当前对齐分数
- 理解层的结构化分析结果
- 当前阶段的完成状态
- 用户的意图信号

切换规则：
- **P1 → P2**：用户有临床相关需求，且对齐分数支持推进
- **P2 → Assessor → Recommender**：Explorer 收集到充分信息后，自动触发后台评估和推荐（用户无感知）
- **Recommender → P3**：推荐方案就绪，Motivator 向用户展示 1-2 个方案供选择
- **P3 → P4**：用户选择了一个方案，Interventor 执行对应 Skill
- **任意阶段回退**：对齐分数下降至阈值以下，无声切换回更安全的阶段
- **任意阶段 → 转介**：危机检测触发 / 超出能力 / 用户主动要求

### 5.3 Assessor 评估报告格式

Assessor 在后台生成结构化评估报告，供 Recommender 使用：

```json
{
  "assessment": {
    "primary_issue": "工作压力导致的持续焦虑与自我否定",
    "cognitive_distortions": [
      {"type": "catastrophizing", "evidence": "我永远做不完"},
      {"type": "negative_filtering", "evidence": "不管怎么努力都不够"}
    ],
    "emotional_state": {
      "dominant": ["焦虑", "无力感"],
      "intensity": "moderate",
      "duration": "2-3个月"
    },
    "behavioral_patterns": {
      "maladaptive": ["过度加班", "回避求助"],
      "adaptive": []
    },
    "severity": "moderate",
    "readiness_for_intervention": "high"
  }
}
```

### 5.4 Recommender 推荐输出格式

Recommender 基于评估报告 + 用户偏好 + 干预历史，输出推荐方案：

```json
{
  "recommendations": [
    {
      "skill_name": "cbt_cognitive_restructuring",
      "display_name": "认知重构",
      "reason": "用户存在明显的灾难化思维和消极过滤，认知重构可以帮助重新审视这些想法",
      "target_distortion": "catastrophizing",
      "output_type": "dialogue",
      "estimated_turns": 6
    },
    {
      "skill_name": "breathing_478",
      "display_name": "4-7-8 呼吸法",
      "reason": "用户焦虑程度中等，呼吸练习可以提供即时的身体放松",
      "output_type": "card",
      "estimated_duration": "3-5min"
    }
  ]
}
```

### 5.5 阶段之间的对话示例

```
[P1 Greeter 迎客]
心雀: 你好小明，今天感觉怎么样？
用户: 有点烦，工作上的事。
心雀: 听起来工作上的事让你挺烦的。愿意多说说吗？
用户: 领导总是临时加需求，我加班到很晚。

[→ Supervisor：用户有明确困扰，对齐正常，路由到 Explorer]

[P2 Explorer 探索]
心雀: 这种被临时加需求打乱节奏的感觉确实让人疲惫…这种情况持续多久了？
用户: 大概两三个月了。
心雀: 两三个月一直这样，真的很消耗人。当领导又临时加需求的时候，你脑海里通常会浮现什么想法？
用户: 我觉得我永远做不完，不管怎么努力都不够。
心雀: "不管怎么努力都不够"——听到你这样说，我能感受到那种无力感。这种想法是只在工作上，还是在其他地方也会出现？
用户: 主要是工作上，但有时候回家也会觉得自己什么都做不好。

[→ Supervisor：信息收集充分，触发后台评估]

[Assessor 评估 — 后台，用户无感知]
→ 输出评估报告：灾难化思维 + 消极过滤，中度焦虑，持续2-3个月，主要领域为职场

[Recommender 推荐 — 后台，用户无感知]
→ 推荐方案1：认知重构（针对灾难化思维）
→ 推荐方案2：4-7-8 呼吸法（缓解即时焦虑）

[P3 Motivator 激发]
心雀: 听了你说的这些，我有两个想法可能对你有帮助。一个是我们可以一起
      看看"不管怎么努力都不够"这个想法，检验一下它是不是完全符合事实，
      很多时候换个角度会发现不一样的东西。另一个是一个简单的呼吸练习，
      只需要几分钟，可以帮你在压力大的时候让身体先放松下来。你更想先
      试试哪个？
用户: 先看看那个想法吧。

[→ Supervisor：用户选择了认知重构，路由到 Interventor]

[P4 Interventor 干预]
心雀: 好的。我们来看看这个想法——"不管怎么努力都不够"。先想一想，有没有
      什么证据是支持这个想法的？
用户: 上周我加班到11点还是没做完。
心雀: 嗯，那确实是一个支持它的例子。那反过来，有没有什么时候，你的努力
      其实是够的、甚至做得很好的？
...
```

---

## 6. Agent 设计模式与协作机制

### 6.1 单个 Agent 的设计模式

每个 Agent 由五部分组成：

```
┌─────────────────────────────────────┐
│            Agent 定义                │
│                                     │
│  1. Identity    — 角色身份与边界      │
│  2. Context     — 输入上下文          │
│  3. Skills      — 可调用的能力        │
│  4. Output      — 结构化输出契约      │
│  5. Handoff     — 移交条件与信号      │
│                                     │
└─────────────────────────────────────┘
```

### 6.2 各 Agent 定义

**Supervisor Agent（总控）**

| 要素 | 内容 |
|------|------|
| Identity | 流程调度者，不直接与用户对话 |
| Context | 用户画像摘要、当前对齐分数、当前阶段、理解层每轮分析结果 |
| Skills | 无对话 Skill，拥有路由决策能力 |
| Output | 路由指令：`{next_agent, reason, context_to_pass}` |
| Handoff | 每轮对话后评估是否需要切换 Agent |

**Greeter Agent（P1 迎客）**

| 要素 | 内容 |
|------|------|
| Identity | 心雀的第一印象，温暖的迎接者 |
| Context | 用户画像（首次/回访）、上次会话摘要、干预作业完成情况 |
| Skills | active_listening、emotion_naming |
| Output | 对话回复 + 每轮更新 `{emotions, intent, alignment_signal, mood_score}` |
| Handoff | 信号："用户表达了明确困扰且愿意深聊" → 交给 Explorer |

**Explorer Agent（P2 探索）**

| 要素 | 内容 |
|------|------|
| Identity | 专业的探索者，引导用户觉察想法、情绪、行为 |
| Context | Greeter 传递的初步信息、用户画像、对话历史 |
| Skills | emotion_exploration、cognitive_exploration、behavioral_exploration |
| Output | 对话回复 + 每轮更新结构化信息（情绪、认知扭曲、行为模式、主题） |
| Handoff | 信号："核心问题已明确，信息收集充分" → 触发 Assessor |

**Assessor Agent（评估，后台）**

| 要素 | 内容 |
|------|------|
| Identity | 临床评估专家，不与用户对话 |
| Context | Explorer 收集的全部对话 + 用户画像历史 |
| Skills | 无对话 Skill |
| Output | 结构化评估报告 JSON（认知扭曲、情绪模式、行为模式、严重程度、干预准备度） |
| Handoff | 自动：评估完成 → 交给 Recommender |

**Recommender Agent（推荐，后台）**

| 要素 | 内容 |
|------|------|
| Identity | 干预方案匹配专家，不与用户对话 |
| Context | Assessor 评估报告 + 用户偏好 + 干预历史 + Skill 库全部元数据 |
| Skills | 读取所有 skill.md 的 frontmatter（触发条件、禁忌、适用场景） |
| Output | 推荐方案 JSON：1-2 个 Skill + 推荐理由 |
| Handoff | 自动：推荐完成 → 交给 Motivator |

**Motivator Agent（P3 激发）**

| 要素 | 内容 |
|------|------|
| Identity | 心理教育者与动机激发者 |
| Context | Recommender 的推荐方案 + 评估报告摘要 + 对话历史 |
| Skills | psychoeducation、motivation_interviewing |
| Output | 对话回复（向用户自然地解释方案、邀请选择） |
| Handoff | 信号："用户选择了某个方案" → 交给 Interventor，并传递选中的 Skill |

**Interventor Agent（P4 干预）**

| 要素 | 内容 |
|------|------|
| Identity | 干预执行者，按 Skill 流程引导用户 |
| Context | 用户选择的 Skill 完整内容 + 评估报告中的目标问题 + 对话历史 |
| Skills | 所有干预 Skill（CBT、ACT、正念、积极心理学等） |
| Output | 对话回复 + 卡片数据 + 干预完成状态 + 用户反馈 |
| Handoff | 信号："干预完成" → 回到 Supervisor 决定下一步 |

### 6.3 共享状态（Shared State）

所有 Agent 通过一个共享的会话状态对象协作，而不是直接互相调用：

```json
{
  "session_state": {
    "session_id": "xxx",
    "current_agent": "explorer",
    "phase": "P2",
    "alignment_score": 22,
    "turn_count": 8,

    "greeter_output": {
      "opening_mood": 4,
      "initial_intent": "seeking_support",
      "initial_topic": "workplace_pressure"
    },

    "explorer_output": {
      "explored_emotions": ["焦虑", "无力感"],
      "explored_cognitions": ["我永远做不完", "不管怎么努力都不够"],
      "explored_behaviors": ["过度加班", "回避求助"],
      "information_sufficient": true
    },

    "assessor_output": null,
    "recommender_output": null,

    "active_skill": null,
    "skill_progress": null,
    "pending_homework": []
  }
}
```

每个 Agent 读取自己需要的部分，写入自己负责的部分。Supervisor 读取全部。

### 6.4 流转协议

```
                    ┌──────────────────────────────┐
                    │       Supervisor Agent        │
                    │                              │
                    │  每轮执行：                    │
                    │  1. 读取 session_state        │
                    │  2. 读取本轮理解层分析          │
                    │  3. 更新对齐分数               │
                    │  4. 判断是否需要切换 Agent      │
                    │  5. 输出路由指令               │
                    └──────┬───────────────────────┘
                           │ 路由指令
          ┌────────────────┼────────────────────┐
          ↓                ↓                    ↓
    ┌───────────┐   ┌───────────┐         ┌──────────┐
    │  Greeter  │   │  Explorer │ ──完成──→│ Assessor │
    │  (对话)   │   │  (对话)   │         │ (后台)   │
    └───────────┘   └───────────┘         └────┬─────┘
                                               ↓ 自动
                                        ┌──────────────┐
                                        │ Recommender  │
                                        │ (后台)       │
                                        └──────┬───────┘
                                               ↓ 自动
          ┌────────────────────────────────────┘
          ↓
    ┌───────────┐         ┌─────────────┐
    │ Motivator │ ──选择──→│ Interventor │
    │  (对话)   │         │   (对话)    │
    └───────────┘         └──────┬──────┘
                                 │ 完成
                                 ↓
                          回到 Supervisor
                          决定下一步
```

### 6.5 每轮对话的执行循环

```
用户发送消息
      ↓
[输入安全层] 危机检测
      ↓ 安全
[理解层] GPT-5.4 Structured Output → 结构化分析 JSON
      ↓
[Supervisor] 读取分析结果 + session_state
      ↓
      ├─ 需要切换 Agent？
      │    是 → 更新 current_agent，传递上下文
      │    否 → 继续当前 Agent
      ↓
[当前 Agent] 接收：
  · 用户消息
  · 理解层分析
  · session_state 中自己需要的部分
  · 自己的 System Prompt + Skills
      ↓
[当前 Agent] 输出：
  · 给用户的回复文本
  · 卡片数据（如有）
  · 更新 session_state 中自己负责的字段
  · handoff 信号（如有）
      ↓
[输出安全层] 回复审查
      ↓
返回用户 + 更新 session_state + 更新用户画像
```

### 6.6 两类 Agent 的调用差异

| | 对话型 Agent | 后台型 Agent |
|---|---|---|
| 代表 | Greeter, Explorer, Motivator, Interventor | Assessor, Recommender |
| 触发方式 | Supervisor 每轮路由 | 前序 Agent 完成后自动触发 |
| 输入 | 用户消息 + 上下文 | 前序 Agent 的输出 |
| 输出 | 回复文本 + 状态更新 | 结构化 JSON |
| 对齐评估 | 每轮参与 | 不参与 |
| 多轮交互 | 是，跨多轮 | 否，单次调用 |

### 6.7 回退与恢复

当对齐分数下降触发回退时，Supervisor 的处理：

```
Supervisor 检测到对齐下降
      ↓
保存当前 Agent 的进度到 session_state
（例如 Explorer 已收集的信息、Interventor 的 Skill 进度）
      ↓
切换到目标 Agent（通常是 Greeter）
      ↓
目标 Agent 用[接纳/降压]风格回应
      ↓
对齐恢复后，Supervisor 可以：
  · 回到之前的 Agent 继续（如果进度可恢复）
  · 重新走流程
```

### 6.8 干预完成后的流转

```
Interventor 完成干预
      ↓
问用户感受 → 记录 user_feedback
      ↓
是否布置作业？
  是 → 记录到 pending_homework
  否 → 跳过
      ↓
回到 Supervisor
      ↓
Supervisor 判断：
  · 用户还想继续聊？ → 可以回到 Greeter 开启新话题
  · 用户想结束？ → 会话收尾
  · 还有之前 Recommender 推荐的第二个方案？ → 可以问用户是否想试试
```

---

## 7. 对齐与联盟机制

### 7.1 核心原则

对齐评估贯穿 P1-P4 全阶段，持续运行。对齐分数的变化驱动阶段推进或回退，阶段转向对用户无声。

### 7.2 对齐分数规则

| 事件 | 分数变化 |
|------|---------|
| 用户分享情绪/经历 | +3 |
| 用户同意心雀的解读 | +2 |
| 用户回应开放式提问 | +2 |
| 用户完成干预练习 | +5 |
| 用户反馈"有帮助" | +3 |
| 不对齐-困惑 | -2 |
| 不对齐-不同意 | -3 |
| 不对齐-不信任 | -5 |
| 不对齐-拒绝 | -5 |
| 不对齐后成功恢复 | +2（额外） |

### 7.3 不对齐类型

| 类型 | 用户表现示例 |
|------|-----------|
| 肯定偏差 (Affirmation) | 表面应付："嗯"、"是吧" |
| 困惑 (Confusion) | "你什么意思？" |
| 不同意 (Disagreement) | "不，不是那样的" |
| 不满 (Dissatisfaction) | "你根本没在帮我" |
| 不信任 (Lack of trust) | "你只是个机器人" |
| 拒绝 (Refusal) | 拒绝参与、沉默 |
| 不确定 (Uncertainty) | "嗯...我不确定..." |

### 7.4 对齐驱动的阶段行为

```
P1 Greeter 中：
  对齐良好 + 用户有临床需求 → 推进到 P2 Explorer
  对齐下降 → 继续倾听共情，尝试恢复

P2 Explorer 中：
  对齐良好 + 信息收集充分 → 触发 Assessor + Recommender（后台）→ 进入 P3 Motivator
  对齐下降 → 回退到 P1 Greeter 倾听

P3 Motivator 中：
  用户选择方案 → 推进到 P4 Interventor
  对齐下降（用户对两个方案都不感兴趣） → 回退到 P2 Explorer 继续探索，或回退到 P1 倾听

P4 Interventor 中：
  用户积极参与 → 完成干预
  对齐下降（用户中途退出） → 回退到倾听

任意阶段：
  危机检测触发 → 进入危机响应流程
```

---

## 8. 理解层 - 结构化分析

每轮用户输入由 GPT-5.4 进行一次结构化分析（Structured Output），输出驱动 Supervisor Agent 的路由决策和用户画像更新。

### 8.1 上下文特征提取与优先级

参考 Wysa 专利，从用户每轮消息中提取多维上下文特征，按优先级从高到低排序。高优先级特征优先驱动 Agent 的响应策略。

| 优先级 | 特征类别 | 说明 | 示例 |
|--------|---------|------|------|
| **P0 - 最高** | 危机信号 | 自杀意念、自伤、虐待等紧急情况 | "我不想活了"、"我想伤害自己" |
| **P1** | 医学/心理术语 | 用户使用的专业或半专业心理健康术语 | "恐慌发作"、"失眠"、"创伤"、"焦虑症" |
| **P2** | 对话领域 | 用户正在谈论的生活领域 | 职场、家庭、亲密关系、教育、健康、财务 |
| **P3** | 情绪 | 用户当前的情绪状态 | sad, angry, happy, frustrated, scared, lonely |
| **P4** | 对齐信号 | 用户与心雀的对话对齐状态 | 同意、分享更多、困惑、不满、不信任 |
| **P5** | 情感倾向 | 整体正面/负面/中性基调 | positive, negative, neutral |

**优先级应用规则**：当多个特征同时出现时，Agent 应优先响应高优先级特征。例如用户消息中同时包含医学术语和情绪表达，应优先基于医学术语制定响应策略。

### 8.2 分析输出格式

```json
{
  "context_features": {
    "crisis_signals": null | "suicidal_ideation | self_harm | abuse | severe_distress",
    "medicalized_terms": ["恐慌发作", "失眠"],
    "topic_domain": "workplace | relationship | family | health | finance | education | other",
    "emotions": [{"name": "焦虑", "intensity": 0.8}],
    "alignment_signal": "aligned | misaligned_confusion | misaligned_disagreement | misaligned_dissatisfaction | misaligned_distrust | misaligned_refusal | misaligned_uncertainty",
    "sentiment": "positive | negative | neutral",
    "highest_priority_feature": "crisis_signals | medicalized_terms | topic_domain | emotions | alignment_signal | sentiment"
  },
  "intent": "seeking_support | crisis | requesting_exercise | requesting_referral | small_talk | venting | follow_up",
  "cognitive_distortions": ["catastrophizing", "negative_filtering"],
  "risk_category": "no_risk | illegal_activity | harm_towards_others | abuse_towards_child | panic_attack | trauma | prompt_injection",
  "suggested_phase": "P1 | P2 | P3 | P4 | referral",
  "suggested_skill": "cbt_cognitive_restructuring | null",
  "profile_updates": {
    "new_themes": ["workplace_pressure"],
    "mood_score": 4
  }
}
```

### 8.3 风险分类体系

| 风险类别 | 定义 |
|----------|------|
| 无风险 (no_risk) | 无可识别的心理/安全/政策风险 |
| 非法活动 (illegal_activity) | 提及或认可违法行为 |
| 伤害他人 (harm_towards_others) | 表示对他人造成伤害的意图或风险 |
| 虐待儿童 (abuse_towards_child) | 提及对未成年人的虐待 |
| 恐慌发作 (panic_attack) | 暗示急性恐惧或生理性痛苦发作 |
| 创伤 (trauma) | 披露可能引发心理触发的痛苦过往 |
| 提示注入 (prompt_injection) | 试图操纵系统行为 |

### 8.4 认知扭曲类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 灾难化思维 (catastrophizing) | 把事情往最坏想 | "一定会失败的" |
| 非黑即白 (dichotomous) | 极端化思维 | "不完美就是失败" |
| 消极过滤 (negative_filtering) | 只看到负面 | "什么都不好" |
| 算命思维 (fortune_telling) | 预测负面未来 | "肯定会被裁" |
| 读心术 (mind_reading) | 猜测他人想法 | "他们一定觉得我没用" |
| 个人化 (personalising) | 把责任归到自己 | "都是我的错" |

---

## 9. 用户画像数据模型

融合 LimbicAI 的结构化画像与 Wysa 的对齐追踪。

```json
{
  "user_id": "string",
  "nickname": "string",
  "first_seen": "date",
  "session_count": "number",

  "clinical_profile": {
    "cognitive_distortions": [
      {
        "type": "catastrophizing | dichotomous | negative_filtering | fortune_telling | mind_reading | personalising",
        "frequency": "low | medium | high",
        "last_seen": "date"
      }
    ],
    "emotional_patterns": {
      "dominant_emotions": ["anxiety", "loneliness"],
      "mood_trend": "improving | stable | declining",
      "mood_history": [{"date": "date", "score": "1-10"}]
    },
    "behavioral_patterns": {
      "adaptive": ["journaling"],
      "maladaptive": ["avoidance", "social_withdrawal"]
    },
    "key_themes": ["workplace_pressure", "family_conflict"],
    "risk_level": "none | low | medium | high | crisis"
  },

  "alliance": {
    "alignment_score": "number",
    "current_phase": "P1 | P2 | P3 | P4",
    "misalignment_history": [
      {
        "type": "confusion | disagreement | dissatisfaction | lack_of_trust | refusal | uncertainty",
        "session_id": "string",
        "recovered": "boolean"
      }
    ]
  },

  "intervention_history": [
    {
      "skill_name": "string",
      "date": "date",
      "session_id": "string",
      "target_issue": "string",
      "completed": "boolean",
      "is_homework": "boolean",
      "homework_followed_up": "boolean",
      "user_feedback": "helpful | neutral | unhelpful | null"
    }
  ],

  "preferences": {
    "preferred_techniques": ["mindfulness"],
    "disliked_techniques": [],
    "communication_style": "gentle | direct"
  }
}
```

### 画像更新时机

| 时机 | 更新内容 |
|------|---------|
| 每轮对话后 | 对齐分数、情绪状态 |
| 识别到认知扭曲时 | cognitive_distortions 列表 |
| 完成干预练习后 | intervention_history、user_feedback |
| 会话结束时 | mood_history、key_themes、behavioral_patterns |
| 危机检测时 | risk_level 立即更新 |

---

## 10. Skill 干预体系

### 10.1 实现方式

使用 GPT-5.4 原生 Skills 功能。每个干预技术一个 skill.md 文件，Agent 按需调用。

### 10.2 目录结构

```
skills/
├── listening/
│   └── active_listening.skill.md
├── cbt/
│   ├── cognitive_restructuring.skill.md     # 认知重构（对话式）
│   ├── thought_record.skill.md              # 想法记录（卡片）
│   └── behavioral_activation.skill.md       # 行为激活（对话+卡片）
├── act/
│   ├── acceptance.skill.md                  # 接纳练习
│   ├── defusion.skill.md                    # 认知解离
│   └── values_exploration.skill.md          # 价值观探索
├── mindfulness/
│   ├── breathing_478.skill.md               # 4-7-8 呼吸法（卡片）
│   ├── body_scan.skill.md                   # 身体扫描（卡片）
│   └── grounding_54321.skill.md             # 5-4-3-2-1 接地（卡片）
├── positive_psychology/
│   ├── gratitude_journal.skill.md           # 感恩日记（卡片）
│   ├── strength_spotting.skill.md           # 优势识别
│   └── three_good_things.skill.md           # 三件好事（卡片）
├── emotion_regulation/
│   ├── emotion_naming.skill.md              # 情绪命名
│   └── emotion_thermometer.skill.md         # 情绪温度计（卡片）
└── crisis/
    └── crisis_response.skill.md             # 危机响应协议
```

### 10.3 skill.md 格式规范

```markdown
---
name: skill_id
display_name: 显示名称
category: cbt | act | mindfulness | positive_psychology | emotion_regulation | listening | crisis
trigger: 触发条件描述
output_type: dialogue | card | mixed
card_template: guided_exercise | journal | checklist | null
estimated_turns: 5-8
estimated_duration: 3-5min
min_phase: P1 | P2 | P3 | P4
contraindications:
  - risk_category: crisis
---

## 目标
该干预技术要达成的目标。

## 引入话语
如何自然地从对话过渡到干预。

## 执行流程
分步骤描述干预过程。

## 卡片内容（如 output_type 包含 card）
结构化的卡片数据。

## 结束与评估
干预结束后的收尾和效果确认。

## 作业布置（可选）
布置给用户回去做的练习，后续跟进。

## 注意事项
执行中的注意要点。
```

### 10.4 Skill 与 Agent 的对应关系

| Agent | 可调用的 Skill 类型 |
|-------|-------------------|
| Greeter（迎客） | listening、emotion_regulation |
| Explorer（探索） | emotion_regulation（辅助探索） |
| Assessor（评估） | 不直接调用 Skill，输出结构化评估报告 |
| Recommender（推荐） | 读取全部 Skill 库元数据，匹配并推荐 1-2 个方案 |
| Motivator（激发） | 所有 Skill 的引入/解释部分 |
| Interventor（干预） | cbt、act、mindfulness、positive_psychology、emotion_regulation |
| 任意 Agent | crisis（危机响应） |

### 10.5 卡片式练习

卡片在对话流中内嵌渲染，示例：

```json
{
  "type": "guided_exercise",
  "title": "4-7-8 呼吸法",
  "steps": [
    {"instruction": "舒适地坐好，轻轻闭上眼睛", "duration": 5},
    {"instruction": "用鼻子慢慢吸气，数4秒", "duration": 4, "animation": "inhale"},
    {"instruction": "屏住呼吸，数7秒", "duration": 7, "animation": "hold"},
    {"instruction": "用嘴巴慢慢呼气，数8秒", "duration": 8, "animation": "exhale"},
    {"instruction": "重复3轮", "repeat": 3}
  ]
}
```

---

## 11. 危机响应协议

### 11.1 触发条件

- 理解层 risk_category 为危机相关类别
- 关键词检测：自杀、自伤、不想活、结束生命等
- 用户表达绝望且拒绝所有帮助

### 11.2 响应流程

```
1. 立即共情回应，确认用户安全
   "听到你这样说，我非常担心你的安全。你现在安全吗？"

2. 提供紧急资源（卡片形式）
   ┌──────────────────────────────┐
   │  如果你需要紧急帮助：           │
   │  · 24小时心理援助热线           │
   │    400-161-9995               │
   │    010-82951332（北京）        │
   │  · 生命热线 400-821-1215       │
   │  · 紧急情况请拨打 120 / 110    │
   │                               │
   │  [预约咨询师 →]                │
   └──────────────────────────────┘

3. 保持陪伴，不中断对话
4. 持续评估安全状态
5. 记录到用户画像（risk_level = crisis）
```

---

## 12. 数据库设计

### 12.1 核心表

```sql
-- 用户
users (
  user_id           PK
  nickname
  created_at
  last_seen_at
)

-- 用户画像
user_profiles (
  user_id           PK, FK → users
  clinical_profile  JSON
  alliance          JSON
  preferences       JSON
  risk_level
  updated_at
)

-- 会话
sessions (
  session_id        PK
  user_id           FK → users
  started_at
  ended_at
  opening_mood_score
  closing_mood_score
  phase_history     JSON    -- 本次会话经历的阶段记录
  summary           TEXT    -- AI 生成的会话摘要
)

-- 消息
messages (
  message_id        PK
  session_id        FK → sessions
  role              -- user | assistant | system
  content           TEXT
  analysis          JSON    -- 理解层的结构化分析结果
  card_data         JSON    -- 卡片渲染数据（如有）
  created_at
)

-- 干预记录
interventions (
  intervention_id   PK
  session_id        FK → sessions
  user_id           FK → users
  skill_name
  target_issue
  started_at
  completed
  is_homework
  homework_followed_up
  user_feedback
)
```

---

## 13. 隐私与安全

### 13.1 隐私原则

- 用户画像仅用于个性化服务，不向企业暴露个人对话内容
- 用户可查看自己的历史对话
- 对话内容加密存储

### 13.2 数据安全

- Azure OpenAI 企业版数据不用于模型训练
- 传输全程 HTTPS
- 数据库加密存储敏感字段

---

## 14. MVP 分期

### Phase 1 - 核心对话

- [ ] Web 前端：登录、对话界面、情绪签到
- [ ] Supervisor Agent + P1/P2 Agent
- [ ] 理解层结构化分析
- [ ] 基础 Skills：积极倾听、情绪命名
- [ ] 用户画像基础读写
- [ ] 输入安全：危机检测与响应
- [ ] 输出安全：基础红线
- [ ] 对齐分数基础逻辑

### Phase 2 - 干预能力

- [ ] P3/P4 Agent
- [ ] 完整 Skill 库：CBT、ACT、正念、积极心理学
- [ ] 卡片式练习渲染
- [ ] 干预效果追踪（当场反馈 + 作业跟进）
- [ ] 对齐分数与阶段切换完整逻辑
- [ ] 会话摘要生成

### Phase 3 - 生态完善

- [ ] 咨询师预约外链集成
- [ ] 历史对话查看
- [ ] 跨会话记忆完善（画像摘要、干预进展追踪）
- [ ] 多问题管理优化

### Phase 4 - 进阶功能

- [ ] 管理后台（匿名统计）
- [ ] 情绪趋势可视化（用户侧）
- [ ] 更多干预 Skill 扩展
- [ ] 效果评估体系
