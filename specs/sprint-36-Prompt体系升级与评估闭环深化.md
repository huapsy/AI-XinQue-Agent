# Sprint 36 - Prompt 体系升级与评估闭环深化

## 背景

`Sprint 35` 已经完成了 Prompt 指南的首轮落地，把 [`05-心雀Prompt撰写指南-v1.md`](/E:/AI_XinQue_Agent/docs/design/05-心雀Prompt撰写指南-v1.md) 推进到运行时 contract、测试与手测检查项。

但如果按 [`product-plan-v2.1.md`](/E:/AI_XinQue_Agent/docs/design/product-plan-v2.1.md) 第 5.1 节与第 8.4 节继续推进，当前 Prompt 体系仍然只是“第一轮收口”，还没有完全达到下一阶段目标：

- Prompt 分层仍偏静态 contract，离“更强的运行时契约体系”还有距离
- 工具依赖、完成条件、验证闸门、空结果恢复等规则还不够系统
- evaluator 对 Prompt 质量的消费仍偏检查项，没有形成更强的结构化审查闭环
- 长会话、工具循环、phase 漂移控制仍需要更明确的 Prompt 约束

如果你的重点是“继续升级 Prompt”，那么它不应该被视为已完成，而应被正式定义成下一阶段的独立 sprint。

## 目标

本轮 sprint 的目标，是把心雀当前 Prompt 体系从“已落地的首轮 contract”升级为“更强的运行时 Prompt 架构”，并深化与 evaluator / review 的闭环。

完成后应达到：

- Prompt 分层更明确，长期契约与本轮控制边界更清楚
- 工具依赖、完成契约、验证契约、空结果恢复成为更硬的 Prompt 规则
- evaluator 能更直接消费 Prompt 审查信号，而不只依赖人工阅读
- 长会话与工具循环下的 phase 漂移控制更稳定

## 范围

### 1. Prompt 分层升级

继续收口并强化以下层次：

- 持久人格层
- 行为契约层
- 工具契约层
- 完成契约层
- 验证契约层
- 长会话契约层
- 回合级写作控制层
- 动态运行时注入层

重点不是“把 Prompt 写更长”，而是让每一层职责更清楚、互相不混淆。

### 2. 工具依赖与完成闸门强化

将 `plan-v2.1` 和 Prompt 指南里已经明确提出、但尚未完全系统化的规则继续前移到 Prompt 契约，包括：

- 不因目标看起来 obvious 就跳过前置工具
- 空结果或低置信度结果时的恢复策略
- 高影响动作前的确认或依赖检查
- 什么算“本轮完成”，什么仍不算完成

### 3. 长会话与 phase 漂移控制

围绕 Responses-first 长会话要求，补强：

- `phase` 的保持与使用纪律
- 中间 commentary / tool 过渡 / final answer 的区分
- compact / previous_response_id / working_contract / working_context 的职责一致性

### 4. Prompt 审查的 evaluator 闭环深化

将部分 Prompt 审查标准从“测试能断言字符串存在”升级到“evaluator 可以消费的结构化或半结构化信号”，优先覆盖：

- 是否过早建议化
- 是否条列化过强
- 是否过长、过重
- 是否把推断写成事实
- 是否跳过工具依赖或完成闸门

## 非目标

- 本轮不新增大量业务 Tool
- 不重写前端对话 UI
- 不把所有 evaluator 逻辑一次性完全自动化

## 预期结果

如果本轮完成，心雀的 Prompt 不再只是“已有规范与首轮测试”，而会真正成为下一阶段长会话、工具治理和评估闭环的稳定中轴。
