"""开发期 SQLite schema 兼容修复。"""

from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.engine import Connection


def ensure_sqlite_compat_schema(connection: Connection) -> None:
    """为旧版 SQLite 数据库补齐当前模型依赖的缺失列。"""
    if connection.dialect.name != "sqlite":
        return

    inspector = inspect(connection)
    table_names = set(inspector.get_table_names())
    if "user_profiles" not in table_names:
        return

    columns = {column["name"] for column in inspector.get_columns("user_profiles")}
    if "clinical_profile" not in columns:
        connection.exec_driver_sql(
            "ALTER TABLE user_profiles ADD COLUMN clinical_profile JSON"
        )
