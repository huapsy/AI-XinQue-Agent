# Sprint 31 Contract

## 目标

验证系统已将关键分析链路迁移到 Responses 原生 structured outputs，并保留显式降级与错误观测。

## 成功标准

### A. Judge 走原生 structured output

- `run_llm_judge()` 使用统一 structured output helper
- 单元测试可断言请求参数包含 `text.format`
- 当模型返回合法结构化结果时，函数返回解析后的对象
- 当结构化解析失败时，函数返回结构化错误对象，而不是抛未处理异常

### B. Summary 走原生 structured output

- 会话摘要生成主路径使用 schema 化输出
- 测试可断言成功结果包含摘要文本和最小结构字段
- 当 Responses 调用失败或结构化结果不可用时，现有降级摘要仍可返回

### C. Formulation 主对象 schema 化

- `formulate()` 的主对象以 schema 化结果为主
- 测试至少覆盖 `primary_issue / readiness / missing`
- 写库与后续读取不因 schema 化迁移而破坏

### D. 统一 helper 已落地

- 项目中存在统一 structured output helper
- judge 和 summary 至少都复用该 helper
- helper 具备错误标记或 fallback 元数据

### E. 回归通过

- 定向测试通过
- 后端全量测试通过

## 证据

- `app/backend/tests/test_judge_evaluation.py`
- `app/backend/tests/test_structured_outputs.py`
- `app/backend/tests/test_formulate.py` 或同类测试
- `python -m unittest discover -s app/backend/tests -p "test_*.py"`
