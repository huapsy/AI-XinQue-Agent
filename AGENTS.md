# AI心雀（XinQue）

## 项目概述

面向企业员工的 AI 心理健康支持平台。提供情感陪伴、心理咨询与循证干预（CBT、ACT、正念、积极心理学），需要时可转介真人咨询师。

- **定位**：非诊断性工具，不替代专业心理咨询
- **目标用户**：企业员工（B2B2C）
- **产品形态**：独立 Web 应用
- **权威设计文档**：@docs/design/product-plan-v2.md

## 技术栈

| 项 | 选型 |
|---|------|
| LLM | Azure OpenAI GPT-5.4（105万上下文、原生 Skills/Function Calling/Structured Output） |
| 后端 | Python + FastAPI |
| 前端 | React + Vite + TypeScript |
| 数据库 | SQLite（开发阶段）→ PostgreSQL（生产） |
| ORM | SQLAlchemy + Alembic（迁移） |
| 部署 | 独立 Web 应用 |

## 开发工作流（Harness Design）

采用 Anthropic Harness Design 模式，三个 Agent 分工协作，通过文件通信，迭代推进。

### Agent 角色

| Agent | 职责 | 输出位置 |
|-------|------|---------|
| **Planner** | 将需求转为产品规格（不写实现细节） | `specs/` |
| **Generator** | 按 spec 迭代实现代码，每轮自检后提交评估 | `app/` + git commit |
| **Evaluator** | 运行应用，用 Playwright 测试 UI、调用 API、模拟对话，对照 contract 评估 | `evaluations/` |

### Sprint 流程

```
1. 需求描述 → Planner 生成 spec
2. 人工审核 spec
3. Generator + Evaluator 协商 sprint contract（可测试的成功标准）
4. 人工审核 contract
5. Generator 实现代码
6. Evaluator 测试评估
7. 未通过 → Generator 修复 → Evaluator 再评估（自动循环）
8. 通过 → 进入下一个 sprint
```

### 通信文件

- `specs/sprint-XX-功能名.md` — Planner 输出的产品规格
- `contracts/sprint-XX-contract.md` — Generator 与 Evaluator 协商的成功标准
- `evaluations/sprint-XX-eval.md` — Evaluator 的评估报告（通过/不通过 + 问题清单）

## 文档目录治理

以下规则用于明确 `design`、`plans`、`specs`、`contracts`、`evaluations`、`testing` 的定位，避免文档混放。

### 目录定位

- `docs/design/`
  - 权威设计层，回答“系统应该是什么样”
  - 存放产品总方案、系统架构、核心机制、长期有效的运行时约束、稳定变量说明
  - 这里的文档优先级高于 `plans/`、`specs/`
- `docs/plans/`
  - 实施计划层，回答“跨多个 sprint 准备怎么做”
  - 只存放跨多个 sprint 的问题分析与解决计划
  - 这里不是权威产品设计，不应和 `product-plan-v2.md` 并列为真相源
- `specs/`
  - Sprint 规格层，回答“这一轮要交付什么”
  - 存放背景、目标、范围、非目标、预期结果
- `contracts/`
  - Sprint 验收契约层，回答“做到什么算完成”
  - 存放成功标准、证据要求、测试约束
- `evaluations/`
  - Sprint 评估结果层，回答“这一轮实际做到了什么”
  - 存放 PASS / PARTIAL / FAIL、问题清单、验证证据
- `docs/testing/`
  - 测试资产层，回答“怎么测”
  - 存放手动测试清单、测试模板、回归说明，不存放设计或评估结论

### 放置规则

- 如果文档定义长期产品真相、架构原则、核心约束，放 `docs/design/`
- 如果文档描述跨多个 sprint 的问题分析、实施路线、阶段性解决计划，放 `docs/plans/`
- 如果文档定义单个 sprint 的目标与范围，放 `specs/`
- 如果文档定义单个 sprint 的成功标准，放 `contracts/`
- 如果文档记录单个 sprint 的实际结果，放 `evaluations/`
- 如果文档主要用于测试执行，放 `docs/testing/`
- 若 `plans/` 与 `design/` 内容冲突，以 `docs/design/product-plan-v2.md` 为准，再回头修正 `plans/`

### 文件命名规则

- `docs/design/`
  - 产品总方案：`product-plan-vN.md`
  - 实施状态总览：`product-plan-vN-implementation-status.md`
  - 稳定专题设计：`主题名-vN.md` 或 `NN-主题名.md`
  - 这里不要使用 `sprint-XX-...` 命名，除非该文件本身是对 sprint 设计的长期归档说明
