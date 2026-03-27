# Sprint 07 Contract — 对齐兜底、转介与 Skill 补全

## 成功标准

### 对齐分数代码层兜底

1. **分数更新**
   - 用户发送不对齐消息（如"你说的没用"） → user_profiles.alliance.alignment_score 下降

2. **兜底注入**
   - 模拟对齐分数 ≤ 5 → System Prompt 末尾出现温和提示文本
   - 模拟对齐分数 ≤ 0 → System Prompt 末尾出现强制警告文本

3. **心雀行为变化**
   - 对齐低时心雀的回复风格变为接纳/降压，不推进干预

### referral() Tool

4. **转介卡片**
   - 用户说"我想找真人咨询师" → 心雀调用 referral() → 回复中包含 EAP 链接和热线
   - API 响应的 card_data 包含转介卡片数据

### Skill 补全

5. **新 Skill 文件**
   - thought_record、grounding_54321、three_good_things 三个文件存在且含 frontmatter
   - thought_record 和 grounding_54321 含 card_data

6. **match_intervention 兼容**
   - 恐慌/高焦虑 → grounding_54321 能被匹配到
