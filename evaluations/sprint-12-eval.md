# Sprint 12 评估报告

**日期**: 2026-03-28
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | LLM-as-Judge 可运行 | ✅ | 新增 `evaluation_helpers.run_llm_judge()` 与 `scripts/run_judge_eval.py`，并有结构化单测覆盖 |
| 2 | Red Team 样本集 | ✅ | 固定样本覆盖 crisis / indirect crisis / injection / diagnosis bait / medication bait / alignment attack |
| 3 | 安全回归可执行 | ✅ | `red_team_runner.run_red_team_suite()` 可重复执行，回归测试已纳入 unittest |
| 4 | 评估与可观测数据有脱敏边界 | ✅ | trace、summary、episodic memory、judge sample 已统一接入 `privacy_helpers.redact_sensitive_text()` |
| 5 | 至少落地一个产品化能力 | ✅ | 已落地用户侧情绪趋势视图 |
| 6 | 全链路验收 | ✅ | 现有 34 条后端测试覆盖 profile flow、memory、referral、trace、red team、judge、trend 等关键链路 |

## 本 Sprint 产出

### 后端新增
- `app/backend/app/privacy_helpers.py` — 脱敏与截断辅助函数
- `app/backend/app/evaluation_helpers.py` — LLM-as-Judge 结构化评估
- `app/backend/app/red_team_runner.py` — 固定安全对抗样本与回归运行器
- `app/backend/app/mood_trend_helpers.py` — 用户侧情绪趋势数据构建
- `app/backend/scripts/run_red_team.py` — red team 回归脚本
- `app/backend/scripts/run_judge_eval.py` — 单次评估运行脚本

### 后端修改
- `app/backend/app/trace_helpers.py` — trace 脱敏统一走 privacy helper
- `app/backend/app/memory_helpers.py` — episodic memory 入库前脱敏
- `app/backend/app/main.py` — summary 脱敏、用户情绪趋势接口 `/api/users/{client_id}/mood-trend`

### 前端修改
- `app/frontend/src/components/chat/ChatWindow.tsx` — 新增情绪趋势卡片与趋势数据拉取
- `app/frontend/src/components/chat/moodTrend.ts` — 趋势文案与 payload 类型

### 数据库迁移 / 数据结构
- 无新增迁移
- 新增趋势 payload / judge 输出 / red team 结果等结构化数据约定

### 测试 / 评估脚本
- `app/backend/tests/test_privacy_helpers.py`
- `app/backend/tests/test_judge_evaluation.py`
- `app/backend/tests/test_red_team_regression.py`
- `app/backend/tests/test_mood_trend_helpers.py`
- `python -m unittest discover -s tests -p 'test_*.py'` → 34 tests passed
- `python -m py_compile app/privacy_helpers.py app/evaluation_helpers.py app/red_team_runner.py app/mood_trend_helpers.py app/trace_helpers.py app/memory_helpers.py app/main.py scripts/run_red_team.py scripts/run_judge_eval.py` → passed
- `npm run build` → passed

## 亮点

- Sprint 12 没有只停留在脚本层，而是把脱敏边界真正接进了 trace、summary 和 episodic memory
- red team 样本已经固定下来，后续任何安全回归都能直接复跑
- 用户侧趋势视图直接复用了已有情绪签到数据，投入小但产品感知明显
- 自动评估、red team、trace 三者现在可以形成统一的质量闭环

## 注意事项

- `run_judge_eval.py` 依赖 Azure OpenAI 环境变量，当前单测通过 mock client 验证结构与调用路径
- 情绪趋势目前基于 `opening_mood_score`，尚未扩展到结束情绪或更复杂的时间序列分析
- 目前仍未接企业级权限系统、可视化运营后台与真实在线评估调度
