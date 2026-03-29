# Sprint 34 Contract

## 目标

验证系统已形成 Responses-first 的运行时分层，并对官方 Skills 给出清晰的架构对齐边界。

## 成功标准

### A. Runtime contract 已成文并部分落地

- 项目中存在专门的 Responses runtime contract 文档或模块
- `instructions / working_contract / working_context / previous_response_id / store` 的职责有清晰定义

### B. Stateful / Stateless 有行为说明

- `XINQUE_RESPONSES_STORE=true/false` 的行为有明确文档
- 至少有测试覆盖 `store=false` 的受限路径或 fallback 路径

### C. Skills 对齐文档存在

- 新增架构文档说明产品 skill 与官方 Skills 的区别、映射与边界
- AGENTS/CLAUDE 至少一处引用 OpenAI 官方文档作为 prompt / tools / skills 设计参考

### D. 回归通过

- 定向测试通过
- 后端全量测试通过

## 证据

- `docs/design/responses-tools-skills-architecture.md`
- `app/backend/tests/test_settings.py`
- `app/backend/tests/test_xinque_trace.py`
- `python -m unittest discover -s app/backend/tests -p "test_*.py"`
