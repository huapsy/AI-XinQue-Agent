# Sprint 43 Contract

## 目标

验证 [`sprint-43-积极情绪首触发Skill路由.md`](/E:/AI_XinQue_Agent/specs/sprint-43-积极情绪首触发Skill路由.md) 是否至少补齐了“积极情绪首触发 skill 路由”的最小闭环。

---

## A. 新 skill 必须符合现有 skill 体系规范

### 成功标准

至少应新增一个合法的 `.skill.md` 文件，并满足：

- manifest v2 必需字段完整
- 能被 skill registry 识别
- 内容体现正向体验巩固目标，而不是普通负向干预

### 失败条件

如果只新增了文案文件，但不能被当前 registry 加载，则视为未完成。

---

## B. Runtime 必须允许正向 sentiment 直达该 skill

### 成功标准

至少应存在受控规则，使：

- 用户刚开始明确表达积极情绪时，可直接加载 `positive_experience_consolidation`
- 不要求先完成 `match_intervention`
- 不放宽其他 skill 的 acceptance guardrail

### 失败条件

如果这条 skill 仍被默认 `missing_acceptance_signal` 阻断，则视为未完成。

---

## C. 必须阻止负面主导场景误入该 skill

### 成功标准

至少应存在明确阻止条件，使：

- 当用户消息中正向表达不清晰
- 或明显由负面情绪主导

系统不会直接进入 `positive_experience_consolidation`

### 失败条件

如果只要消息里出现一点正向词就能误入该 skill，则视为未完成。

---

## D. Prompt 必须显式承认该路径

### 成功标准

Prompt / tool contract 至少应明确说明：

- 用户刚开始明确表达积极情绪或良好状态时
- 可直接加载 `positive_experience_consolidation`

### 失败条件

如果代码里悄悄加了特例，但 prompt 没有承认这是一条合法路由，则视为未完成。

---

## E. 定向测试必须覆盖 skill、runtime 与 prompt

### 成功标准

至少新增或更新测试覆盖：

- skill registry 能加载该 skill
- 正向 sentiment 可直达该 skill
- 负面主导时被阻止
- prompt 中存在对应路由提示

### 失败条件

如果只有代码改动，没有对应测试证据，则视为未完成。

---

## 验证命令

至少应运行并通过以下定向测试：

```powershell
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_skill_registry.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_xinque_guardrails.py
& .\app\backend\.venv\Scripts\python.exe app\backend\tests\test_system_prompt_contract.py
```
