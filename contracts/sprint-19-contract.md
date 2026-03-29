# Sprint 19 Contract — GPT-5.4 提示工程与运行契约升级

## 成功标准

1. [`AGENTS.md`](/E:/AI_XinQue_Agent/AGENTS.md) 与 [`CLAUDE.md`](/E:/AI_XinQue_Agent/CLAUDE.md) 明确要求：新增、修改、重构 Prompt 时必须参考 [`docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md`](/E:/AI_XinQue_Agent/docs/reference/gpt-5.4/prompt-guidance-for-GPT-5.4.md)
2. [`system_prompt.py`](/E:/AI_XinQue_Agent/app/backend/app/agent/system_prompt.py) 不再只是单一大段风格说明，而是具备清晰的契约式结构，至少覆盖输出契约、工具契约、完成契约与验证契约
3. 首轮与低上下文阶段的 Tool 路由规则更明确，`recall_context`、`search_memory`、`match_intervention` 的调用前提和边界可在 Prompt 或运行时中清晰验证
4. 当检索结果为空、前置依赖未满足或阶段信息不足时，Agent 不会直接草率结束，而会执行补充探索、回退或显式标记缺失信息
5. `referral`、`save_session`、`record_outcome` 等高影响动作具备轻量 verification loop，可验证其前提、语义与返回结果一致
6. 项目内形成对长会话一致性的明确治理方案，至少体现为 phase-aware / Responses API 迁移准备设计、或当前运行时中的最小长会话治理约束
7. Prompt 组织方式完成“持久人格”与“回合级写作控制”的分层，后续可支持不同场景的局部输出控制
8. 至少存在自动化测试、可重复验证流程或文档化检查点覆盖以上升级，不只停留在主观描述
