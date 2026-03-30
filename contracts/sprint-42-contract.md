# Sprint 42 Contract

## 目标

验证 [`sprint-42-咨询阶段纪律与四步回复微结构.md`](/E:/AI_XinQue_Agent/specs/sprint-42-咨询阶段纪律与四步回复微结构.md) 是否至少补齐了“跨轮阶段纪律”与“单轮四步回复微结构”的运行时约束。

---

## A. Prompt / runtime 必须明确阶段纪律

### 成功标准

至少应明确表达：

- `P1` 不应写成表单式分流
- `P2` 不应抢跑到建议或干预
- `P3` 必须建立在足够理解之上
- `P4` 必须建立在用户接受练习之上

### 失败条件

如果阶段只停留在标题式罗列，没有足够明确的默认行为和禁止行为，则视为未完成。

---

## B. 探索型单轮回复必须有四步微结构约束

### 成功标准

至少应明确表达：

1. 接住
2. 正常化
3. 缩小问题
4. 一个具体问题

并明确：

- 默认每轮只问一个具体问题
- 不用分类选项或多入口问题替代该结构

### 失败条件

如果只写“半步推进”之类的宽泛描述，没有把四步结构压成更硬的规则，则视为未完成。

---

## C. 评估层必须能识别阶段抢跑与四步缺失

### 成功标准

至少新增或更新评估信号，用于识别：

- 在 `P1 / P2` 轮次中过早建议
- 表单式分流替代咨询式推进
- 单轮缺失“正常化”或“缩小问题”
- 单轮出现多个并列问题

### 失败条件

如果这些问题仍只能靠人工读回复判断，没有结构化评估入口，则视为未完成。

---

## D. 定向测试必须覆盖新约束

### 成功标准

至少新增或更新测试覆盖：

- system prompt 中的阶段纪律
- system prompt / working contract 中的四步结构
- evaluator 对阶段抢跑或四步缺失的识别

### 失败条件

如果只有代码修改，没有测试证明这些约束真的存在，则视为未完成。

---

## 验证命令

至少应运行并通过与 prompt / responses contract / evaluation 相关的定向测试，例如：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_responses_contract.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_judge_evaluation.py
```
