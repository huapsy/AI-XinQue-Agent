# Sprint 30 Contract — Responses API 链路与守门补强

对应规格：[specs/sprint-30-Responses-API链路与守门补强.md](../specs/sprint-30-Responses-API链路与守门补强.md)。

## 范围

仅覆盖规格中列出的五项：**跨轮系统契约连续性**、**Preflight 与本轮工具状态对齐**、**function_call 标识符兼容**、**评估/摘要解析健壮性**、**`store` 可配置与说明**。  
不包含 Responses 流式全链路、不换模型、不重做聊天主 UI。

## 成功标准

### A. 跨轮 `previous_response_id` 与系统契约

1. **每轮请求对模型可见的契约不「静默丢失」**  
   当调用 `client.responses.create` 且传入非空 `previous_response_id` 时，实现必须保证本轮仍向模型提供与产品一致的**最小系统契约**，至少包括：
   - 安全与输出相关约束的摘要或可合并的完整 `instructions`（二者择一或组合，由实现选定，但须可测）；
   - **对齐状态**：当传入的 `alignment_score` 落在规格所述「警告」区间（与 `build_system_prompt` 中 `alignment_score <= 5` 或 `<= 0` 的阈值一致）时，模型输入中须出现**明确可断言**的对齐引导文案（不得仅依赖「服务商是否持久化首轮 instructions」）。

2. **回合级控制可测**  
   首轮回合纪律与长会话纪律（`turn_number` 相关）在带 `previous_response_id` 的轮次中仍生效，或实现**显式策略**（如每轮注入回合摘要）；须在自动化测试中至少覆盖一种可断言行为（例如：`turn_number <= 2` 与 `turn_number >= 6` 时，请求中 instructions 或注入块包含约定关键词或互斥片段）。

### B. Preflight 与本轮工具执行同源

3. **`load_skill` 守门**  
   在同一用户回合内（单次 `xinque.chat` 调用、多轮 LLM→工具循环），若已在该回合内成功执行 `match_intervention` 且返回的 JSON 中包含与本次 `load_skill` 参数一致的 `skill_name`，则**不得**仅因「用户消息中缺少接受类关键词」而返回 `missing_acceptance_signal` 拦截（在其余业务规则未触发拦截的前提下）。

4. **`record_outcome` 守门**  
   在同一用户回合内已成功执行 `load_skill` 且 skill 名称与 `record_outcome` 参数一致时，**不得**仅因历史 `messages` 中无 `role: tool` 而返回 `missing_intervention_context`（在载荷满足 `insufficient_outcome_payload` 以外规则的前提下）。

5. **负例仍成立**  
   保留并继续通过：无接受信号、且**同一回合内**也未发生匹配该 skill 的 `match_intervention` 时，`load_skill` 仍应被合理拦截（与现有 `test_xinque_guardrails` 语义一致）。

### C. Function call 输出标识符

6. **兼容 `call_id` 与 `id`**  
   从 Responses 输出的 function call 项构造 `function_call_output` 时，须支持：
   - 仅存在 `call_id`；
   - 仅存在 `id`（且无 `call_id`）；  
   二者至少各有一条单元测试或等价契约测试，且提交的 `call_id` 字段与 API 要求一致。

### D. 评估与摘要

7. **LLM-as-Judge 解析**  
   `run_llm_judge`（或封装路径）在模型返回内容外层包含 markdown 代码围栏（如 ` ```json `）或前后空白/说明性一行时，仍能解析出 JSON 并得到各分数字段；若仍无法解析，须返回**结构化错误对象**（或抛出带类型的应用异常并在调用方记录），**不得**裸 `json.loads` 未捕获导致评估脚本静默崩溃。

8. **会话摘要**  
   `_generate_summary` 在 LLM 调用失败时仍走降级路径，不引入新的未处理异常到 `/api/sessions/{id}/end`；对当前部署，`input` 使用字符串或消息列表须在评估报告中注明实测结论（与 `AZURE_OPENAI_API_VERSION` 一致）。

### E. `store` 与文档

9. **环境变量**  
   提供环境变量 **`XINQUE_RESPONSES_STORE`**（或写入本 Contract 修订后的最终名称，但须在「配置约定」一节登记）：
   - 默认值为 **`true`**（与当前线上行为一致：允许跨轮 `previous_response_id` 依赖服务端存储）；
   - 设为 `false` / `0` / `off`（实现须明确支持的假值集合）时，`responses.create` 对应参数为不存储；**若**此时跨轮 `previous_response_id` 在技术上必然失效，须在 `app/backend/README.md`（或项目根 README 的「后端环境变量」小节）中用**不超过一段**说明该行为，避免运维误配。

10. **技术事实说明**  
    在同一段 README 或 `docs/` 下简短说明（可与上条合并）：开启 `store` 时，对话链相关数据可能由模型服务商按 Responses API 策略保留；与本地消息加密存储的关系用技术语言写清即可（不要求法律合规全文）。

## 配置约定（实现后必填）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `XINQUE_RESPONSES_STORE` | `true` | 为 `false` 时关闭 Responses `store`；跨轮 id 行为见 README |

若实现选用其他变量名，Evaluator 应要求同步更新本表与 README。

## 自动化验证

1. `cd app/backend && pytest` 全量通过。
2. 新增或更新测试须覆盖：**A**（带 `previous_response_id` 时对 `create` 的 kwargs 或注入内容断言）、**B**（同回合 match→load、load→record）、**C**（双标识符形态）、**D**（围栏 JSON 的 judge 解析）。
3. 不强制要求 Playwright；若契约项仅能通过集成测验证，允许使用 `AsyncMock` + 对 `responses.create` 的 `await_args` 断言，与现有 `test_xinque_trace.py` 风格一致。

## 评估结论规则

| 结论 | 条件 |
|------|------|
| **FAIL** | 任一成功标准 A–E 未满足；pytest 失败；`store` 无配置或文档缺失 |
| **PARTIAL** | 核心 B+C 完成，但 A 仅部分注入（无对齐可测信号）或 D 仅 judge 未覆盖摘要 |
| **PASS** | A–E 全部满足，自动化验证通过，README/配置表已更新 |

## 评估产出

- Evaluator 填写 `evaluations/sprint-30-eval.md`，对照本 Contract 逐条勾选并附测试命令与结果摘要。
