# Responses / Tools / Skills Architecture

## 定位

本文定义心雀在 `Responses-first` 架构下的运行时分层，并明确项目内部 `skills` 与 OpenAI 官方 `Skills` 的区别、映射与边界。

这是一份长期设计文档，服从 [`product-plan-v2.md`](/E:/AI_XinQue_Agent/docs/design/product-plan-v2.md)。

## 1. Responses-first Runtime Layers

### `instructions`

- 作用：当前请求级高优先级行为约束
- 来源：[`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)
- 特点：
  - 只对本次请求生效
  - 不依赖服务端记忆自动跨轮继承
  - 承载安全契约、阶段契约、工具纪律、完成契约

### `working_contract`

- 作用：跨轮仍必须可见的最小行为契约
- 来源：[`responses_contract.py`](/E:/AI_XinQue_Agent/app/backend/app/responses_contract.py)
- 特点：
  - 仅在 `store=true` 且使用 `previous_response_id` 的 stateful 模式下注入
  - 作为 assistant message 进入输入
  - 补偿 `instructions` 不会自动跨轮延续这一事实

### `working_context`

- 作用：运行时上下文卡片
- 来源：[`session_context.py`](/E:/AI_XinQue_Agent/app/backend/app/session_context.py)
- 内容：
  - 当前目标
  - 稳定状态
  - 语义摘要
  - 检索边界

### `tool_state`

- 作用：本回合工具执行状态
- 来源：[`tool_runtime.py`](/E:/AI_XinQue_Agent/app/backend/app/tool_runtime.py)
- 内容：
  - `tool`
  - `arguments`
  - `call_id`
  - `payload`
  - `error`
  - `status`
  - `phase`
  - `recorded_at`

### `previous_response_id`

- 作用：让 Responses 服务端串接前一轮上下文
- 仅在 `store=true` 的 stateful 模式使用
- 不承载业务契约本身，只承载服务端上下文链路

### `store`

- 作用：决定当前是否启用 Responses 的服务端状态
- 配置：`XINQUE_RESPONSES_STORE`
- 默认：`true`

## 2. Stateful / Stateless 策略

### Stateful 模式

条件：

- `XINQUE_RESPONSES_STORE=true`
- 且存在 `previous_response_id`

行为：

- 使用 `previous_response_id`
- 不重复发送 `instructions`
- 注入 `working_contract + working_context + 当前用户消息`
- tool loop 继续使用服务端 response chain

适用场景：

- 默认产品模式
- 长会话连续支持
- 需要最小化历史重放时

### Stateless 模式

条件：

- `XINQUE_RESPONSES_STORE=false`
- 或虽然传入了 `previous_response_id`，但 store 被关闭

行为：

- 不发送 `previous_response_id`
- 保留 `instructions`
- 回退到完整输入路径
- tool loop 通过本地累积 `function_call_output` 继续当前回合

适用场景：

- 需要禁用服务端状态时
- 未来若做更严格的数据驻留 / ZDR 路径时

当前限制：

- stateless 模式下，跨轮 continuation 会退化为“历史重放 + 本地上下文卡片”
- 若未来需要更强 ZDR，需要进一步设计 encrypted reasoning items

## 3. 产品 Skills 与官方 Skills 的关系

### 当前心雀 `skills`

心雀当前的 `skills` 是**产品层能力包**。

它们负责：

- 心理干预协议
- 卡片渲染提示
- follow-up 规则
- cooldown 与 completion signals
- 干预型对话的业务语义

它们不依赖 OpenAI 平台托管，可由应用独立校验、索引和调用。

### OpenAI 官方 `Skills`

官方 `Skills` 更接近**平台层可挂载能力包**，重点是：

- manifest / metadata
- path-based loading
- 平台运行时可见性
- shell / hosted / local 环境下的能力扩展

### 映射关系

当前心雀 skill manifest v2 中，下列字段未来可直接映射到官方 Skills 风格的 metadata：

- `name`
- `version`
- `display_name`
- `category`
- `trigger`
- `output_type`

下列字段仍然属于产品层协议，不应直接交给平台 Skills 作为唯一真相：

- `contraindications`
- `cooldown_hours`
- `follow_up_rules`
- `completion_signals`
- 具体干预 protocol
- 前端 card 渲染负载

## 4. 设计结论

- 心雀当前以 `Responses` 为对话底座
- `tool` 是运行时执行平台
- `skill` 是产品层能力包

三者关系是：

1. `Responses` 负责推理与会话协议
2. `tools` 负责可执行动作与状态治理
3. `skills` 负责干预知识与业务协议

未来若接入官方 Skills，不应替代心雀产品 skill 系统，而应作为平台层对齐接口。

## 参考

- [Using tools | OpenAI API](https://developers.openai.com/api/docs/guides/tools)
- [Skills | OpenAI API](https://developers.openai.com/api/docs/guides/tools-skills)
- [Migrate to the Responses API | OpenAI API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Text generation | OpenAI API](https://developers.openai.com/api/docs/guides/text)
