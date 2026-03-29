# Plan-v2 实现差距评估

> 生成时间：2026-03-28
> 评估范围：Sprint 01-08 全部已提交代码

---

## 总体完成度

| Phase | 完成度 | 状态 |
|-------|--------|------|
| Phase 1 核心对话 | **95%** | 基本完整 |
| Phase 2 干预能力 | **90%** | 基本完整 |
| Phase 3 记忆与生态 | **80%** | 大部分完成 |
| **整体** | **~88%** | 相当成熟 |

---

## 一、架构层

### 核心架构 ✅
- 单一核心 LLM + Tool Use 自主推理循环（ReAct 模式）
- 位置：`xinque.py` `chat()` 函数，`finish_reason == "tool_calls"` 循环，最多 10 次迭代
- Tool 调用后追加 `{"role": "tool", "tool_call_id": ..., "content": result}` 到消息历史

### Tool 集 ⚠️（9/11 个）

| Tool | 阶段 | 状态 |
|------|------|------|
| `recall_context` | P1 | ✅ |
| `formulate` | P2 | ✅ |
| `match_intervention` | P3 | ✅ |
| `load_skill` | P4 | ✅ |
| `record_outcome` | P4 | ✅ |
| `update_profile` | 跨阶段 | ✅ |
| `search_memory` | 跨阶段 | ✅ |
| `referral` | 跨阶段 | ✅ |
| `save_nickname` | 跨阶段 | ✅ |
| `render_card` | P4 | ❌ 卡片嵌在 load_skill 返回中，未独立 |
| `save_session` | 跨阶段 | ❌ 通过 API `/end` 端点自动触发，LLM 无法主动调用 |

### 输入/输出安全层 ✅
- 输入安全层（`input_guard.py`）：危机关键词正则（20+ 模式）+ Prompt Injection 防护（9 模式），触发时绕过 LLM
- 输出安全层（`output_guard.py`）：诊断性表述、药物推荐、绝对化承诺检测，触发时替换为安全回复
- 集成位置：`main.py` `chat()` 函数

### 分层记忆 ✅（4 层全实现）
- 工作记忆：会话内消息历史（`messages` 表）
- 会话记忆：上次会话摘要 + 待完成作业（`recall_context()` 返回）
- 情景记忆：`episodic_memories` 表 + `search_memory()` 语义检索
- 语义记忆：`clinical_profile` JSON 字段（认知/情绪/行为模式）

---

## 二、System Prompt（7 个模块）✅（完整度 95%）

| 模块 | 状态 | 说明 |
|------|------|------|
| 1. 身份与角色 | ✅ | "心雀，专业但亲切的心理咨询师" |
| 2. 对话风格规范 | ✅ | 三层结构、共情 5 模式、推进 6 模式、风格原则 6 条 |
| 3. 安全红线 | ✅ | 10 条完整 |
| 4. 双维度响应模型 | ✅ | 维度 A（P0-P4 内容优先级）+ 维度 B（对齐状态） |
| 5. 四阶段对话指南 | ✅ | P1/P2/P3/P4 + 灵活跳步规则 |
| 6. Tool 使用指南 | ✅ | 每个 Tool 的调用时机、参数、返回值解读 |
| 7. 对齐与不对齐应对 | ✅ | `build_system_prompt(alignment_score)` 动态注入兜底提示 |

---

## 三、四阶段 Tool 详细实现

### P1 — recall_context ✅

返回内容（`recall_context.py` 第 80-117 行）：
```json
{
  "profile_snapshot": {
    "nickname", "session_count", "risk_level",
    "alliance", "preferences", "clinical_profile"
  },
  "last_session_summary",
  "pending_homework": [
    { "skill_name", "assigned_date", "description", "frequency" }
  ],
  "recent_interventions": [
    { "skill_name", "date", "completed", "user_feedback", "key_insight" }
  ]
}
```

### P2 — formulate ✅（渐进式，多次调用）

输入（11 个可选字段）：`emotions`, `cognitions`, `behaviors`, `context`, `alliance_signal`, `primary_issue`

输出 readiness 三态：
- `"exploring"` — 信息不足，继续探索
- `"sufficient"` — 核心问题和维持机制已明确，可进入 P3
- `"solid"` — 理解全面，高信心推荐

### P3 — match_intervention ✅

匹配逻辑（基于认知扭曲类型加权）：
- 灾难化/非黑即白 → CBT 认知重构 (+10)
- 反刍思维 → 认知解离 (+9)
- 焦虑情绪 → 正念 (+8)
- 躯体化 → 身体扫描 (+8)
- 消极过滤 → 感恩日记 (+7)
- 恐慌 → 接地练习 (+9)
- 用户偏好 +3，排除不喜欢技术和禁忌

输出：1-2 个方案，含 `skill_name`, `display_name`, `rationale`, `user_friendly_intro`

### P4 — load_skill / record_outcome ✅

- `load_skill`：返回完整协议 + 卡片数据
- `record_outcome`：记录 completed、user_feedback、key_insight、homework_assigned

---

## 四、对齐机制 ⚠️（部分实现）

### 已实现的信号检测（`alignment.py`）

| 信号 | 分数变化 |
|------|---------|
| 不信任（"你只是机器"） | -5 |
| 拒绝（"不想说""算了"） | -5 |
| 不满（"没用""没帮助"） | -3 |
| 不同意（"你说错了"） | -3 |
| 困惑（"什么意思"） | -2 |
| 有帮助/有用 | +3 |
| 同意/认可 | +2 |
| 表达尝试意愿 | +2 |

