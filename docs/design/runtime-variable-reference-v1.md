# 心雀运行时变量参考

## 用途

本文件集中整理当前系统中与连续对话、心理支持和干预跟进相关的核心变量，便于后续优化：

- 用户画像
- 历史事件（情景记忆）
- 最近做过的练习（interventions）
- 作业（homework）
- 会话状态（session state）

说明原则：

- `存储位置` 指数据库表或运行时结构
- `字段名` 指当前代码中实际存在的变量/键
- `含义` 指这个字段在业务上的用途
- `主要写入来源` 指哪些函数/Tool 会更新它

---

## 1. 用户画像 Profile

### 1.1 数据表

- `users`
- `user_profiles`

### 1.2 核心字段

| 字段名 | 存储位置 | 含义 | 主要写入来源 |
|---|---|---|---|
| `user_id` | `users.user_id` | 用户唯一 ID | 用户创建 |
| `client_id` | `users.client_id` | 当前前端匿名身份标识 | 前端初始化 + `_get_or_create_user()` |
| `nickname` | `users.nickname` / `user_profiles.nickname` | 用户称呼 | `save_nickname()` / `update_profile()` |
| `session_count` | `user_profiles.session_count` | 累计会话次数 | `_create_session()` |
| `risk_level` | `user_profiles.risk_level` | 风险级别：`none/low/medium/high/crisis` | 输入安全层、`update_profile()`、风险逻辑 |
| `alliance` | `user_profiles.alliance` | 关系/对齐状态容器 | `_build_alliance_patch()` 相关逻辑 |
| `preferences` | `user_profiles.preferences` | 用户偏好/厌恶的技术与 skill | `record_outcome()` → `build_preference_patch_from_outcome()` |
| `clinical_profile` | `user_profiles.clinical_profile` | 从 formulation 提炼出的结构化心理画像 | `formulate()` → `build_clinical_profile_patch_from_formulation()` |

### 1.3 `alliance` 子字段

| 字段名 | 含义 |
|---|---|
| `alignment_score` | 当前对齐分数 |
| `misalignment_history` | 历史不对齐信号记录 |

### 1.4 `preferences` 子字段

| 字段名 | 含义 |
|---|---|
| `preferred_techniques` | 用户反馈有帮助的技术或 skill |
| `disliked_techniques` | 用户反馈无帮助或不喜欢的技术或 skill |

### 1.5 `clinical_profile` 当前提炼字段

| 字段名 | 含义 |
|---|---|
| `key_themes` | 关键主题/领域，如 `workplace` |
| `dominant_emotions` | 主要情绪 |
| `cognitive_distortions` | 认知扭曲类型 |
| `behavioral_patterns` | 适应性/非适应性行为模式 |
| `primary_issue` | 当前主要问题 |

---

## 2. 历史事件 Episodic Memories

### 2.1 数据表

- `episodic_memories`

### 2.2 核心字段

| 字段名 | 存储位置 | 含义 | 主要写入来源 |
|---|---|---|---|
| `memory_id` | `episodic_memories.memory_id` | 记忆唯一 ID | 自动生成 |
| `user_id` | `episodic_memories.user_id` | 所属用户 | `maybe_store_episodic_memory()` |
| `session_id` | `episodic_memories.session_id` | 来源会话 | `maybe_store_episodic_memory()` |
| `content` | `episodic_memories.content` | 事件文本内容 | `build_memory_candidate()` |
| `topic` | `episodic_memories.topic` | 事件主题，如 `workplace`、`family_health` | `_infer_topic()` |
| `emotions` | `episodic_memories.emotions` | 与事件关联的情绪 | `build_memory_candidate()` |
| `embedding` | `episodic_memories.embedding` | 用于检索排序的 embedding | `embed_text()` |
| `created_at` | `episodic_memories.created_at` | 记忆沉淀时间 | 自动生成 |

### 2.3 运行时返回字段

`search_memory()` 当前主要返回：

