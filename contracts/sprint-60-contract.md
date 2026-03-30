# Sprint 60 Contract

## 成功标准

1. `build_system_prompt` 明确约束中文口语风格，显式压制翻译腔、配音腔、客服腔、教材腔
2. `build_system_prompt` 提供至少一组正反向中文改写示例
3. `run_llm_judge` 的 `prompt_review` 增加 `translationese`
4. `translationese` 被纳入：
   - judge schema
   - prompt_review 归一化
   - combined evaluation payload
5. 现有 prompt contract 测试与 judge evaluation 测试继续通过

## 证据要求

- system prompt 单元测试覆盖口语化硬约束与示例块
- judge evaluation 单元测试覆盖 `translationese`

## 测试约束

- 使用本地单元测试
- 不依赖真实 OpenAI 调用
- 本轮不要求证明所有真实回复都已完全去翻译腔，只要求 runtime contract 与 evaluator contract 已对齐
