# Sprint 29 Contract

## 范围

本轮只做“全面审查收口与架构重构”，不新增业务功能，重点覆盖：

- schema / migration 收口
- Tool schema 源头统一
- 配置环境化
- 前端产品壳层收口
- 运行时职责下沉

## 成功标准

1. Alembic revision 补齐当前主链路所依赖的 schema 变化，至少覆盖：
   - `user_profiles.clinical_profile`
   - `session_states`
   - `session_state_history`

2. 新环境可以通过迁移到达当前 schema；旧环境启动时不会因缺列/缺表在主链路直接报错。

3. 所有 Tool 定义统一为 Responses API 原生格式，运行时代码不再依赖“正式主路径上的 schema 转换层”。

4. 前端 API 地址与后端 CORS origin 已环境化，业务代码中不再残留硬编码 localhost 常量。

5. 前端入口结构完成收口，至少具备：
   - 聊天页入口
   - 历史页入口
   - 管理页入口
   且不再只依赖 `#admin` 作为主要产品分叉方式。

6. `main.py` / `xinque.py` 中至少一类横切逻辑被下沉到单独 helper / service 层，并有对应测试覆盖。

## 自动化验证

1. 补 migration / schema 相关测试或可重复验证。
2. 补 tool schema 统一相关测试。
3. 现有后端全量回归通过。
4. 若涉及前端路由或配置变更，补充最小前端验证或测试。

## 评估结论规则

- 只写文档未改结构：`FAIL`
- 只修单点 bug，未完成源头统一：`FAIL`
- 后端通过但前端入口/配置未收口：`PARTIAL`
- 主路径重构完成且回归通过：`PASS`
