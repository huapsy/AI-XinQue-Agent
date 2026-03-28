# Sprint 09 Spec — 用户画像完善与 Profile 收口

## 目标

把当前分散在不同流程中的用户画像写入逻辑收拢为稳定的数据模型和统一更新策略，让 `user_profiles` 真正成为跨会话个性化的单一事实来源（single source of truth）。

## 背景

Sprint 01-08 已经完成了核心对话、安全层、个案概念化、干预执行、跨会话连续性、对齐兜底、转介和前端历史会话体验。系统已经具备可用的 MVP 能力，但用户画像层仍处于“部分就位”状态：

- `user_profiles` 表已存在，且已承载 `nickname`、`risk_level`、`alliance`
- 一部分画像信息通过代码流程写入（如 `risk_level`、对齐分数）
- 一部分信息仍散落在 `case_formulations`、`interventions`、`sessions.summary` 中，没有统一聚合出口
- `recall_context()` 虽然能返回昵称、摘要、作业和干预历史，但其返回内容越来越多，缺乏清晰的画像边界

`product-plan-v2` 第 8、9 节要求用户画像承担更强的跨会话个性化能力，因此本 Sprint 的核心任务不是新增更多功能，而是**把已有信息收敛成稳定模型，并明确后续写入口**。

## 本 Sprint 范围

### 1. user_profiles 结构完善

**做**：
- 为 `user_profiles` 明确以下字段边界：
  - `nickname`
  - `risk_level`
  - `alliance`
  - `preferences`
  - `clinical_profile`
- 若当前表结构不足，新增 Alembic 迁移补齐缺失字段
- 明确哪些字段是“聚合视图”，哪些字段是“原始记录来源”

**建议结构**：

```json
{
  "nickname": "阿明",
  "risk_level": "low | medium | high | crisis",
  "alliance": {
    "alignment_score": 12,
    "misalignment_history": []
  },
  "preferences": {
    "preferred_techniques": ["mindfulness"],
    "disliked_techniques": [],
    "communication_style": "gentle"
  },
  "clinical_profile": {
    "key_themes": ["work_pressure"],
    "dominant_emotions": ["anxiety"],
    "cognitive_distortions": ["catastrophizing"],
    "behavioral_patterns": ["avoidance"],
    "mood_trend": "stable"
  }
}
```

**不做**：
- 复杂统计型画像分析
- 画像版本管理

### 2. Profile 更新策略统一

**做**：
- 明确以下写入来源：
  - 输入安全层更新 `risk_level`
  - 对齐追踪更新 `alliance`
  - `formulate()` 在合适时将提炼后的主题、认知扭曲、情绪、行为模式写入 `clinical_profile`
  - 干预完成后，将用户偏好线索写入 `preferences`
- 不要求所有更新都做成 Tool，但必须统一到清晰的后端入口，避免“随手在各处写 JSON”
- 封装 profile merge/update 辅助函数，统一处理 JSON 字段合并

**不做**：
- LLM 任意自由写画像
- 画像的自动过期/衰减策略

### 3. update_profile() Tool 或等价统一入口

**做**：
- 在以下两种方案中选一种并落实：

方案 A（推荐）：
- 新增 `update_profile()` Tool
- 只允许更新有限字段，如 `preferences.communication_style`、`preferred_techniques`、`disliked_techniques`
- LLM 只在用户明确表达偏好时调用

方案 B：
- 暂不暴露 Tool
- 仍由后端代码根据已结构化的数据自动更新 profile

**推荐理由**：
- clinical/risk/alliance 更适合代码驱动
- 用户偏好类信息适合通过 Tool 显式写入

### 4. recall_context() 收口

**做**：
- 调整 `recall_context()` 的返回结构，区分：
  - `profile_snapshot`
  - `last_session_summary`
  - `pending_homework`
  - `recent_interventions`
- 避免继续无边界地往顶层塞字段
- 为 system prompt 补充说明：LLM 应把 profile 当作“参考”，而不是逐字段复述给用户

**不做**：
- 引入 episodic memory（留到 Sprint 10）

### 5. 回归验证

**做**：
- 新增测试覆盖：
  - formulation 写入 profile 的聚合逻辑
  - alliance 更新不覆盖其他 profile 字段
  - recall_context 返回结构稳定
  - 用户表达“我更喜欢短一点、直接一点”的偏好后，profile 能保存

## 用户可感知的变化

本 Sprint 对用户来说不是“看得见的新页面”，而是“心雀记得我且更稳定”：

- 回访时对用户画像的利用更一致，不会一会儿记得、一会儿忘记
- 干预推荐更能参考用户过去偏好
- 对齐状态、风险状态、用户偏好不会彼此覆盖或丢失

## 不在范围

- episodic memory / embedding / `search_memory()`
- Trace 与 OpenTelemetry
- 自动评估体系
- 管理后台 / 趋势图
