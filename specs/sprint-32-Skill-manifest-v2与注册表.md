# Sprint 32 - Skill manifest v2 与注册表

## 背景

当前 `app/skills/**/*.skill.md` 已经可以驱动 `match_intervention()` 和 `load_skill()`，但仍更像“带 frontmatter 的说明文档”，不是一个可治理的 skill 系统。

现有问题：

- metadata 字段不统一
- 每次匹配或加载依然可能依赖文件系统扫描
- 缺少版本号、冷却规则、follow-up 规则等运行时元数据
- `load_skill()` 返回内容仍偏裸文本 + 局部推断

## 目标

把现有 skill 库升级为 manifest v2 + registry/index 模式。

完成后应达到：

- 每个 skill 具备统一 manifest v2
- skill 可以被校验、索引、加载
- `match_intervention()` 和 `load_skill()` 以 registry 为主，不再以文件扫描为主

## 范围

### 1. 定义 Skill Manifest v2

新增统一字段集，至少包含：

- `name`
- `version`
- `display_name`
- `category`
- `trigger`
- `contraindications`
- `cooldown_hours`
- `output_type`
- `card_template`
- `estimated_turns`
- `follow_up_rules`
- `completion_signals`

### 2. Skill Registry / Index

新增 skill registry 层，负责：

- 扫描并校验 skill 文件
- 构建标准化 skill metadata
- 供 `match_intervention()` 和 `load_skill()` 查询

### 3. 标准化 Skill Payload

`load_skill()` 返回值要标准化，至少分为：

- `manifest`
- `protocol`
- `render_payload`
- `safety_notes`
- `follow_up_rules`

### 4. Skill 校验与测试

新增 skill manifest validation tests，确保：

- 必需字段齐全
- 枚举值合法
- cooldown / output_type / card_template 等约束有效

## 非目标

- 本轮不接入 OpenAI 官方 hosted Skills
- 不在本轮改前端卡片组件协议

## 验收结果

如果本轮完成，心雀的 `skills` 将从“可读取文档集合”升级成“版本化能力注册表”，为后续与官方 Skills 概念对齐打基础。
