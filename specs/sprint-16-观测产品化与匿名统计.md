# Sprint 16 Spec — 观测产品化与匿名统计

## 目标

把当前已经存在的 trace 与质量数据，从“开发者可诊断”推进到“团队可运营”。

## 背景

Sprint 11 已有最小 trace，Sprint 12 已有评估与 red team。下一步不是继续堆日志，而是把它们接成更可用的观测与运营视图。

## 本 Sprint 范围

### 1. OpenTelemetry 真接入

**做**：
- 基于现有 trace sink 抽象接入 OTel exporter / adapter
- 保持现有 DB trace 不回退

### 2. 可观测性指标

**做**：
- 产出最小指标：
  - latency
  - tool failure rate
  - safety trigger rate
  - average turns per session

### 3. 管理侧匿名统计页

**做**：
- 落地匿名统计页
- 至少展示：
  - 会话数
  - 平均轮次
  - 干预完成率
  - 安全层触发率

### 4. 评估联动

**做**：
- 将 judge / red team / trace 三类结果形成统一查看入口或统一数据结构

## 不在范围

- 完整企业级 BI 系统
- 复杂权限管理
- 多租户看板隔离
