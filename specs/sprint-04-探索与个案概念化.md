# Sprint 04 — 探索与个案概念化

## 目标

实现 P2 阶段的核心能力：`formulate()` Tool。让心雀在探索对话中能渐进式构建个案概念化（case formulation），识别用户的情绪、认知模式、行为模式和问题维持机制。

## 背景

Sprint 03 心雀有了安全层和 recall_context()。当前心雀能共情倾听（P1），但进入 P2 后只能靠 LLM 自身推理理解用户——没有结构化的记录和累积。

v2 架构要求 formulate() 是 P2 的主力工具：
- 边探索边调用，每次传入新发现的临床观察
- Tool 内部合并增量信息，返回当前 formulation 状态
- readiness 字段帮助 LLM 判断是否可以进入 P3

## 本 Sprint 范围

### 1. case_formulations 表

**做**：
- Alembic 迁移新增 case_formulations 表
- 字段：formulation_id, session_id, user_id, readiness, primary_issue, mechanism, cognitive_patterns (JSON), emotional_state (JSON), behavioral_patterns (JSON), context (JSON), severity, alliance_quality, missing (JSON), created_at, updated_at

### 2. formulate() Tool

**做**：
- `app/backend/app/agent/tools/formulate.py`
- Tool 定义（OpenAI Function Calling 格式），参数：emotions, cognitions, behaviors, context, alliance_signal
- execute()：
  - 首次调用：创建新 formulation 记录
  - 后续调用：合并增量信息到现有 formulation
  - 根据已收集信息的完整度自动计算 readiness（exploring / sufficient / solid）
  - 根据已有认知+情绪+行为模式自动生成 mechanism 描述
  - 返回完整 formulation JSON
- readiness 计算逻辑：
  - exploring：缺少认知模式或缺少情绪或缺少行为模式
  - sufficient：认知、情绪、行为三个维度都有至少一条记录，且有 primary_issue
  - solid：sufficient 基础上，有 mechanism 描述，missing 为空或只有低优先级项

### 3. 昵称自动提取与保存

**做**：
- 心雀得知用户昵称后（通过 LLM 对话自然获取），需要存入 user_profiles.nickname
- 实现方式：新增 `save_nickname()` Tool，LLM 在得知用户称呼后调用
- 这样 recall_context() 下次能返回昵称

### 4. Agent 集成

**做**：
- 在 xinque.py 中注册 formulate 和 save_nickname Tool
- 更新 System Prompt 中的 Tool 使用指南，指导 LLM 何时调用 formulate()

### 5. 前端无变化

本 Sprint 纯后端改动，前端无需修改。

## 用户可感知的变化

对话体验本身变化不大（LLM 原本就能做共情和探索），但后端现在有了结构化的个案概念化记录。这为 Sprint 05 的 match_intervention()（P3 推荐）奠定基础——没有 formulation 就无法匹配干预方案。

## 不在范围

- match_intervention()（Sprint 05）
- load_skill() / render_card()（Sprint 06+）
- 对齐分数自动计算（后续 Sprint，当前靠 formulate() 的 alliance_signal 手动传入）
- 情景记忆 embedding
