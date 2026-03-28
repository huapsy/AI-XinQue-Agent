# Sprint 15 Spec — 向量记忆升级与趋势深化

## 目标

把当前“轻量可用版”的情景记忆与情绪趋势，升级成更接近 `plan-v2` 目标态的版本。

## 背景

Sprint 10 与 Sprint 12 已经把跨会话记忆和情绪趋势打通，但仍有两个明显限制：

- `search_memory()` 仍依赖 token overlap，而不是真正的 embedding 检索
- 情绪趋势目前只有平均分、最近一次和简单文案，不是稳定的趋势分析

## 本 Sprint 范围

### 1. 真实 embedding 生成

**做**：
- 为 `episodic_memories` 增加真实 embedding 生成路径
- 明确 embedding provider 和失败降级策略

### 2. 向量检索

**做**：
- 替换或增强当前 `rank_memories_by_query()`
- 让 `search_memory()` 先用向量召回，再做必要过滤
- 保留最小回退路径，避免 embedding 服务异常时完全不可用

### 3. 趋势判断升级

**做**：
- 在 mood trend payload 中补充：
  - trend direction
  - volatility / 波动性
  - recent streak / 最近趋势窗口
- 前端文案与图形据此更新

### 4. 回归测试

**做**：
- 检索质量与回退路径测试
- 趋势判断与前端 payload 测试

## 不在范围

- 多模态记忆
- 长期知识图谱
- 管理后台运营分析
