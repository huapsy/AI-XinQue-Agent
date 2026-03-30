# Sprint 39 Contract

## 目标

验证 [`sprint-39-外部向量索引抽象与检索升级.md`](/E:/AI_XinQue_Agent/specs/sprint-39-外部向量索引抽象与检索升级.md) 是否真正把检索层从具体本地实现中抽象出来，并保留清晰回退路径。

---

## A. 检索 backend 必须被抽象出来

### 成功标准

至少能清楚区分：

- embedding 生成
- 向量检索执行
- search_memory 对 backend 的调用

`search_memory` 不应再直接把具体本地打分函数当作唯一主路径写死。

### 失败条件

若只是把旧函数换个名字而没有形成清晰边界，则视为未完成。

---

## B. 必须保留本地 backend 作为默认与回退路径

### 成功标准

- 当前实现仍能在无外部服务时正常工作
- 存在明确的 local backend
- 若未来 external backend 不可用，能清楚回退到 local backend

### 失败条件

若抽象后反而失去当前本地可用性，或没有清晰回退说明，则视为未完成。

---

## C. 检索质量回归样本不能丢

### 成功标准

原有关键检索样本仍需通过，至少覆盖：

- 召回正确历史
- topic 过滤回退
- 时间新鲜度优先

### 失败条件

若抽象后原有检索行为出现明显退化且没有测试保护，则视为未完成。

---

## D. 定向测试必须覆盖 backend 选择或抽象边界

### 成功标准

至少新增或更新测试覆盖：

- local backend 正常路径
- backend 抽象调用边界
- search_memory 的主路径不再直接耦合具体实现细节

### 失败条件

如果只能从人工读代码看出抽象存在，没有测试证据，则视为未完成。

---

## 验证命令

至少应运行并通过与记忆检索相关的定向测试，例如：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_search_memory.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_memory_vectorization.py
```

