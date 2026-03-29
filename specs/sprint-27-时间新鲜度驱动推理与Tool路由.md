# Sprint 27 - 时间新鲜度驱动推理与 Tool 路由

## 背景

`Sprint 26` 已经让运行时上下文具备“当前时间 + 历史条目的绝对时间/相对时间”，但目前这些时间信息主要用于展示和提示，还没有真正影响心雀的推理与 Tool 路由。

这会带来一个直接问题：如果用户昨天刚完成过一次 intervention，今天再次聊天时，模型可能仍然直接调用 `match_intervention()` 或 `load_skill()`，机械重复推荐或重新加载练习，而没有先 follow-up 用户是否尝试、是否完成、效果如何。

## 目标

让“时间新鲜度”从上下文元数据升级为最小运行时规则：

1. 当最近 48 小时内存在“未收口”的 intervention 时，心雀优先 follow-up，而不是立即重新推荐方案。
2. 只有当用户明确要求换方法、说明旧方法无效、或主动要求重做同一个练习时，才允许跳过 follow-up。
3. 这一规则需要同时体现在：
   - `system_prompt.py` 的 Tool Contract / 长会话契约
   - `xinque.py` 的运行时 guardrail

## 本 Sprint 范围

### 1. recent intervention follow-up guardrail

对以下 Tool 增加时间新鲜度判断：

- `match_intervention`
- `load_skill`

最小规则：

- 若用户最近一次 intervention 距今不超过 48 小时，且该 intervention 仍属于“未收口”状态：
  - `completed` 不是 `True`，或
  - 缺少 `user_feedback` / `key_insight` / `homework_completed` 等结果性信息
- 则本轮优先要求 follow-up，不应直接重新推荐或重复加载同一练习。

### 2. 允许跳过 follow-up 的显式信号

以下情况允许放行：

- 用户明确要求“换一个方法 / 别的方法 / 新的方法”
- 用户明确表示“刚才那个没用 / 不适合 / 不想做那个”
- 用户明确要求“再做一次 / 重新来一遍 / 再带我做那个”

### 3. prompt contract 同步

在 `system_prompt.py` 中加入明确规则：

- 最近 intervention/作业具有高时间新鲜度时，优先 follow-up
- 不要因为用户再次来聊天，就机械重复推荐昨天刚做过的方案
- 当用户明确要求换方法或重做时，再进入新推荐/重做路径

## 不在本 Sprint 范围

- 不做基于所有历史 intervention 的复杂冷却系统
- 不做 skill 级别推荐去重排序
- 不做 evaluator 专用的时间分析 UI
- 不改 `match_intervention.py` 的评分算法，只在运行时入口补 guardrail

## 验收要点

1. recent intervention 在 48 小时内且未收口时，`match_intervention` 会被阻止，并返回要求 follow-up 的 blocked 结果。
2. 同一练习在 48 小时内刚做过时，`load_skill` 会被阻止，除非用户明确要求重做。
3. 用户明确要求换方法或重做时，上述阻止规则会放行。
4. `system_prompt.py` 中存在与时间新鲜度一致的明确契约描述。
5. 新增测试先失败后通过，并通过后端全量回归。