| 字段名 | 含义 |
|---|---|
| `content` | 事件内容 |
| `topic` | 事件主题 |
| `emotions` | 事件情绪 |
| `created_at` | 绝对时间 |

---

## 3. 最近做过的练习 Interventions

### 3.1 数据表

- `interventions`

### 3.2 核心字段

| 字段名 | 存储位置 | 含义 | 主要写入来源 |
|---|---|---|---|
| `intervention_id` | `interventions.intervention_id` | 干预记录唯一 ID | `record_outcome()` |
| `session_id` | `interventions.session_id` | 来源会话 | `record_outcome()` |
| `user_id` | `interventions.user_id` | 所属用户 | `record_outcome()` |
| `skill_name` | `interventions.skill_name` | 做过的具体 skill | `record_outcome()` |
| `target_issue` | `interventions.target_issue` | 目标问题 | `record_outcome()` |
| `started_at` | `interventions.started_at` | 干预开始时间 | 自动生成 |
| `completed` | `interventions.completed` | 是否完成 | `record_outcome()` |
| `user_feedback` | `interventions.user_feedback` | 用户反馈，如 `helpful/neutral/unhelpful` | `record_outcome()` |
| `key_insight` | `interventions.key_insight` | 关键洞察 | `record_outcome()` |
| `homework_assigned` | `interventions.homework_assigned` | 附带作业 JSON | `record_outcome()` |
| `homework_completed` | `interventions.homework_completed` | 作业是否完成 | 后续 follow-up / 更新逻辑 |

### 3.3 `recent_interventions` 运行时视图

`recall_context()` 当前整理出的最近干预字段：

| 字段名 | 含义 |
|---|---|
| `skill_name` | 最近做过的练习名 |
| `date` | 日期级时间 |
| `started_at_iso` | 精确时间 |
| `relative_time` | 相对时间，如“昨天” |
| `completed` | 是否完成 |
| `user_feedback` | 用户反馈 |
| `key_insight` | 关键洞察 |

---

## 4. 作业 Homework

### 4.1 存储方式

当前没有独立 `homework` 表，作业挂在 `interventions.homework_assigned` 上。

### 4.2 核心字段

| 字段名 | 存储位置 | 含义 | 主要写入来源 |
|---|---|---|---|
| `homework_assigned.description` | `interventions.homework_assigned` | 作业内容描述 | `record_outcome()` |
| `homework_assigned.frequency` | `interventions.homework_assigned` | 建议频率 | `record_outcome()` |
| `homework_completed` | `interventions.homework_completed` | 作业是否完成 | 后续跟进更新 |

### 4.3 `pending_homework` 运行时视图

`recall_context()` 当前整理出的未完成作业字段：

| 字段名 | 含义 |
|---|---|
| `skill_name` | 作业归属的 skill |
| `assigned_date` | 布置日期 |
| `assigned_at_iso` | 布置绝对时间 |
| `relative_time` | 相对时间 |
| `description` | 作业内容 |
| `frequency` | 作业频率 |

---

## 5. 会话状态 Session State

### 5.1 数据表

- `session_states`
- `session_state_history`

### 5.2 当前状态 `SessionState`

| 字段名 | 存储位置 | 含义 | 主要写入来源 |
|---|---|---|---|
| `session_id` | `session_states.session_id` | 会话 ID | `save_session_state_with_history()` |
| `current_focus` | `session_states.current_focus` | 当前这轮对话主焦点 | `build_layered_context()` |
| `semantic_summary` | `session_states.semantic_summary` | 长会话语义摘要 | `build_layered_context()` |
| `stable_state` | `session_states.stable_state` | 稳定背景状态 | `load_runtime_session_state()` + persisted state |
| `updated_at` | `session_states.updated_at` | 最近更新时间 | 自动生成 |

### 5.3 历史状态 `SessionStateHistory`

