# Sprint 40 Contract

## 目标

验证 [`sprint-40-生产级可观测平台接入.md`](/E:/AI_XinQue_Agent/specs/sprint-40-生产级可观测平台接入.md) 是否至少补齐了面向 collector 的 OTel 配置边界与启停策略。

---

## A. OTel exporter 配置必须可显式控制

### 成功标准

至少应存在明确配置，用于控制：

- 是否启用 OTel 导出
- collector / endpoint 目标
- service name 等最小资源字段

### 失败条件

若 exporter 仍完全写死在本地 JSONL 文件路径，没有配置边界，则视为未完成。

---

## B. 必须保留安全的本地回退路径

### 成功标准

即使配置 collector 目标，当前实现仍应保留本地安全回退路径或关闭路径，避免在未配置生产环境时直接失败。

### 失败条件

若一旦启用配置就要求真实外部平台存在，否则本地无法运行，则视为未完成。

---

## C. 定向测试必须覆盖启停策略

### 成功标准

至少新增或更新测试覆盖：

- 启用 / 禁用 OTel 导出
- collector / endpoint 配置读取
- 本地回退写入行为

### 失败条件

如果这些配置只能靠人工读代码理解，没有测试证据，则视为未完成。

---

## 验证命令

至少应运行并通过与 OTel helper / settings 相关的定向测试，例如：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_otel_helpers.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_settings.py
```

