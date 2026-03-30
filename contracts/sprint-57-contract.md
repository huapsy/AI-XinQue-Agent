# Sprint 57 Contract

## 目标

把 session 联合评估结果持久化，使 `combined-evaluation` 具备可复用的评估存储基线。

## 成功标准

1. 存在联合评估结果持久化模型
   - 至少包含：
     - `session_id`
     - `payload`
     - `updated_at`

2. 存在读取 / 保存 helper
   - 可按 `session_id` 读取
   - 可 upsert 保存

3. `combined-evaluation` 接口会保存结果
   - 返回结构仍保持不变
   - 评估结果写入存储

4. 有测试覆盖
   - store 单测
   - API 单测

## 证据要求

- 模型代码
- store helper 代码
- API 代码
- 定向测试结果

## 非验收项

- 不要求评估结果版本历史
