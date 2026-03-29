# Sprint 33 Contract

## 目标

验证 tool 系统已经平台化，运行时状态、守门、结果协议和 trace 记录统一。

## 成功标准

### A. Tool registry 存在并被主链路使用

- `xinque.py` 不再手工维护分散注册逻辑作为主路径
- Responses API 的 `tools` 来自统一 registry

### B. Tool state 统一

- 同回合多个 tool 调用共享统一 state
- guardrails 读取统一 state，而不是消息内容猜测
- 测试覆盖 `match -> load -> record` 正反例

### C. Tool result envelope 统一

- 至少核心 tool 返回统一 envelope
- trace 写入可直接消费 envelope

### D. 主循环瘦身

- `xinque.py` 相比当前版本减少 tool-specific 内联逻辑
- tool runtime 有独立测试

### E. 回归通过

- 定向 runtime 测试通过
- 后端全量测试通过

## 证据

- `app/backend/tests/test_tool_runtime.py`
- `app/backend/tests/test_xinque_guardrails.py`
- `app/backend/tests/test_xinque_trace.py`
- `python -m unittest discover -s app/backend/tests -p "test_*.py"`
