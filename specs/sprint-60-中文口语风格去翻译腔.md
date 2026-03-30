# Sprint 60 - 中文口语风格去翻译腔

## 背景

当前心雀在流程推进、阶段迁移和行动支持上已经基本可用，但用户试聊反馈暴露出一个明显问题：回复经常“意思对了”，但说法像翻译腔、配音腔或心理咨询教材改写，不够像中国人真实会说的话。

这类问题不会直接破坏 phase flow，却会明显拉低陪伴感、信任感和自然度。

## 目标

把“自然中文口语、少翻译腔、少书面腔”提升为显式 prompt contract，并让 evaluator 能稳定识别这一类缺陷。

## 范围

- system prompt 增加中文口语风格硬约束
- system prompt 增加少量正反例示例，降低翻译腔默认表达
- judge prompt 增加 `translationese` 评分项
- 保持现有 phase flow、tool discipline、structured output 逻辑不变

## 非目标

- 不重写整套人格
- 不改动 Flow Controller 或 phase routing
- 不接入新的前端文案层
- 不做大规模回复模板库

## 预期结果

- 默认回复更短、更口语、更像中文真人在说话
- evaluator 能单独识别“翻译腔/书面腔”缺陷，而不是把它混进泛化的 `summary` 里
