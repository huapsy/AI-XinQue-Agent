# Sprint 05 评估报告

**日期**: 2026-03-27
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | Skill 文件存在且含 frontmatter | ✅ | cognitive_restructuring + breathing_478 + emotion_naming |
| 2 | match_intervention 方案匹配 | ✅ | catastrophizing → 返回 cognitive_restructuring + breathing_478，含 rationale 和 user_friendly_intro |
| 3 | load_skill 加载干预内容 | ✅ | 返回完整执行流程，breathing_478 含 card_data |
| 4 | record_outcome 记录干预结果 | ✅ | interventions 表写入成功，completed=true, feedback=helpful, key_insight + homework |
| 5 | 前端卡片渲染 | ✅ | ChatResponse 含 card_data 字段，前端 ExerciseCard 组件就位，TS 编译通过 |
| 6 | 端到端四阶段 | ✅ | P1 倾听→P2 探索(formulate×多次)→P3 推荐→P4 认知重构干预→记录结果 |

## 本 Sprint 产出

### Skill 文件
- `app/skills/mindfulness/breathing_478.skill.md` — 4-7-8 呼吸法（含卡片 JSON）
- `app/skills/emotion_regulation/emotion_naming.skill.md` — 情绪命名（对话式）
- `app/skills/cbt/cognitive_restructuring.skill.md` — 已有（Sprint 04）

### 后端新增
- `app/backend/app/agent/tools/match_intervention.py` — P3 主力 Tool（方案匹配）
- `app/backend/app/agent/tools/load_skill.py` — P4 Tool（加载 Skill 内容）
- `app/backend/app/agent/tools/record_outcome.py` — P4 Tool（记录干预结果）
- `app/backend/app/models/tables.py` — 新增 Intervention 模型
- `app/backend/alembic/versions/ee7af091ee8f_add_interventions_table.py` — 迁移
- `app/backend/requirements.txt` — 新增 pyyaml 依赖

### 后端修改
- `app/backend/app/agent/xinque.py` — 注册 6 个 Tool，chat() 返回 card_data
- `app/backend/app/agent/system_prompt.py` — 新增 4 个 Tool 使用指南
- `app/backend/app/main.py` — ChatResponse 新增 card_data 字段

### 前端修改
- `app/frontend/src/components/chat/ChatWindow.tsx` — ExerciseCard 组件 + card_data 渲染

## 亮点

- LLM 自主完成了完整的四阶段对话流（P1→P2→P3→P4），包括多次 formulate 调用和最终 record_outcome
- match_intervention 正确匹配了 cognitive_restructuring（针对 catastrophizing）和 breathing_478（针对焦虑）
- record_outcome 正确记录了 key_insight（"用户意识到不是每次都不行"）和作业布置
- 对话质量高：心雀的认知重构引导自然流畅，用了用户自己的语言
- formulation 的 mechanism 准确描述了问题维持循环
