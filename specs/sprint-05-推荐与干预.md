# Sprint 05 — 推荐与干预

## 目标

实现 P3 + P4 的核心能力：`match_intervention()` 匹配干预方案，`load_skill()` 加载干预协议，`render_card()` 渲染练习卡片，`record_outcome()` 记录干预结果。本 Sprint 完成后，心雀将具备完整的四阶段对话能力。

## 背景

Sprint 04 的 formulate() 已能构建 readiness="solid" 的个案概念化。但心雀目前只能探索，不能推荐和执行干预。本 Sprint 补齐 P3/P4，打通从探索到干预的完整闭环。

## 本 Sprint 范围

### 1. Skill 文件（skill.md）

**做**：
- 创建 3 个基础 Skill 文件：
  - `app/skills/cbt/cognitive_restructuring.skill.md` — 认知重构（对话式）
  - `app/skills/mindfulness/breathing_478.skill.md` — 4-7-8 呼吸法（卡片）
  - `app/skills/emotion_regulation/emotion_naming.skill.md` — 情绪命名（对话式）
- 按 product-plan-v2 第 10.3 节的格式规范编写

**不做**：
- 完整 Skill 库（ACT、积极心理学等留后续 Sprint）

### 2. match_intervention() Tool — P3 主力

**做**：
- `app/backend/app/agent/tools/match_intervention.py`
- 读取当前会话的 formulation
- 扫描 skills/ 目录下所有 skill.md 的 frontmatter
- 基于 formulation 的认知扭曲类型、情绪、严重程度匹配合适的 1-2 个方案
- 返回匹配结果（skill_name, display_name, rationale, user_friendly_intro）

### 3. load_skill() Tool — P4

**做**：
- `app/backend/app/agent/tools/load_skill.py`
- 根据 skill_name 加载对应 skill.md 的完整内容
- 返回给 LLM（LLM 按其中的执行流程引导用户）

### 4. render_card() Tool — P4

**做**：
- `app/backend/app/agent/tools/render_card.py`
- 接收卡片 JSON 数据，通过 API 响应传递给前端
- 本 Sprint 先实现数据传递机制，前端渲染卡片

### 5. record_outcome() Tool — P4

**做**：
- `app/backend/app/agent/tools/record_outcome.py`
- interventions 表（Alembic 迁移）
- 记录干预完成状态、用户反馈、关键洞察、作业布置

### 6. 前端：卡片渲染

**做**：
- ChatWindow 支持渲染 card_data（嵌入消息流中）
- 基础卡片组件：呼吸引导步骤展示
- API 响应增加 card_data 字段

### 7. Agent 集成

**做**：
- 注册 4 个新 Tool
- System Prompt 增加 P3/P4 Tool 使用指南
- 当 formulate() readiness="sufficient" 时，LLM 应调用 match_intervention()

## 用户可感知的变化

完整的四阶段体验：
1. 心雀问好，了解用户状态（P1）
2. 深入探索情绪/认知/行为（P2）
3. 向用户推荐干预方案，解释为什么适合（P3）
4. 引导用户完成干预练习，询问感受，布置作业（P4）

## 不在范围

- 完整 Skill 库（仅 3 个基础 Skill）
- 情景记忆 embedding
- 对齐分数自动计算
- 可观测性 Trace
