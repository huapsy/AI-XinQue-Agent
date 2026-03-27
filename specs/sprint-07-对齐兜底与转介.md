# Sprint 07 Spec — 对齐兜底、转介与 Skill 补全

## 目标

落地产品方案中"三层保障机制"的代码层兜底，实现转介工具，补齐 Skill 库至 9 个。

## 功能点

### 1. 对齐分数代码层追踪

产品方案 6.2-6.4 节要求的双轨机制：

- **分数更新**：每轮对话后，后端基于 formulate() 的 alliance_signal 和轻量级文本检测更新对齐分数
- **兜底注入**：
  - 对齐分数持续 3 轮 ≤ 5 → 在下一轮 System Prompt 末尾注入温和提示
  - 对齐分数 ≤ 0 → 注入强制警告，阻止推进
- **分数存储**：写入 user_profiles.alliance JSON 字段（alignment_score）

实现方式：
- 在 main.py 的 chat 端点中，每轮对话后检测对齐信号并更新分数
- build_system_prompt() 接受 alignment_score 参数，低于阈值时追加提示
- 轻量级检测：关键词匹配（"没用""不想说""你不理解""你只是机器"等）

### 2. referral() Tool

- LLM 可调用的 Tool，返回结构化转介卡片
- 包含 EAP 链接（www.eap.com.cn）和热线号码
- 前端渲染为卡片样式
- 触发场景：超出心雀能力、用户主动要求、危机检测

### 3. Skill 补全

新增 3 个 Skill：
- `app/skills/cbt/thought_record.skill.md` — CBT 想法记录（卡片式，用户记录触发情境/自动思维/情绪/替代想法）
- `app/skills/mindfulness/grounding_54321.skill.md` — 5-4-3-2-1 接地练习（卡片式，恐慌/高焦虑时用）
- `app/skills/positive_psychology/three_good_things.skill.md` — 三件好事（对话式，与感恩日记互补）
