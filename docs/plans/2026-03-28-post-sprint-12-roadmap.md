# Post Sprint 12 Roadmap

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Define the next sprint set after Sprint 12 based on the implementation status gaps and Claude Code review findings.

**Architecture:** The next phase should fix the remaining plan-v2 contract gaps first, then separate rendering and session control concerns, then upgrade memory/observability, and only after that move into production-grade security and admin capabilities.

**Tech Stack:** Python, FastAPI, SQLAlchemy, React, Vite, Azure OpenAI, future vector store / OpenTelemetry

---

## Sequencing Rationale

### Sprint 13

先补 `P0` 缺口：

- `record_outcome(completed=true)` → alignment `+5`
- `save_session()` Tool 化

这一步改动小，但能补上 `plan-v2` 中最关键的正反馈闭环和主动结束会话能力。

### Sprint 14

再处理 `render_card()`：

- 将卡片渲染从 `load_skill()/referral()` 结果中解耦
- 给前端补更通用的 card renderer

这样后面 Skill 扩展和更多卡片类型才不会继续堆在一个组件里。

### Sprint 15

之后升级“最小版”的两项：

- 轻量记忆检索 → 真正 embedding / 向量检索
- 简化趋势图 → 更明确的趋势分析

这一步属于把 MVP 能力推向真正可扩展的版本。

### Sprint 16

再把 trace 从“能诊断”推进到“可运营”：

- OTel 真接入
- 匿名统计页
- 基础 dashboard / metrics

### Sprint 17

最后做企业准备项：

- 字段级加密
- 更明确的数据安全边界
- 生产化安全收口

### Sprint 18

再做一轮审查问题收口：

- 移除固定默认加密密钥兜底
- 修复 `record_outcome(completed=true)` 被 `user_feedback` 误门控的问题
- 让 `save_session()` 真正结束会话
- 修正匿名统计页与 hash 路由的不一致
- 同步纠偏 `Sprint 13/14/16/17` 的文档表述

## Output Set

本轮准备以下文档：

1. `specs/sprint-13~17-*.md`
2. `contracts/sprint-13~17-contract.md`
3. `evaluations/sprint-13~17-eval.md`
4. 如进入审查收口阶段，再补 `Sprint 18` 文档

## Notes

- 这些 sprint 是基于当前 `product-plan-v2-implementation-status.md` 的缺口倒推出来的
- 如果后续优先级变化，优先调整这个 roadmap，再同步改 spec/contract/eval
