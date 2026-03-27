# Sprint 05 Contract — 推荐与干预

## 成功标准

### Skill 文件

1. **Skill 存在**
   - `app/skills/cbt/cognitive_restructuring.skill.md` 存在且含 frontmatter
   - `app/skills/mindfulness/breathing_478.skill.md` 存在且含 frontmatter
   - `app/skills/emotion_regulation/emotion_naming.skill.md` 存在且含 frontmatter

### match_intervention()

2. **方案匹配**
   - 当 formulation 包含 catastrophizing 认知扭曲 → match_intervention() 返回包含 cognitive_restructuring 的方案
   - 返回结果包含 rationale 和 user_friendly_intro

### load_skill()

3. **加载干预内容**
   - load_skill("cognitive_restructuring") → 返回完整的 skill.md 内容（包含执行流程）

### record_outcome()

4. **记录干预结果**
   - interventions 表存在
   - 干预完成后 record_outcome() 写入记录（completed=true, user_feedback, key_insight）

### 前端卡片

5. **卡片渲染**
   - chat API 响应支持 card_data 字段
   - 呼吸练习触发时前端显示卡片（步骤列表）

### 端到端

6. **完整四阶段**
   - 用户 A 对话：问好 → 告知困扰 → 探索 2-3 轮 → 心雀推荐方案 → 用户选择 → 心雀引导完成干预 → 询问感受 → 记录结果
   - 数据库中有 formulation（readiness=sufficient+）和 intervention 记录
