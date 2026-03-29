# Sprint 19 Spec — GPT-5.4 提示工程与运行契约升级

## 目标

基于 [`docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md`](/E:/AI_XinQue_Agent/docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md) 对心雀当前的单 LLM + Tool Use 架构做一次“提示工程与运行契约”升级。

本 Sprint 的目标不是更换核心架构，而是在保留现有单体运行时的前提下，补齐 GPT-5.4 文档强调的 Prompt Contract、Tool Contract、Completion Criteria、Verification Loop 与 Long-Session Discipline，使系统从“主要靠 prompt 习惯运行”升级为“靠明确契约稳定运行”。

## 背景

当前心雀的运行时主链路已经成立：

- 后端以 [`main.py`](/E:/AI_XinQue_Agent/app/backend/app/main.py) 为 API 编排入口
- 对话核心以 [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 为单 LLM + Tool Use 循环
- Prompt 主体在 [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)
- 安全、对齐、记忆与 trace 已经形成横切能力

但从 GPT-5.4 参考文档视角看，当前实现仍有几个结构性缺口：

- 对话流程推进过度依赖自然语言提示，而不是显式契约
- 早期回合的 Tool 路由约束还不够硬
- 缺少明确的 completeness / verification 规则
- 长会话治理还未形成 GPT-5.4 推荐的持续一致性设计
- `AGENTS.md` / `CLAUDE.md` 尚未明确规定“写 prompt 时必须参考 GPT-5.4 文档”

因此需要一个独立 Sprint，把 GPT-5.4 参考文档转化成项目级约束，而不是停留在参考资料层。

## 本 Sprint 范围

### 1. 在 `AGENTS.md` 与 `CLAUDE.md` 中加入 GPT-5.4 Prompt 参考要求

**做**：

- 在 [`AGENTS.md`](/E:/AI_XinQue_Agent/AGENTS.md) 与 [`CLAUDE.md`](/E:/AI_XinQue_Agent/CLAUDE.md) 中明确新增一条规则：
  - 凡是新增、修改、重构系统 Prompt、工具使用 Prompt、评估 Prompt、结构化输出 Prompt 时，必须参考 [`docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md`](/E:/AI_XinQue_Agent/docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md)
- 规则中应明确：
  - 不是“可选参考”，而是“默认依据”
  - 若实现与参考文档建议不一致，需要在 spec / contract / PR 说明中写出原因

**不做**：

- 把 `AGENTS.md` / `CLAUDE.md` 改成冗长的 GPT-5.4 文档摘抄
- 在规则中写入与本项目无关的通用提示工程条目

### 2. 把 Prompt 从“风格说明”升级为“结构化契约”

对应建议 1：明确输出契约。  

**做**：

- 重构 [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)，把现有大段自然语言说明整理为可维护的契约分块
- 至少显式引入以下类型的块：
  - 输出契约：回复结构、长度、风格、禁止项
  - 工具契约：每个工具的调用前提、用途边界、禁止误用场景
  - 完成契约：何时视为本轮完成，何时不得提前结束
  - 验证契约：回复前检查安全、阶段适配、工具依赖是否满足
- 保持现有人格与安全红线，但减少“隐含规则”

**验收要点**：

- Prompt 结构比现在更模块化
- 规则是“可执行约束”，不是重复产品描述
- 不丢失现有心雀风格与心理支持边界

### 3. 强化首轮与低上下文阶段的 Tool 路由纪律

对应建议 2：早期低上下文阶段要显式约束工具路由。  

**做**：

- 明确首轮回合的先决步骤：
  - 首轮必须优先考虑 `recall_context`
  - 需要历史事件时先尝试 `search_memory`
  - 未达到 formulation readiness 前不应调用 `match_intervention`
- 视实现复杂度，允许两种落地方式：
  - Prompt 层显式契约增强
  - 在 [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py) 增加最小必要的代码级防呆或 gating
- 若选择代码级 gating，应尽量轻量，不把当前架构改造成重状态机

**验收要点**：

- 首轮工具调用更稳定
- 过早推荐干预的概率下降
- 工具选择更符合阶段逻辑

### 4. 引入依赖检查、完整性检查与空结果恢复策略

对应建议 3：在 Prompt 中显式加入 dependency checks 与 completeness checks。  

**做**：

- 为 Agent 增加明确的依赖检查规则：
  - 推荐干预前检查 formulation 是否足够
  - 使用技能前检查用户是否已接受或选择方案
  - 检索为空时不能立刻下“没有历史/没有匹配”的结论
- 为检索、匹配、会话结束等场景增加空结果恢复逻辑：
  - 至少尝试一次更宽松的策略、改写 query、或退回补充探索
- 为多步骤任务增加完成标准：
  - 没覆盖必要项时不能结束本轮
  - 若信息缺失，要明确标记为缺什么，而不是假装已经完成

**验收要点**：

- Agent 不再因为一次空检索就草率结束
- 推荐和干预链路的前置条件更明确
- 最终回复更少出现“半完成态”

### 5. 为高影响动作增加轻量 verification loop

对应建议 4：在高影响动作前加入验证闭环。  

**做**：

- 在 Prompt 或运行时中，为以下动作加入显式验证步骤：
  - `referral`
  - `save_session`
  - `record_outcome`
  - 任何可能改变风险判断、会话状态、用户偏好的操作
- 验证至少包含：
  - 当前动作是否满足前提
  - 是否有更安全的低风险选项
  - 返回内容是否与动作语义一致
- 对于高风险或不可逆动作，允许保持“先确认、再执行”的策略

**验收要点**：

- 转介、保存会话、记录结果的语义更稳定
- 降低工具被误调用或在错误阶段调用的概率

### 6. 为长会话引入 GPT-5.4 风格的持续一致性设计

对应建议 5：考虑 `phase` / compaction / long-session discipline。  

**做**：

- 评估并设计心雀从当前 Chat Completions 风格调用向更适合长会话的模式演进路径
- 本 Sprint 至少要完成以下之一：
  - 在 spec / contract / runtime 注释中显式引入“phase-aware”设计占位
  - 为未来迁移到 Responses API + `phase` + compaction 建立清晰接口边界
  - 在当前实现中补充对长会话一致性的最小治理规则，如摘要时机、历史重放边界、工作记忆控制
- 若本 Sprint 不直接迁移 API，也必须输出明确的迁移准备设计，而不是口头建议

**验收要点**：

- 长会话治理不再只靠“上下文够大”
- 项目内出现面向未来迁移的明确接口或文档约束

### 7. 拆分“持久人格”与“回合级写作控制”

对应建议 6：把人格和单次输出控制分开。  

**做**：

- 重构 Prompt 组织方式，把以下内容显式分层：
  - 持久人格：心雀身份、语气、边界、专业姿态
  - 安全层规则：绝对红线
  - 流程层规则：P1-P4、工具调用、阶段推进
  - 回合级写作控制：本轮是否要更简洁、只做倾听、只做总结、只给结构化输出等
- 若需要，可把 Prompt Builder 拆成多个函数或模块，而不是单一大常量字符串

**验收要点**：

- Prompt 维护成本下降
- 后续做“只生成摘要”“只做评估”“只输出卡片说明”等场景时更容易局部控制

## 不在范围

- 更换核心模型供应商
- 大规模重写前端
- 上线外部向量数据库
- 完整迁移到 Responses API 并一次性接入全部新能力
- 重构为多服务或多 Agent 运行时

## 建议实现策略

本 Sprint 建议分成三层推进：

1. **规则落地层**
   - 更新 `AGENTS.md` / `CLAUDE.md`
   - 在 spec / contract 中固定 GPT-5.4 Prompt 参考原则

2. **Prompt 契约层**
   - 重构 `system_prompt.py`
   - 为 Tool Use、完成标准、验证闭环补充结构化规则

3. **运行时防呆层**
   - 在不重构整体架构的前提下，为首轮工具路由、空结果恢复、高影响动作加最小代码约束

## 验收标准

- `AGENTS.md` 与 `CLAUDE.md` 明确要求写 prompt 时参考 GPT-5.4 文档
- `system_prompt.py` 从单一大段说明升级为更清晰的契约式结构
- 首轮 `recall_context`、`search_memory`、`match_intervention` 的使用纪律更清晰
- 检索为空、上下文不足、阶段未成熟时，Agent 不会草率结束或过早推进
- 高影响工具调用前有显式 verification 机制
- 长会话治理有明确演进路径或最小实现
- Prompt 内部实现完成“人格层”与“回合控制层”的分离

## 影响范围

- [`AGENTS.md`](/E:/AI_XinQue_Agent/AGENTS.md)
- [`CLAUDE.md`](/E:/AI_XinQue_Agent/CLAUDE.md)
- [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py)
- [`xinque.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/xinque.py)
- 相关 Tool 模块与测试
- 后续的 `contract` / `evaluation` 文档

## 风险与注意事项

- 不要把 GPT-5.4 文档原文机械搬进 prompt；重点是转化为项目内契约
- 不要因为加规则而把 Prompt 膨胀成无法维护的大杂烩
- 不要把当前架构一次性重写成硬状态机；先做最有价值的最小约束
- 对心理支持场景而言，安全边界优先级高于“更聪明的自主性”

## 本 Sprint 完成后的理想结果

完成后，心雀的对话主链路仍然是当前的单 LLM + Tool Use 架构，但它会从“依赖模型大致理解开发者意图”升级为“依赖明确的 GPT-5.4 风格运行契约”。这会直接提升首轮稳定性、阶段推进正确性、长会话一致性，以及后续 Prompt 维护和演进的可控性。