### 代码层兜底（`main.py`）✅
- 对齐分 ≤5：注入 `ALIGNMENT_WARNING_MILD`（修复关系）
- 对齐分 ≤0：注入 `ALIGNMENT_WARNING_SEVERE`（纯接纳，不推进）

### 缺失
- ❌ 完成干预练习 → +5 分的规则未接入 `record_outcome()` 回调，正向反馈环路断裂

---

## 五、情景记忆 ✅

**EpisodicMemory 表**（`tables.py`）：
```
memory_id, user_id(FK), session_id(FK),
content(TEXT), topic(VARCHAR), emotions(JSON),
embedding(JSON), created_at
```

**自动存储策略**（`memory_helpers.py`）：
- 最小长度 ≥8 字符 + 关键词触发（住院、离职、分手等 14 个）
- token 相似度 ≥0.5 则跳过（去重）
- 自动推断 topic，调用 `redact_sensitive_text()` 脱敏，截断 240 字符

**检索**（`search_memory.py`）：
- 基于 query 的 token 相似度排序
- 支持 topic 过滤，返回 top-k（默认 3）

---

## 六、数据库设计 ✅（8 张表全实现）

| 表 | 关键字段 | 状态 |
|----|---------|------|
| `users` | user_id, client_id, nickname, created/last_seen_at | ✅ |
| `user_profiles` | clinical_profile(JSON), alliance(JSON), preferences(JSON), risk_level | ✅ |
| `sessions` | opening/closing_mood_score, summary | ✅ |
| `messages` | role, content, tool_calls(JSON) | ✅ |
| `case_formulations` | readiness, primary_issue, mechanism, cognitive/emotional/behavioral_patterns(JSON) | ✅ |
| `interventions` | completed, user_feedback, key_insight, homework_assigned(JSON), homework_completed | ✅ |
| `episodic_memories` | content, topic, emotions(JSON), embedding(JSON) | ✅ |
| `traces` | input_safety, llm_call(含tool_calls), output_safety, total_latency_ms(JSON) | ✅ |

---

## 七、可观测性 ✅

每轮 LLM 调用记录完整 Trace：
```json
{
  "input_safety":  { "triggered", "reason", "latency_ms" },
  "llm_call":      { "model", "request_count", "prompt/completion/total_tokens", "latency_ms",
                     "tool_calls": [{ "tool", "arguments", "result", "success", "latency_ms" }] },
  "output_safety": { "triggered", "reason", "latency_ms" },
  "total_latency_ms"
}
```
脱敏：文本限制 120 字符，调用 `redact_sensitive_text()`
查询接口：`GET /api/sessions/{session_id}/traces`

---

## 八、前端集成 ✅

- 会话创建/恢复（含 sessionRestore.ts 策略）
- 卡片渲染：ReferralCard + ExerciseCard（两种类型）
- 情绪签到（MoodCheckin）
- 会话列表 + 情绪趋势
- 消息实时同步

---

## 九、最关键的缺口

### P0 — 对齐正向反馈环路断裂 ⚠️⚠️⚠️

**计划**：完成干预 → `record_outcome(completed=true)` → 对齐 +5
**现状**：record_outcome 记录了 completed，但没有触发对齐分数更新
**影响**：正向强化循环缺失，对齐机制残缺
**修复**：在 `main.py` 的对齐计算逻辑中，检测 `record_outcome` 调用结果，若 `completed=true` 则 +5

### P1 — render_card Tool 未独立 ⚠️⚠️

**计划**：LLM 显式调用 `render_card()` 控制卡片渲染时机
**现状**：卡片数据内嵌在 `load_skill` 和 `referral` 返回中
**影响**：LLM 无法灵活控制卡片展示时机

### P2 — save_session Tool 未独立 ⚠️

**计划**：LLM 可主动调用 `save_session()` 结束会话
**现状**：通过页面卸载 `navigator.sendBeacon()` 或 API `/end` 端点自动触发
**影响**：LLM 无法主动决定何时保存/结束

### P3 — 前端卡片类型有限

目前只支持 referral / exercise 两种卡片，Skill 库中 journal、checklist 类型暂无前端渲染

---

## 十、代码审核关键 Bug（另见完整审核报告）

| 级别 | 文件 | 问题 |
|------|------|------|
| Critical | main.py:265 | 事务管理缺陷，消息与情景记忆可能不一致 |
| Critical | formulate.py:238 | `profile.clinical_profile` 为 None 时 deepcopy 报错 |
| Critical | recall_context.py:62 | `homework_completed == False` 应用 `.is_(False)` |
| Critical | ChatWindow.tsx:152 | sessionId 竞态条件 |
| Major | xinque.py:88 | LLM 循环无超时保护，10 次迭代可能超 200 秒 |
| Major | formulate.py:195 | 并发调用产生重复 CaseFormulation 记录 |
| Major | memory_helpers.py:66 | 中文相似度算法不准，关键记忆可能误判为重复 |

---

## 总结

整体实现质量高，架构严格遵循 v2 设计，安全防护完整，可观测性好。主要缺口：

1. **立即补**：对齐 +5 分闭环（改动小，影响核心机制）
2. **短期补**：render_card Tool 分离
3. **可选**：save_session Tool 显式化、前端卡片类型扩展
