# Sprint 37 Contract

## 目标

验证 [`sprint-37-状态时间线聚合与运营分析.md`](/E:/AI_XinQue_Agent/specs/sprint-37-状态时间线聚合与运营分析.md) 是否真正把当前“能读的状态和 timeline 原始数据”推进成“可消费的聚合分析视图”。

---

## A. 状态历史读取接口必须具备稳定消费能力

### 成功标准

`state-history` 相关读取至少满足：

- 支持分页或 continuation
- 支持聚焦关键变化，而不是只能全量拉取
- 返回最小消费元信息，例如 `has_more`、continuation token / before version、过滤条件回显

### 失败条件

若消费方仍必须自己遍历全量历史并手工筛选关键变化，则视为未完成。

---

## B. Timeline 读取必须能表达关键 phase 演进

### 成功标准

timeline 相关读取至少能表达：

- 每轮出现过哪些 phase
- 关键切换点
- 最小分页 / 过滤能力

且返回结构应稳定到足以被后续 dashboard 或 evaluator 消费。

### 失败条件

若 timeline 仍只是原始 trace 的机械透传，没有形成可稳定消费的会话级视图，则视为未完成。

---

## C. 必须存在最小运营分析载荷

### 成功标准

至少新增一个面向运营 / 评估消费的聚合视图，能直接返回大部分以下信息：

- 当前主线摘要
- 最近关键状态变化
- 最近 phase 演进概览
- 可用于 dashboard 的稳定字段

### 失败条件

如果本轮只补了过滤分页，没有新增聚合分析载荷，则视为部分完成，不算完全通过。

---

## D. 聚合逻辑必须有定向测试

### 成功标准

至少新增或更新测试覆盖：

- 状态历史过滤 / continuation
- timeline 聚合 / phase 提取
- 运营分析视图输出

### 失败条件

如果功能只能靠手工接口查看，没有定向测试，则视为未完成。

---

## E. 文档状态必须同步

### 成功标准

至少以下两类文档要同步：

- `spec / contract / eval`
- `docs/design/product-plan-v2-implementation-status.md` 或同类状态文档

### 失败条件

如果代码已改而状态文档仍继续把这部分能力描述为缺失，则视为未完成。

---

## 验证命令

至少应运行并通过与状态查询 / timeline / trace 相关的定向测试，例如：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_session_state_api.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_trace_api.py
```

如果本轮新增了聚合分析 helper 或 endpoint，也必须追加对应测试命令。

