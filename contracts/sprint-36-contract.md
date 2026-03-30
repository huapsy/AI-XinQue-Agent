# Sprint 36 Contract

## 目标

验证 [`sprint-36-Prompt体系升级与评估闭环深化.md`](/E:/AI_XinQue_Agent/specs/sprint-36-Prompt体系升级与评估闭环深化.md) 是否真正把心雀 Prompt 从“首轮落地的 contract”推进到“更强的运行时 Prompt 架构”，并让 evaluator / review 可以更直接消费这些规则。

---

## A. Prompt 分层必须继续收口，而不是只增加文案

### 成功标准

运行时 Prompt 相关模块必须能清晰区分并表达至少以下层次中的大部分：

- 持久人格层
- 行为契约层
- 工具契约层
- 完成契约层
- 验证契约层
- 长会话契约层
- 回合级写作控制层
- 动态运行时注入层

至少应满足以下要求：

- 不是简单把更多规则堆进一个大段 prompt
- 能从代码或文档中看出“长期稳定规则”和“本轮动态控制”的边界
- `working_contract` 与 `working_context` 的职责不被混淆

### 失败条件

如果本轮只是追加散文式 Prompt 文案，而没有让层次与职责更清楚，则视为未完成。

---

## B. 工具依赖、完成契约、验证契约必须更硬

### 成功标准

Prompt 体系中必须能明确断言以下规则至少大部分已成为硬约束：

- 不因目标看起来 obvious 就跳过前置工具
- 工具空结果、过窄结果或低置信度结果时，存在恢复策略
- 高影响动作前要做依赖检查或确认
- “本轮完成”有更明确的定义
- 输出前存在最小验证闸门，而不是想到哪做到哪

至少应新增对应测试或 contract 断言，覆盖：

- 工具依赖顺序
- 完成条件
- 空结果恢复
- 输出前验证

### 失败条件

若这些规则仍然只在设计文档里存在，代码和测试无法证明其进入 Prompt 体系，则视为未完成。

---

## C. 长会话与 phase 漂移控制必须增强

### 成功标准

运行时 Prompt / Responses contract 必须更明确覆盖：

- `phase` 的保留与使用纪律
- 中间 commentary / tool 过渡 / final answer 的区分
- `previous_response_id` 只负责串接，不替代行为契约
- `working_contract / working_context` 与 compaction 语义保持一致

至少应满足以下之一：

- 新增或更新 contract tests，能断言相关职责存在
- 新增或更新 trace / Responses 相关测试，能断言 `phase` 语义没有被弱化

### 失败条件

若本轮没有让长会话和工具循环下的 `phase` / contract 语义更稳定，仍沿用模糊约定，则视为未完成。

---

## D. Prompt 审查必须进入 evaluator 可消费层

### 成功标准

本轮至少要把一部分 Prompt 审查标准从“人工读 prompt”推进到“evaluator / review 可直接消费”，优先覆盖：

- 是否过早建议化
- 是否条列化过强
- 是否过长、过重
- 是否把推断写成事实
- 是否跳过工具依赖或完成闸门

可接受的落地形式包括：

- evaluator 结构化输出字段
- review helper / judge helper 可读取的审查项
- 新增专门 Prompt review contract

### 失败条件

如果 Prompt 审查仍主要依赖人工阅读和手工判断，没有进入 evaluator 可消费层，则视为未完成。

---

## E. 文档、代码、测试三层必须一致

### 成功标准

至少以下三层要同步更新并互相一致：

- 设计 / Prompt 指南或相关 architecture 文档
- 运行时 Prompt / Responses contract 代码
- 测试或 evaluator 检查项

### 失败条件

若三层任意一层明显滞后，导致“文档说一套、代码做一套、测试验另一套”，则视为未完成。

---

## 验证命令

至少应运行并通过与 Prompt / Responses / trace / evaluator 相关的定向测试。推荐最小集合：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_responses_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_trace.py
```

如果本轮引入了新的 evaluator / prompt review 测试，也必须纳入验证证据。

后端全量回归是否要求本轮强制通过，可由 Generator 与 Evaluator 在执行前再次确认；若不跑全量，评估报告必须写明原因与残余风险。

---

## 证据要求

评估报告至少应提供：

- 被修改的 Prompt / Responses contract 文件
- 被新增或更新的测试文件
- 与 Prompt 审查闭环有关的 evaluator / review 入口
- 实际运行过的验证命令与结果

