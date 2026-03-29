# Sprint 30 Spec — Responses API 链路与守门补强

## 背景

主对话链路已在 **Sprint 20** 迁移至 **Responses API**，并与 `previous_response_id`、`store`、phase 感知等机制配合运行。近期针对 **GPT‑5.4 / Responses API** 的专项代码审查发现若干与协议和守门逻辑强相关的缺口；若不处理，可能出现：

1. **跨轮延续时系统契约「断档」**
  存在 `previous_response_id` 时不再下发完整 `instructions`（原 `build_system_prompt` 内容），依赖服务商是否在链上持久化首轮指令。若未持久化或策略变化，后续轮次可能缺失人设、安全/工具契约、首轮回合纪律及**对齐警告**等；而当前分层上下文卡片又未显式承载对齐状态，无法可靠补偿。
2. **同一条用户消息内的多步工具链与 Preflight 脱节**
  守门逻辑依赖本地 `messages` 中是否出现 `role: tool` 及工具 JSON，但运行时既不会把本轮工具输出写入该结构，持久化历史也通常只有 user/assistant。结果是：审查中预期的「本轮已 match 则可 load」在真实路径上往往不成立，**同一回合内**先匹配再加载时可能被误拦。
3. **SDK / 协议细节与可运维性**
  工具回传依赖 `call_id` 字段命名；评估与摘要使用字符串 `input` 及裸 `json.loads`，对模型输出形态敏感；`store=True` 与隐私、驻留策略需在产品和配置上可解释；API 版本需与「已开通 Responses」的部署一致。

本 Sprint 聚焦上述与 **Responses 运行时协议** 及 **守门一致性** 直接相关的问题，不扩散为大规模重构。

## 目标

1. 保证在 **使用 `previous_response_id` 延续对话** 时，模型侧仍能稳定获得**应生效的系统级契约**（至少包含：安全与输出约束、工具使用边界、以及对齐状态的可见性之一：通过可合并的 `instructions` 或等价注入到本轮输入上下文）。
2. 保证 **Preflight / 守门** 所依据的「本轮是否已发生某工具及其结果」与 **实际工具执行顺序** 一致，避免误拦合法的多工具单回合流程。
3. 提升 **工具回传、评估解析、存储策略** 对 API/SDK 差异的鲁棒性与可配置性，并在文档或配置说明中明确 **Responses + `store`** 的数据驻留假设。

## 本 Sprint 范围

### 1. `previous_response_id` 路径下的系统契约连续性

**目标**：

- 任意一轮对话（含第二轮及以后）在需要时，模型仍能遵循与产品一致的安全、输出与工具契约；对齐分数变化时，**对齐相关引导**不应静默消失。
- 若平台允许在带 `previous_response_id` 的请求中同时提供与首轮兼容的 `instructions`，应验证行为并采用；若不允许或行为不一致，则必须在 **本轮可验证的输入**（例如 working_context / 开发者消息）中注入**最小等价摘要**，使行为可测、可回归。

**验收要点**：

- 存在历史 trace、`previous_response_id` 非空的会话中，对齐处于「警告」区间时，模型输入侧仍能得到明确的对齐约束信号（通过 instructions 或上下文卡片等可追溯方式）。
- 回合级控制（如首轮回合纪律、长会话纪律）不因仅依赖「首轮 instructions 是否被服务商持久化」而偶然失效；至少具备可配置的明确策略（例如每轮重发摘要指令）。

### 2. Preflight 与本轮工具状态对齐

**目标**：

- `load_skill`、`record_outcome` 等依赖「本轮是否已 match / 是否已 load」的守门逻辑，应以 **当前用户回合内已执行的工具序列或等价状态** 为依据，而非依赖从未填充的 `messages` 中的 `tool` 行。
- 不改变对用户的对外 API 契约；守门仅修正**判断数据源**与**时序**。

**验收要点**：

- 自动化测试覆盖：**单条用户消息**触发先 `match_intervention` 再 `load_skill`（且无特定接受关键词）时，在业务规则允许的前提下不应被错误拦截；与「缺少接受信号应拦截」的用例并存且语义一致。
- `record_outcome` 与「本轮已加载 skill」的关联同样基于真实本轮状态，而非仅历史 DB 中不存在的 tool 消息。

### 3. 工具回传标识符兼容性

**目标**：

