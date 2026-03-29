# Sprint 28 Contract

## 范围

本轮只实现“时间新鲜度排序与多干预优先级治理”的最小运行时版本：

- `search_memory()` 的时间新鲜度排序
- 多 intervention 场景下的主 follow-up 优先级选择
- 主线 / 背景区分规则
- 最小冷却语义

不包含前端可视化，也不包含推荐引擎重写。

## 成功标准

1. `search_memory()` 在相关性接近时，较新的记忆排在前面。

2. 当用户存在多个 intervention 时，系统可以识别一个主 follow-up 对象，并满足以下优先级：
   - 近 48 小时内且未收口的 intervention 优先
   - 近 7 天内且与当前主题连续相关的 intervention 次优先
   - 更早但被用户主动重新提及的 intervention 可重新进入主线

3. 更早的 intervention 在未被用户重新激活时，不会抢占近期 intervention 的优先级。

4. 短时间内刚做过或刚推荐过的同类 intervention，在没有新证据时不会再次成为首推方案。

5. `system_prompt.py` / retrieval guidance 与运行时规则保持一致，明确：
   - 时间新鲜度影响检索排序
   - 时间新鲜度影响多 intervention follow-up 优先级
   - 旧 intervention 默认进入背景层

## 自动化验证

1. 为 `search_memory()` 新增时间排序测试。
2. 为多 intervention 优先级新增运行时测试。
3. 为“旧 intervention 不抢近期主线”新增测试。
4. `Sprint 27` 的已有 guardrail 测试不能回归失败。
5. `python -m unittest discover -s app/backend/tests -p "test_*.py"` 通过。

## 评估结论规则

- 任一核心排序/优先级测试失败：`FAIL`
- 只更新 prompt 或文档，未落运行时规则：`FAIL`
- 定向测试通过但全量回归失败：`PARTIAL`
- 定向测试和全量回归均通过：`PASS`
