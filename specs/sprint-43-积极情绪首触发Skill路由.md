# Sprint 43 - 积极情绪首触发 Skill 路由

## 背景

当前心雀已经具备：

- `P1-P4` 咨询阶段纪律
- 负向情绪和问题导向场景下的探索、推荐与干预链路
- 多个负向或调节导向 skill

但从真实对话反馈看，当前系统在用户刚开始表达积极情绪时，仍主要沿默认探索逻辑推进：

- 正向 sentiment 会被当作普通情感倾向继续探索
- 感谢、认同、愿意等更多被当作 alignment 加分，而不是积极情绪专用路径
- 系统缺少一条“用户明确高兴 / 开心 / 满足 / 自豪时，就进入正向体验巩固”的 skill 路由

这导致用户处在积极状态时，系统容易：

- 回到问题导向探索
- 过度解释用户
- 过早转成任务化或总结化
- 错失把积极体验沉淀为可复用心理资源的机会

## 目标

本轮 sprint 的目标，是建立“积极情绪首触发 skill 路由”的最小闭环，至少覆盖：

- 新增一个可被现有 skill 体系识别的正向体验巩固 skill
- 当用户刚开始明确表达积极情绪时，允许直接进入该 skill
- 当负面情绪仍明显主导时，阻止误入该 skill
- 用最小测试证明这条路由存在且可控

## 范围

### 1. 新增正向体验 skill

新增 `positive_experience_consolidation`，用于在用户表达积极情绪时：

- 承接正向感受
- 回顾具体情境
- 深化主观体验
- 提炼内在资源
- 轻量引向可复制性

### 2. Skill registry 合法接入

该 skill 必须符合现有 `.skill.md + manifest v2` 规范，并能被当前 skill registry 正常识别。

### 3. Runtime 受控直达

在不放宽其他 skill guardrail 的前提下，为 `positive_experience_consolidation` 增加一条例外路径：

- 若用户消息中有明确积极情绪信号
- 且没有明显负面情绪主导
- 则允许直接 `load_skill("positive_experience_consolidation")`

若条件不满足，则应明确阻止。

### 4. Prompt 路由提示

Prompt 中至少应明确说明：

- 用户刚开始表达积极情绪或良好状态时
- 可直接加载 `positive_experience_consolidation`

以便模型知道这是一条合法能力，而不是只能走默认探索。

## 非目标

- 本轮不重做完整积极情绪对话架构
- 不把积极 sentiment 自动接入 `match_intervention()` 推荐排序
- 不做完整对话级正向路径 eval 样本库
- 不扩展更多正向 skill 家族

## 预期结果

如果本轮完成，心雀将具备第一条“积极情绪首触发”的正式 skill 路由：当用户刚开始明确表达高兴、开心、自豪等状态时，系统不再只能沿默认探索逻辑处理，而是可以合法进入 `positive_experience_consolidation` 来承接并巩固这份积极体验。
