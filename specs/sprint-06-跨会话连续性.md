# Sprint 06 Spec — 跨会话连续性与作业跟进

## 目标

让回访用户感受到心雀"记得我上次做了什么"。补全 recall_context 的信息完整度，升级会话摘要为 LLM 生成，扩展 Skill 库。

## 功能点

### 1. recall_context 增强

当前 recall_context 只返回昵称、session_count、上次会话摘要。需要增加：

- **pending_homework**：查 interventions 表中 homework_assigned 非空且 homework_completed=false 的记录
- **intervention_history**：最近 3 次干预记录（skill_name、user_feedback、key_insight、日期）

LLM 拿到这些信息后，能在回访开场中自然地提及"上次你试了认知重构，还布置了一个作业，完成得怎么样？"

### 2. LLM 生成会话摘要

当前 end_session 只是拼接用户消息。改为调用 LLM 生成结构化摘要：
- 本次讨论的主题
- 用户的核心困扰
- 做了什么干预、效果如何
- 布置了什么作业

摘要用于下次 recall_context 返回，帮助 LLM 快速了解上次对话内容。

### 3. 扩展 Skill 库

新增 3 个 Skill 文件：
- `app/skills/act/defusion.skill.md` — ACT 认知解离（对话式）
- `app/skills/mindfulness/body_scan.skill.md` — 身体扫描（卡片式）
- `app/skills/positive_psychology/gratitude_journal.skill.md` — 感恩日记（卡片式）

### 4. 端到端回访验证

完整流程：对话→干预→结束会话→新会话→心雀主动关联上次干预和作业
