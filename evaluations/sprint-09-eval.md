# Sprint 09 评估报告

**日期**: 2026-03-28
**结果**: ✅ **PASSED**

## 验收结果

| # | 验收标准 | 结果 | 备注 |
|---|---------|------|------|
| 1 | user_profiles 结构完善 | ✅ | 新增 `clinical_profile` JSON 字段 + Alembic 迁移 |
| 2 | 风险与对齐信息不互相覆盖 | ✅ | 统一通过 profile helper 合并，alliance 更新不覆盖其他 section |
| 3 | formulate 聚合入画像 | ✅ | `formulate()` 会把主题、情绪、认知扭曲、行为模式增量写入 `clinical_profile` |
| 4 | 用户偏好可持久化 | ✅ | 新增 `update_profile()` Tool；`record_outcome()` 也会基于 helpful/unhelpful 沉淀偏好 |
| 5 | recall_context 返回结构稳定 | ✅ | 返回 `profile_snapshot / last_session_summary / pending_homework / recent_interventions` |
| 6 | 端到端回访一致性 | ✅ | 新增链路测试覆盖 `formulate → record_outcome → recall_context` |

## 本 Sprint 产出

### 后端新增
- `app/backend/app/profile_helpers.py` — 用户画像 patch/聚合 helper
- `app/backend/app/agent/tools/update_profile.py` — 受限偏好更新 Tool
- `app/backend/alembic/versions/7b8d8ad9c2c1_add_clinical_profile_to_user_profiles.py` — 为 `user_profiles` 新增 `clinical_profile`

### 后端修改
- `app/backend/app/models/tables.py` — `UserProfile` 新增 `clinical_profile`
- `app/backend/app/agent/tools/formulate.py` — formulation 结果聚合回画像
- `app/backend/app/agent/tools/recall_context.py` — 收口为稳定返回结构
- `app/backend/app/agent/tools/record_outcome.py` — 干预反馈反向沉淀偏好
- `app/backend/app/agent/xinque.py` — 注册 `update_profile` Tool
- `app/backend/app/agent/system_prompt.py` — 补充偏好更新与 recall_context 结构说明
- `app/backend/app/main.py` — alliance 更新改为统一 helper 路径

### 数据库迁移
- `7b8d8ad9c2c1_add_clinical_profile_to_user_profiles.py`

### 测试
- `app/backend/tests/test_profile_helpers.py`
- `app/backend/tests/test_recall_context.py`
- `app/backend/tests/test_update_profile.py`
- `app/backend/tests/test_record_outcome_profile.py`
- `app/backend/tests/test_profile_flow.py`
- `python -m unittest discover -s tests -p 'test_*.py'` → 11 tests passed
- `python -m py_compile ...` → passed

## 亮点

- 画像写入首次形成了明确边界：`risk_level / alliance / preferences / clinical_profile`
- `recall_context()` 的返回结构比此前更稳定，适合作为后续 sprint 的长期接口
- 干预反馈不仅被记录，还能沉淀为后续推荐的偏好信号
- 新链路测试已经覆盖从探索到回访的核心画像流转

## 注意事项

- `update_profile()` 当前只开放偏好类字段，属于有意限制，不允许写风险或临床判断
- 本 Sprint 仍未引入 episodic memory / embedding / `search_memory()`，这部分留在 Sprint 10
- 目前测试以 helper 和 mock 驱动的后端测试为主，尚未做真实数据库迁移后的端到端 API 回归