| 字段名 | 含义 |
|---|---|
| `version` | 状态版本号 |
| `current_focus` | 当时焦点 |
| `semantic_summary` | 当时摘要 |
| `stable_state` | 当时稳定状态 |
| `change_reason` | 为什么生成新版本 |
| `change_summary` | 本次变化摘要 |
| `created_at` | 版本创建时间 |

### 5.4 `current_focus`

当前常见字段：

| 字段名 | 含义 |
|---|---|
| `priority` | 当前优先级来源，现常用 `current_turn` |
| `summary` | 本轮最重要的焦点概述 |

### 5.5 `semantic_summary`

当前常见字段：

| 字段名 | 含义 |
|---|---|
| `primary_themes` | 主要主题 |
| `active_concerns` | 当前关切 |
| `attempted_methods` | 已尝试方法 |
| `open_loops` | 未收口事项 |

### 5.6 `stable_state`

当前主要结构：

#### `runtime_time_context`

| 字段名 | 含义 |
|---|---|
| `current_time_iso` | 当前绝对时间 |
| `current_date` | 当前日期 |
| `timezone` | 当前时区 |

#### `profile_snapshot`

| 字段名 | 含义 |
|---|---|
| `nickname` | 当前昵称 |
| `risk_level` | 当前风险等级 |
| `preferences` | 当前偏好快照 |
| `alliance` | 当前关系状态快照 |

#### `formulation`

| 字段名 | 含义 |
|---|---|
| `readiness` | 个案概念化成熟度 |
| `primary_issue` | 主要问题 |
| `mechanism` | 当前理解机制 |
| `missing` | 尚缺哪些信息 |

#### `recent_intervention`

| 字段名 | 含义 |
|---|---|
| `skill_name` | 最近干预 skill |
| `started_at_iso` | 干预开始时间 |
| `relative_time` | 相对时间 |
| `completed` | 是否完成 |
| `user_feedback` | 用户反馈 |
| `key_insight` | 关键洞察 |

#### `active_phase`

| 字段名 | 含义 |
|---|---|
| `active_phase` | 当前主导阶段子 agent：`p1_listener / p2_explorer / p3_recommender / p4_interventor` |
| `phase_transition_reason` | 当前进入该阶段的最小路由原因 |

#### `last_session_summary`

| 字段名 | 含义 |
|---|---|
| `last_session_summary` | 上次已结束会话的摘要 |

---

## 6. 运行时给 LLM 的主要上下文结构

目前进入模型前，最核心的上下文内容主要是：

1. `profile_snapshot`
2. `last_session_summary`
3. `pending_homework`
4. `recent_interventions`
5. `current_focus`
6. `semantic_summary`
7. `formulation`
8. `runtime_time_context`

也就是说，模型看到的不是原始数据库表，而是这些字段整理后的上下文卡片。

### 6.1 Phase Flow State（v2.2 最小版）

当前主 agent + 四阶段子 agent profile 架构的最小 flow state 变量包括：

| 字段名 | 含义 |
|---|---|
| `active_phase` | 当前主导阶段 |
| `intent` | 用户是否明确表达想直接进入方法/练习 |
| `explore` | 当前是否应推进到探索与概念化 |
| `asking` | 当前正在补哪类探索槽位 |
| `formulation_confirmed` | 当前理解是否已足够进入推荐 |
| `needs_more_exploration` | 推荐前是否仍需补信息 |
| `chosen_intervention` | 当前已锁定的候选干预 |
| `intervention_complete` | 当前干预是否已完成 |
| `active_skill` | 当前是否已有执行中的 skill |

---

## 7. 后续优化建议

如果后续要做变量优化，建议优先看这几类问题：

1. `preferences` 是否要区分“技术偏好”和“skill 偏好”
2. `clinical_profile` 是否要加入更稳定的长期主题/价值观字段
3. `homework` 是否要独立成表，而不是继续挂在 `intervention`
4. `recent_intervention` 是否要扩成 `primary_follow_up_intervention`
5. `semantic_summary` 是否要增加“时间新鲜度”或“主线状态”字段