- 从 Responses 输出的 function call 项解析用于 `function_call_output` 的标识符时，兼容 `call_id` 与仅提供 `id` 等 SDK 差异，避免因字段名不一致导致工具链中断。

**验收要点**：

- 单测或契约测试覆盖两种字段形态（至少文档化期望行为并有一处回归测试）。

### 4. 评估与摘要的健壮性（Responses 输入）

**目标**：

- LLM-as-Judge 等路径在模型返回带 markdown 围栏或非纯 JSON 时，具备**降级解析**或优先使用**结构化输出能力**（若当前部署支持），避免整条评估流水线因 `json.loads` 失败而中断。
- 会话摘要路径继续基于 Responses；若目标 API 对 `input` 形态有强制要求，应在实现前用当前 `AZURE_OPENAI_API_VERSION` 与部署实测，并在 spec 配套的 contract 中写清输入形态约定。

**验收要点**：

- 评估脚本对「围栏包裹的 JSON」或常见杂质仍能得到结构化分数或明确失败原因，而非未处理异常。
- 摘要失败时现有降级策略保留或增强，不回归用户可见错误。

### 5. `store` 与配置、说明

**目标**：

- `store` 是否开启可通过环境变量（或集中配置）控制，默认行为与当前一致或经产品确认后调整。
- 在面向部署/合规的说明中明确：开启 `store` 时，对话链相关数据在模型服务商侧的驻留含义，以及与本地加密存储策略的关系（不要求法律文案，要求**技术事实描述清楚**）。

**验收要点**：

- 配置项名称、默认值、关闭时对 `previous_response_id` 延续策略的影响在 `contracts` 或 README 片段中有简短说明，避免运维误配。

## 不在本 Sprint 范围

- 不更换模型家族或主部署名称（仍假设 GPT‑5.4 / 当前 Azure 部署）。
- 不实现 Responses **流式**全链路（可作为后续独立 sprint）。
- 不重做前端聊天主界面或新增干预 skill。
- 不解决与 Responses 无关的通用代码清理（归入其他 sprint）。
- 不要求一次性达到完整企业合规认证，仅要求配置与文档层可解释。

## 设计原则

1. **协议行为可测优先**
  凡依赖「服务商是否持久化 instructions」的假设，必须有对应集成或契约测试，或改为不依赖该假设的实现。
2. **守门与真实执行同源**
  Preflight 判断应与本轮实际工具调用记录一致，避免双轨状态。
3. **默认安全、配置显式**
  `store` 关闭若会破坏跨轮 `previous_response_id`，必须在文档中写明，避免静默坏链。
4. **最小有效注入**
  补偿系统契约时优先**最小摘要**而非整段重复完整 system prompt，控制 token 与泄露面；具体长度与结构在实现阶段与 Evaluator 协商。

## 预期产出

- 更新后的 `xinque`（及必要的 `session_context` / 状态注入）行为，满足「跨轮契约连续」验收。
- 更新后的 preflight 或等价守门模块，与本轮工具状态一致。
- `responses_helpers` 或调用侧对 `call_id` / `id` 的兼容。
- 评估/摘要路径的解析或结构化输出改进。
- 环境变量（或配置）控制 `store` + 简短运维说明。
- 配套测试与建议的 `**contracts/sprint-30-contract.md`**（由 Generator 与 Evaluator 协商补全可执行验收项）。

## 验收思路（供 Contract 细化）

1. 模拟「第二轮起带 `previous_response_id`」的对话，断言请求中 **instructions 或等价上下文** 含对齐或契约关键词（或由 Evaluator 用固定用例对话行为判定）。
2. 单回合多工具顺序用例：match → load 在规则允许时不被 preflight 误拦。
3. Mock function call 仅含 `id` 不含 `call_id` 时，工具循环仍可提交 `function_call_output`。
4. Judge 输入带围栏的 JSON 仍可解析出分数字段或进入明确错误处理。
5. 切换 `store` 配置后，文档描述的行为与实际一致（含是否仍可使用跨轮 id）。

## 关联文档

- [Sprint 20 — Responses API 与 Phase 感知迁移](./sprint-20-Responses-API与Phase感知迁移.md)
- [Sprint 29 — 全面审查收口与架构重构](./sprint-29-全面审查收口与架构重构.md)
- 运行时核心：`app/backend/app/agent/xinque.py`、`app/backend/app/responses_helpers.py`、`app/backend/app/session_context.py`、`app/backend/app/evaluation_helpers.py`、`app/backend/app/main.py`

