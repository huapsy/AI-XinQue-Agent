# Sprint 25 Spec — 会话状态读取接口与时间线查询

## 目标

在 `Sprint 23/24` 已具备 `SessionState` 与 `SessionStateHistory` 的前提下，补齐会话状态的读取与查询能力。

本 Sprint 的目标是让系统不仅“能存状态”，还“能读状态、看演进、查时间线”，从而支撑调试、评估和后续管理端能力。

## 本 Sprint 范围

### 1. 提供当前会话状态读取接口

**做**：

- 提供读取当前 `SessionState` 的稳定接口或 helper
- 返回：
  - `current_focus`
  - `semantic_summary`
  - `stable_state`
  - 更新时间

**验收要点**：

- 当前状态读取不需要直接查底层表

### 2. 提供状态历史读取接口

**做**：

- 提供读取 `SessionStateHistory` 的接口或 helper
- 返回：
  - version
  - state snapshot
  - `change_reason`
  - `change_summary`
  - 时间

**验收要点**：

- 能看出一段会话状态是如何变化的

### 3. 提供 phase timeline 查询

**做**：

- 从 trace 中提取并汇总 `phase_timeline`
- 提供按会话读取的最小查询能力
- 至少返回每轮的 phase 列表与时间信息

**验收要点**：

- 可以查看一个 session 的 phase/state 推进轨迹

### 4. 保持当前主链路不受影响

**做**：

- 只读接口不改变 chat 主写逻辑
- 不改变 `SessionState` / `SessionStateHistory` 的现有写入契约

**验收要点**：

- 当前对话主链路保持兼容

### 5. 补测试与评估场景

**做**：

- 当前状态读取测试
- 状态历史读取测试
- phase timeline 查询测试
- trace API / 状态 API 回归测试

## 验收标准

- 已提供当前会话状态读取能力
- 已提供状态历史读取能力
- 已提供 session 级 phase timeline 查询能力
- chat 主链路保持兼容
- 至少存在自动化测试或可重复验证覆盖本次改造