- `docs/plans/`
  - 统一命名：`YYYY-MM-DD-主题名-plan.md`
  - 只用于跨多个 sprint 的 plan，不用于单个 sprint
  - 这里不要使用 `sprint-XX-...`、`roadmap`、`overhaul`、`assessment`、`product-plan-...` 命名，避免与其他目录混淆
- `specs/`
  - 统一命名：`sprint-XX-功能名.md`
- `contracts/`
  - 统一命名：`sprint-XX-contract.md`
- `evaluations/`
  - 统一命名：`sprint-XX-eval.md`
- `docs/testing/`
  - 手动测试清单：`manual-test-checklist-vN.md`
  - 测试模板：`test-template-vN.md`
  - 回归说明：`regression-guide-vN.md`

### 执行要求

- 新建文档前，先判断它属于“设计 / 计划 / 规格 / 契约 / 评估 / 测试”哪一层
- 不要把跨多个 sprint 的总路线图写进 `specs/`
- 不要把单个 sprint 的 implementation plan 放进 `docs/plans/`
- 不要把测试清单写进 `docs/design/`
- 不要把评估结果写进 `docs/plans/`
- 如果新增的是 Responses / tools / skills 等专题跨 sprint 计划，默认放 `docs/plans/`，并使用 `*-plan.md` 命名
- 如果新增的是长期有效的架构规则，必须先更新 `docs/design/product-plan-v2.md` 或对应 `design` 文档

## 目录结构

```
AI_XinQue_Agent/                        ← harness 层
├── CLAUDE.md                           ← 本文件
├── docs/
│   ├── design/                         ← 设计文档与参考文献整理
│   │   └── product-plan-v2.md          ← 产品方案（权威设计文档）
│   └── reference/                      ← 参考文献 PDF
├── specs/                              ← Planner 输出
├── contracts/                          ← Sprint 成功标准
├── evaluations/                        ← Evaluator 输出
├── harness/                            ← 编排脚本
│
└── app/                                ← 心雀应用
    ├── backend/
    │   ├── app/
    │   │   ├── main.py                 ← FastAPI 入口
    │   │   ├── agent/                  ← 心雀核心 Agent
    │   │   │   ├── xinque.py           ← 核心 Agent（单一 LLM + Tool Use 循环）
    │   │   │   ├── system_prompt.py    ← System Prompt 构建（人设+阶段指南+安全红线）
    │   │   │   └── tools/              ← Tool 实现（与四阶段对应）
    │   │   │       ├── recall_context.py   ← P1: 回顾用户上下文
    │   │   │       ├── formulate.py        ← P2: 渐进式个案概念化
    │   │   │       ├── match_intervention.py ← P3: 匹配干预方案
    │   │   │       ├── intervention.py     ← P4: load_skill + render_card + record_outcome
    │   │   │       ├── profile.py          ← 跨阶段: 用户画像读写
    │   │   │       └── memory.py           ← 跨阶段: 情景记忆检索
    │   │   ├── analysis/               ← 理解层（结构化分析）
    │   │   ├── safety/                 ← 输入安全 + 输出安全
    │   │   ├── alignment/              ← 对齐评估（贯穿全阶段）
    │   │   ├── profile/                ← 用户画像管理
    │   │   ├── session/                ← 会话管理 + 上下文压缩
    │   │   ├── models/                 ← 数据模型（SQLAlchemy）
    │   │   ├── api/                    ← API 路由
    │   │   └── skill_loader/           ← skill.md 加载与解析
    │   ├── tests/
    │   ├── requirements.txt
    │   └── alembic/                    ← 数据库迁移
    │
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── chat/               ← 对话界面组件
    │   │   │   └── cards/              ← 卡片练习组件
    │   │   └── pages/                  ← 登录、对话、历史
    │   ├── package.json
    │   └── vite.config.ts
    │
    └── skills/                         ← Skill 干预库（.skill.md）
        ├── listening/
        ├── cbt/
        ├── act/
        ├── mindfulness/
        ├── positive_psychology/
        ├── emotion_regulation/
        └── crisis/
```

## 心雀运行时架构

单一核心 LLM + Tool Use 自主推理架构（类 ReAct 模式，Thought 不外显）。

四阶段对话模型：

