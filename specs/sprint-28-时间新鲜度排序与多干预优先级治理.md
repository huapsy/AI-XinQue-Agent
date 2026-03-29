# Sprint 28 - 时间新鲜度排序与多干预优先级治理

## 背景

`Sprint 26` 已让心雀具备时间感知上下文，`Sprint 27` 已让最近 48 小时内的 intervention 能影响 `match_intervention()` 和 `load_skill()` 的最小运行时 guardrail。

但当前系统仍然只处理“最近一次 intervention”的最小场景，还没有解决以下更接近真实使用的问题：

- `search_memory()` 返回多个相关记忆时，结果并不会按时间新鲜度与当前相关性共同排序。
- 当用户存在多个历史 intervention（例如昨天做过呼吸练习、上周做过 thought record）时，系统没有明确的优先级规则去判断应该先 follow-up 哪一个。
- 对“旧方法”与“当前主线”的区分还不稳定，容易把很久以前的练习错误拉回当前主线。

因此，需要把“时间新鲜度”从单个 recent intervention 的 guardrail，推进成多来源、多条目下的运行时排序和优先级治理。

## 目标

建立一套最小但明确的时间优先级规则，使心雀在面对多个历史事件、多个 intervention 和多条 memory 时，能更稳定地判断：

1. 哪些历史事项属于“当前最值得 follow-up 的主线”
2. 哪些历史事项只应作为背景参考
3. `search_memory()` 返回结果时，哪些条目应该排在前面
4. 多个 intervention 同时存在时，优先围绕哪一个继续

## 本 Sprint 范围

### 1. `search_memory()` 增加时间新鲜度排序

在不推翻现有检索逻辑的前提下，为 `search_memory()` 的结果增加最小排序规则：

- 保留现有语义/关键词匹配逻辑
- 在匹配分数接近时，优先返回时间更近的记忆
- 对很久以前的记忆，若没有明显更高相关性，不应排在近期记忆之前

目标不是做复杂 reranker，而是引入“相关性优先、时间新鲜度次优先”的稳定 tie-break 规则。

### 2. 多 intervention 的 follow-up 优先级

当用户存在多个历史 intervention 时，运行时需要明确一个主 follow-up 对象：

优先级建议：

1. 最近 48 小时内且未收口的 intervention
2. 最近 7 天内且与当前主题相关的 intervention
3. 更早但被用户主动重新提及的 intervention
4. 其他 intervention 默认只作背景信息

系统不需要一次性 follow-up 多个 intervention，而应优先聚焦一个最值得继续的对象。

### 3. “主线”与“背景”区分规则

需要补充统一规则，避免旧信息抢占主线：

- 刚发生 / 昨天发生 / 本周仍连续相关的事项，可进入当前主线候选
- 更早的事项默认进入背景层，除非：
  - 用户主动重新提起
  - 当前问题与其直接连续
  - 当前没有更新近的同类事项

这套规则需要同时反映在：

- 运行时 helper / 排序逻辑
- prompt contract / retrieval guidance

### 4. 最小冷却语义

本 Sprint 不做复杂推荐冷却系统，但应补一个最小语义：

- 在短时间内（例如 48 小时）刚推荐或刚执行过的同类 intervention，不应在没有新证据时反复作为第一推荐
- 如果用户主动要求、旧方法无效、或 follow-up 后确认需要切换，则允许重新进入推荐序列

## 不在本 Sprint 范围

- 不做前端 UI 改造
- 不做管理后台时间线可视化
- 不做复杂向量 reranker
- 不做全面的 recommendation engine 重写
- 不做跨用户的全局统计策略

## 设计约束

1. 不能破坏现有 `Sprint 27` 的 recent intervention guardrail。
2. 新增排序逻辑应尽量作为 helper 存在，不把 `xinque.py` 再次堆成更大的单文件规则集合。
3. prompt 中的时间新鲜度原则要与运行时规则一致，不能出现“prompt 说 follow-up、代码却仍优先推荐”的偏差。
4. 测试必须覆盖：
   - `search_memory()` 的时间排序
   - 多 intervention 主优先对象选择
   - 旧 intervention 不应抢占近期主线

## 预期产出

- 一个用于统一判断时间新鲜度优先级的 helper 模块或 helper 函数集
- `search_memory()` 的最小时间排序能力
- 运行时对多 intervention 的主 follow-up 选择能力
- prompt / retrieval guidance 的同步更新
- 对应测试与评估文档

## 验收思路

1. 当两条记忆相关性接近时，较新的记忆排在前面。
2. 当用户同时存在多个 intervention 时，系统能识别一个主 follow-up 对象，而不是平均对待全部历史。
3. 更早的 intervention 在未被用户重新激活时，不会抢占刚发生 intervention 的优先级。
4. 短时间内刚做过/刚推荐过的同类 intervention，不会被机械地再次作为首推方案。
5. 自动化测试通过，且与 `Sprint 27` 的 guardrail 不冲突。
