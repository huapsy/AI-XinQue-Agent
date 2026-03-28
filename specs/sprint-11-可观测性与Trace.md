# Sprint 11 Spec — 可观测性与 Trace

## 目标

为心雀建立最小可用的可观测性体系，让每轮对话从输入安全层到 LLM 调用、Tool 调用、输出安全层的完整处理链路都可追踪、可复盘、可诊断。

## 背景

截至 Sprint 10，系统的产品能力已经比较完整，但运维和诊断能力仍然薄弱。出现以下问题时，当前系统排查成本较高：

- 为什么这一轮触发了危机响应？
- 为什么 LLM 在这一轮调用了 `referral()` 而不是 `match_intervention()`？
- 为什么某次回复质量突然下降？
- 为什么某些会话延迟明显升高？

`product-plan-v2` 第 12 节要求记录完整 trace，因此本 Sprint 的重点是**把“会发生什么”变成“可以被看到什么”**。

## 本 Sprint 范围

### 1. traces 表

**做**：
- Alembic 迁移新增 `traces` 表
- 字段建议：
  - `trace_id`
  - `session_id`
  - `turn_number`
  - `input_safety`
  - `llm_call`
  - `output_safety`
  - `total_latency_ms`
  - `created_at`

### 2. 每轮 Trace 生成

**做**：
- 在 `POST /api/chat` 流程中，为每轮对话生成一条 trace
- 至少记录：
  - 输入安全层是否触发、触发原因、耗时
  - LLM 模型名、token、耗时
  - Tool 调用列表（tool 名称、输入摘要、输出摘要、耗时）
  - 输出安全层是否触发、触发原因、耗时
  - 总耗时

**注意**：
- trace 默认用于诊断，不要求在前端实时展示
- Tool 输入输出需要脱敏和截断，不能直接原样无限存储

### 3. Tool 调用日志规范化

**做**：
- 在 Agent Tool Use 循环中，把每次 Tool 调用包装为统一的 trace entry
- 至少记录：
  - tool 名称
  - arguments 摘要
  - result 摘要
  - success / failure
  - latency

**不做**：
- 展示 LLM 原始 chain-of-thought
- 记录未经处理的敏感原文

### 4. 轻量查询入口

**做**：
- 提供最小可用的查询方式之一：
  - 方案 A：新增内部调试 API `GET /api/sessions/{session_id}/traces`
  - 方案 B：先提供后端脚本 / 管理命令查询
- 能查看指定 session 的 trace 列表

### 5. OpenTelemetry 接口预留

**做**：
- 代码中预留 trace adapter 或抽象层
- 先把 trace 写 DB，后续若接 OTel，不必大改业务主流程

**不做**：
- 完整 OTel 后端部署
- Grafana/Jaeger Dashboard

### 6. 质量验证

**做**：
- 新增测试覆盖：
  - 正常对话 trace 正常落库
  - 危机输入绕过 LLM 时 trace 结构仍完整
  - Tool 调用失败时 trace 能记录 failure
  - 脱敏/截断逻辑不泄露敏感长文本

## 用户可感知的变化

本 Sprint 对终端用户几乎无直接 UI 变化，但它会显著提高团队对系统的可控性：

- 出现错误或异常时可以快速定位
- 能基于真实 trace 做质量分析和后续评估
- 为自动评估与安全审计提供基础数据

## 不在范围

- 完整监控面板
- 自动评估打分
- 管理后台
- 用户侧趋势图
