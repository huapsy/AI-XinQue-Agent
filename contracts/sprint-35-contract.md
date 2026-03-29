# Sprint 35 Contract

## 目标

验证 [`sprint-35-心雀Prompt指南落地.md`](/E:/AI_XinQue_Agent/specs/sprint-35-心雀Prompt指南落地.md) 是否真正把 [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md) 的核心要求落实到心雀运行时 prompt 与相关评估规则。

---

## A. 运行时 Prompt 分层必须覆盖指南核心要求

### 成功标准

[`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) 中的 prompt contract，至少要明确覆盖以下内容：

- 持久人格与回合级控制分层
- 输出契约
- 安全契约
- 对话模型契约
- 工具契约
- 完成契约
- 验证契约
- 长会话契约

并且这些 contract 里必须可断言看见：

- 默认自然 prose，而不是列表或文档腔
- 默认短句、低认知负担
- 默认探索驱动，而不是建议驱动
- 负向 flow 中的“接住 -> 正常化 -> 缩小问题 -> 一个具体问题”微节奏
- 所有理解、总结、归因、机制判断使用“工作性假设”表达

### 失败条件

任一核心规则只存在于设计文档，而未进入运行时 prompt，即视为未完成。

---

## B. Responses-first 语义必须与指南一致

### 成功标准

Prompt 体系和相关运行时说明必须与以下语义保持一致：

- `instructions` 只对当前请求有效
- 跨轮不能把长期契约只放在 `instructions`
- `working_contract` 负责跨轮必须可见的最小行为约束
- `working_context` 负责状态、总结、历史与当前焦点
- `previous_response_id` 只负责串接，不替代产品级 contract

至少应满足以下之一：

- 相关 contract 测试能够断言这些职责存在
- Responses contract 相关测试能够断言这些职责存在

### 失败条件

若代码或测试仍默认把 `previous_response_id` 视为长期 contract 的替代方案，则视为未完成。

---

## C. 用户可见回复风格必须被明确收紧

### 成功标准

运行时 prompt 必须能断言以下规则：

- 普通支持性回复默认不写成列表、编号、小标题块
- 普通支持性回复默认不偏长、不偏重
- 普通支持性回复默认优先探索，不先进入方法清单
- 普通支持性回复默认每轮只往前推进半步

并至少新增对应的 prompt contract 测试，验证：

- 反条列化要求
- 短句低负担要求
- 探索驱动要求

### 失败条件

若这部分仍只有文档描述，而测试无法断言 prompt 中存在相关约束，则视为未完成。

---

## D. “工作性假设”必须成为硬约束

### 成功标准

运行时 prompt 必须明确禁止以下行为：

- 把总结写成确定事实
- 把归因写成确定事实
- 把机制判断写成确定事实
- 把支持性理解写成诊断式结论

并至少新增或更新测试，明确断言：

- prompt 中出现“工作性假设”
- prompt 中出现“不要把总结、归因、机制判断写成确定事实”

### 失败条件

如果“工作性假设”只停留在文档里，或测试没有覆盖，则视为未完成。

---

## E. 审查清单必须至少部分进入测试或评估

### 成功标准

从 [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md) 中抽取关键审查项，至少有一部分被落实到：

- prompt contract tests
- Responses contract tests
- evaluator 检查清单

优先级最高的检查项应包括：

- 默认条列化倾向
- 过早建议化
- 过长、过重
- 把推断写成事实

### 失败条件

若新增内容完全没有进入测试或评估，只是人工约定，则视为未完成。

---

## 验证命令

至少应运行并通过：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_trace.py
& .\app\backend\.venv\Scripts\python.exe -m unittest discover -s app\backend\tests -p "test_*.py"
```

若本轮新增了 Responses contract 或 evaluator 相关测试，也应纳入验证命令与评估报告。