```
P1 共情倾听 → P2 探索与个案概念化 → P3 推荐与激发 → P4 干预执行
                 ↑ formulation 持续进行 ↑
```

核心设计要点：
- **双维度响应**：内容特征（P0危机>P1术语>P2领域>P3情绪>P4情感）决定「聊什么」，对齐状态（实时独立维度）决定「怎么聊」
- **分层记忆**：工作记忆（上下文窗口）+ 会话记忆 + 情景记忆（embedding 检索）+ 语义记忆（画像+Skill）
- P2 中 case formulation 与探索同步进行（渐进式，非离散后置步骤）
- 硬编码安全层（输入/输出）在 LLM 之前/之后执行，不依赖 LLM
- Tool 集：recall_context、formulate、match_intervention、load_skill、render_card、record_outcome 等

详见 @docs/design/product-plan-v2.md 第 4-7 节。

## 代码规范

### Python（后端）

- 遵循 PEP 8
- 类型注解（type hints）
- docstring 用中文
- 命名：snake_case（变量/函数/模块），PascalCase（类）
- 异步优先（async/await）

### TypeScript/React（前端）

- 函数组件 + Hooks
- TypeScript 严格模式
- 命名：camelCase（变量/函数），PascalCase（组件/类型）
- CSS：Tailwind CSS

### Git

- 每个功能一个分支
- commit message 格式：`feat/fix/refactor: 简要描述`
- 中英文皆可

## 构建与运行

```bash
# 后端
cd app/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd app/frontend
npm install
npm run dev

# 测试
cd app/backend && pytest
cd app/frontend && npm test
```

## 安全红线

以下规则适用于所有 Agent 和代码生成：

1. **不做任何医学/心理诊断**
2. **不推荐药物**
3. **不做绝对化承诺**（"保证好转"）
4. **不讨论政治、宗教等敏感话题**
5. **不说"我理解你想死的感受"**
6. **不提供具体的自伤方式**
7. **检测到自杀/自伤风险时必须提供危机热线**
8. **不鼓励用户停药或放弃专业治疗**
9. **用户数据加密存储，对话内容不向企业暴露**
10. **LLM 输出必须经过输出安全层检查再展示给用户**

## MVP 分期

| Phase | 内容 | 对应 Sprint |
|-------|------|------------|
| **Phase 1 - 核心对话** | Web 前端 + Supervisor + P1/P2 + 理解层 + 基础 Skills + 用户画像 + 安全层 + 对齐基础 | Sprint 01-06 |
| **Phase 2 - 干预能力** | P3/P4 + 完整 Skill 库 + 卡片练习 + 干预追踪 + 完整对齐逻辑 + 会话摘要 | Sprint 07-10 |
| **Phase 3 - 生态完善** | 咨询师外链 + 历史对话 + 跨会话记忆完善 | Sprint 11+ |
| **Phase 4 - 进阶功能** | 管理后台 + 情绪趋势可视化 + 更多 Skill + 效果评估 | Sprint 15+ |

## 参考文档

- @docs/design/product-plan-v2.md — 产品方案 v2（权威，当前版本）
- @docs/design/product-plan-v1.md — 产品方案 v1（已归档，多 Agent 管道架构）
- @docs/design/ — 设计文档与参考文献整理
- @docs/reference/ — 原始参考文献 PDF

## Prompt 约束

- 凡是新增、修改、重构系统 Prompt、工具使用 Prompt、评估 Prompt、结构化输出 Prompt，都必须参考 `docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md`
- 该文件是本项目 Prompt 设计的默认依据，不是可选参考
- 如果实现明确偏离该文件中的建议，需要在对应的 spec、contract、evaluation 或代码说明中写出偏离原因

## OpenAI 协议参考

- 凡是新增、修改、重构 Responses API 链路，必须参考 [Migrate to the Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses) 与 [Text generation](https://developers.openai.com/api/docs/guides/text)
- 凡是新增、修改、重构 tool schema、tool runtime、function calling，必须参考 [Using tools](https://developers.openai.com/api/docs/guides/tools)
- 凡是新增、修改、重构 skill manifest、skill registry、skill 与平台能力的映射，必须参考 [Skills](https://developers.openai.com/api/docs/guides/tools-skills)
- 本项目内部 `skills` 默认视为产品层能力包；若要与官方 Skills 对齐，先更新 [`responses-tools-skills-architecture.md`](/E:/AI_XinQue_Agent/docs/design/responses-tools-skills-architecture.md)
