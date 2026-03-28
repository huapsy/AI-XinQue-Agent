# Sprint 14 Spec — 卡片渲染解耦与多形态 Skill

## 目标

把当前“`load_skill()/referral()` 直接返回 `card_data`”的实现，升级为更接近 `plan-v2` 的显式卡片渲染模型，并让前端具备承接更多 card 类型的能力。

## 背景

目前卡片能力是成立的，但卡片渲染时机仍然隐含在 Tool 返回值里，LLM 不能显式控制“先说一段话，再渲染卡片”还是“只给卡片”。随着 Skill 扩展，这种耦合会让前端和 Tool 返回结构越来越重。

## 本 Sprint 范围

### 1. `render_card()` Tool

**做**：
- 新增 `render_card()` Tool
- 输入接受结构化 card payload
- 输出标准化的 `card_data`
- `load_skill()` 负责返回 protocol / recommended card，而不是直接承担最终渲染职责

### 2. Tool 边界重构

**做**：
- 梳理 `load_skill()`、`referral()`、`render_card()` 三者边界
- 让 `referral()` 也能在必要时走统一 card 渲染路径，或至少对齐 payload shape

### 3. 前端 Card Renderer 扩展

**做**：
- 把当前 `referral / exercise` 二分渲染收敛为更通用的 renderer
- 至少准备 1-2 种新增卡片形态：
  - journal
  - checklist
  - guided_exercise

### 4. Skill 库对接

**做**：
- 补齐若干 Skill frontmatter / content，使其可稳定生成标准 card payload

## 不在范围

- 真正的富交互卡片编辑器
- 管理后台中的 card 配置能力
- OTel / dashboard
