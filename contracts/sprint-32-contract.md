# Sprint 32 Contract

## 目标

验证 skill 系统已从前置 metadata + 文件扫描模式，升级为 manifest v2 + registry/index 模式。

## 成功标准

### A. Skill manifest v2 已定义

- 至少 3 个真实 skill 文件已升级到 manifest v2
- manifest 包含 `name / version / category / cooldown_hours / follow_up_rules`
- validation tests 能覆盖缺字段和非法字段

### B. Registry 生效

- 项目存在统一 skill registry/index 模块
- `match_intervention()` 不再直接依赖每次 `rglob` 扫描作为主路径
- `load_skill()` 通过 registry 获取标准化 skill 数据

### C. 标准化 payload 生效

- `load_skill()` 返回标准化对象
- 测试可断言存在 `manifest` 和 `protocol`
- 若 skill 缺失或非法，返回结构化错误结果

### D. 回归通过

- skill 相关定向测试通过
- 后端全量测试通过

## 证据

- `app/backend/tests/test_skill_registry.py`
- `app/backend/tests/test_skill_manifest_validation.py`
- `app/backend/tests/test_load_skill.py`
- `python -m unittest discover -s app/backend/tests -p "test_*.py"`
