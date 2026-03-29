"""时间感知上下文辅助函数。"""

from __future__ import annotations

from datetime import datetime


def build_runtime_time_context(now: datetime | None = None, timezone_name: str = "Asia/Shanghai") -> dict:
    """构造运行时当前时间上下文。"""
    current = now or datetime.now().astimezone()
    return {
        "current_time_iso": current.isoformat(),
        "current_date": current.date().isoformat(),
        "timezone": timezone_name,
    }


def format_relative_time(target: datetime | None, now: datetime | None = None) -> str | None:
    """把绝对时间转换成适合上下文注入的相对时间标签。"""
    if target is None:
        return None
    current = now or datetime.now(target.tzinfo).astimezone(target.tzinfo) if target.tzinfo else datetime.now()
    delta_days = (current.date() - target.date()).days
    if delta_days <= 0:
        return "今天"
    if delta_days == 1:
        return "昨天"
    if delta_days < 7:
        return f"{delta_days}天前"
    if delta_days < 14:
        return "1周前"
    if delta_days < 21:
        return "2周前"
    if delta_days < 30:
        return "3周前"
    return f"{max(1, delta_days // 30)}个月前"
