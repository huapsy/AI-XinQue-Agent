# Sprint 06 Contract — 跨会话连续性与作业跟进

## 成功标准

### recall_context 增强

1. **pending_homework**
   - 用户完成干预并布置作业后，结束会话，开始新会话
   - recall_context() 返回的 pending_homework 包含作业描述和布置日期

2. **intervention_history**
   - recall_context() 返回 intervention_history，包含最近干预的 skill_name、user_feedback、key_insight

### LLM 生成摘要

3. **会话摘要质量**
   - end_session 后 sessions.summary 不是简单的消息拼接
   - 摘要包含主题、干预、作业等关键信息（可读的自然语言）

### Skill 库扩展

4. **新 Skill 文件**
   - `app/skills/act/defusion.skill.md` 存在且含 frontmatter
   - `app/skills/mindfulness/body_scan.skill.md` 存在且含 frontmatter + card_data
   - `app/skills/positive_psychology/gratitude_journal.skill.md` 存在且含 frontmatter + card_data

5. **match_intervention 兼容**
   - 新 Skill 能被 match_intervention 匹配到（如反刍思维 → 认知解离）

### 端到端回访

6. **回访关联**
   - 新会话中心雀主动提及上次的干预和作业完成情况
   - 数据库中新会话的 recall_context 调用返回了 pending_homework
