# Sprint 07 评估报告

**日期**: 2026-03-27
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | 对齐分数更新 | ✅ | 15→12→9→4，三轮不对齐正确扣分（-3,-3,-5） |
| 2 | 兜底 prompt 注入 | ✅ | score≤5 注入温和提示，score≤0 注入强制警告 |
| 3 | 心雀行为变化 | ✅ | 对齐低时回复变为接纳/降压（"没关系，不想说也可以"） |
| 4 | referral Tool | ✅ | 用户说"找真人咨询师"→回复提及 EAP/咨询师资源 |
| 5 | 新 Skill 文件 | ✅ | thought_record + grounding_54321 + three_good_things |
| 6 | match_intervention 兼容 | ✅ | 恐慌→grounding_54321 可被匹配 |

## 本 Sprint 产出

### 新增文件
- `app/backend/app/alignment.py` — 对齐分数代码层追踪（轻量级文本检测 + 分数更新）
- `app/backend/app/agent/tools/referral.py` — 转介工具（EAP 链接 + 热线卡片）
- `app/skills/cbt/thought_record.skill.md` — CBT 想法记录（卡片式）
- `app/skills/mindfulness/grounding_54321.skill.md` — 5-4-3-2-1 接地练习（卡片式）
- `app/skills/positive_psychology/three_good_things.skill.md` — 三件好事（对话式）
- `app/backend/alembic/versions/3fd615485238_add_alliance_to_user_profiles.py` — 迁移

### 修改文件
- `app/backend/app/agent/system_prompt.py` — 对齐兜底 prompt 注入 + referral Tool 指南
- `app/backend/app/agent/xinque.py` — 注册 referral Tool（总计 7 个），传递 alignment_score
- `app/backend/app/main.py` — 集成对齐追踪（检测信号→更新分数→注入 prompt）
- `app/backend/app/models/tables.py` — UserProfile 新增 alliance JSON 字段
- `app/backend/app/agent/tools/match_intervention.py` — 新增 grounding/thought_record/three_good_things 匹配规则
- `app/frontend/src/components/chat/ChatWindow.tsx` — ReferralCard 组件

### 前端新增
- `ReferralCard` 组件 — 红色主题的转介卡片（资源列表 + EAP 链接 + 热线号码）

## 亮点

- 对齐分数双轨机制落地：LLM 自主感知（回复风格自然转变）+ 代码层兜底（score≤5 注入 prompt）
- 三轮不对齐后 score=4，刚好触发温和提示注入，心雀的回复变为纯接纳模式
- Skill 库扩展到 9 个，覆盖 CBT(3)、ACT(1)、正念(3)、积极心理学(2)、情绪调节(1)
- Azure OpenAI 内容过滤会拦截极端表达（如"你只是机器人"触发 hate filter），但温和不对齐表达正常工作

## 注意事项

- Azure OpenAI 的内容过滤可能拦截某些用户不对齐表达，生产环境需考虑在 Azure 侧调整过滤策略
