# Sprint 27 Contract

## 范围

本轮只实现“时间新鲜度驱动推理与 Tool 路由”的最小运行时版本：

- recent intervention follow-up guardrail
- `match_intervention` / `load_skill` 的时间新鲜度阻止逻辑
- prompt contract 同步

不包含推荐算法重写，也不包含新的运营查询接口。

## 成功标准

1. 当最近 intervention 在 48 小时内且仍未收口时：
   - `match_intervention` 返回 `status="blocked"`
   - `reason="recent_intervention_needs_follow_up"`

2. 当最近 intervention 在 48 小时内，且本轮要再次加载相同 skill 时：
   - `load_skill` 返回 `status="blocked"`
   - `reason="recent_intervention_needs_follow_up"`

3. 下列情况下仍允许继续：
   - 用户明确要求换方法
   - 用户明确表示旧方法无效/不适合
   - 用户明确要求重新做同一个练习

4. `system_prompt.py` 更新后包含：
   - recent intervention / homework 的 follow-up 优先原则
   - 时间新鲜度对推荐与重做路径的约束说明

5. 自动化验证：
   - `app/backend/tests/test_xinque_guardrails.py` 新增时间新鲜度测试
   - 新测试先红后绿
   - `python -m unittest discover -s app/backend/tests -p "test_*.py"` 通过

## 评估结论规则

- 任一核心时间新鲜度测试失败：`FAIL`
- 只改 prompt 未落运行时 guardrail：`FAIL`
- 定向测试通过但全量回归失败：`PARTIAL`
- 定向测试与全量回归均通过：`PASS`
