# Sprint 35 评估报告

**日期**: 2026-03-29
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---|---|---|
| A1 | 运行时 prompt 分层覆盖指南核心要求 | ✅ | [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) 已明确覆盖短句、低负担、探索驱动、负向 flow 微节奏、工作性假设 |
| B1 | Responses-first 语义与指南一致 | ✅ | [`responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py) 已明确 `instructions / working_contract / working_context / previous_response_id / store` 关系 |
| C1 | 用户可见回复风格被显式收紧 | ✅ | 已新增对“默认短句、非条列化、探索驱动、半步推进”的 contract 和测试 |
| D1 | “工作性假设”成为硬约束 | ✅ | 系统 prompt 与测试均覆盖“不要把总结、归因、机制判断写成确定事实” |
| E1 | 审查清单至少部分进入测试或评估 | ✅ | 已新增 Responses / prompt contract tests，并补入 [`manual-test-checklist-v1.md`](/E:/AI_XinQue_Agent/docs/testing/manual-test-checklist-v1.md) 的风格检查项 |
| F1 | 定向测试通过 | ✅ | `test_responses_contract.py`、`test_system_prompt_contract.py`、`test_xinque_trace.py` 通过 |
| F2 | 后端全量测试通过 | ✅ | 当前 `133` 项测试通过 |

## 本轮实际改动

### 后端实现

- [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)
- [`responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py)

### 测试

- [`test_system_prompt_contract.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_system_prompt_contract.py)
- [`test_responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_responses_contract.py)
- [`test_xinque_trace.py`](/E:/AI_XinQue_Agent/app/backend/tests/test_xinque_trace.py)

### 文档

- [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md)
- [`manual-test-checklist-v1.md`](/E:/AI_XinQue_Agent/docs/testing/manual-test-checklist-v1.md)

## 当前验证证据

- `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_responses_contract.py`
- `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py`
- `& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_trace.py`
- `& .\app\backend\.venv\Scripts\python.exe -m unittest discover -s app\backend\tests -p "test_*.py"`

## 结论

`Sprint 35` 已把 [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md) 从“写作参考”推进到“运行时 prompt contract + 测试 + evaluator 检查项”的闭环。

当前心雀的 prompt 体系已经更明确地体现了产品定位：

- 自然 prose，而不是文档腔
- 短句、低认知负担
- 探索驱动，而不是过早建议化
- 工作性假设，而不是确定性心理判断
