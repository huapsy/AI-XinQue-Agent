"""时间新鲜度排序与多干预优先级辅助函数。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.tables import Intervention


def parse_iso_datetime(value: str | None) -> datetime | None:
    """解析 ISO 时间字符串。"""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def intervention_needs_follow_up(
    intervention: Intervention | None,
    now: datetime | None = None,
    freshness_window: timedelta = timedelta(hours=48),
) -> bool:
    """判断某个 intervention 是否仍需要优先 follow-up。"""
    if intervention is None or intervention.started_at is None:
        return False

    current = _coerce_reference_time(now, intervention.started_at)
    if current - intervention.started_at > freshness_window:
        return False

    if intervention.completed is not True:
        return True

    has_outcome = bool(
        intervention.user_feedback
        or intervention.key_insight
        or intervention.homework_completed
    )
    return not has_outcome


def select_primary_follow_up_intervention(
    interventions: list[Intervention],
    user_message: str,
    now: datetime | None = None,
) -> Intervention | None:
    """从多个 intervention 中挑选当前最值得 follow-up 的主对象。"""
    candidates: list[tuple[tuple[int, int, float], Intervention]] = []
    for intervention in interventions:
        if intervention is None or intervention.started_at is None:
            continue
        current = _coerce_reference_time(now, intervention.started_at)
        age = current - intervention.started_at
        if age > timedelta(days=30) and not _is_specific_intervention_reference(intervention, user_message):
            continue

        specifically_reactivated = _is_specific_intervention_reference(intervention, user_message)
        reactivated = specifically_reactivated or _is_generic_intervention_reference(user_message)
        needs_follow_up = intervention_needs_follow_up(intervention, now=current)

        if needs_follow_up and age <= timedelta(hours=48):
            priority = 0
        elif age <= timedelta(days=7) and (needs_follow_up or specifically_reactivated):
            priority = 1
        elif specifically_reactivated:
            priority = 2
        else:
            continue

        candidates.append(((priority, 0 if specifically_reactivated else 1, -intervention.started_at.timestamp()), intervention))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def sort_memories_with_time_freshness(
    scored_memories: list[tuple[dict[str, Any], float]],
) -> list[dict[str, Any]]:
    """在相关性接近时，优先返回较新的记忆。"""

    def sort_key(item: tuple[dict[str, Any], float]) -> tuple[int, float]:
        memory, score = item
        score_bucket = int(round(score / 0.05))
        created_at = parse_iso_datetime(memory.get("created_at"))
        timestamp = created_at.timestamp() if created_at else 0.0
        return (-score_bucket, -timestamp)

    ranked = sorted(scored_memories, key=sort_key)
    return [memory for memory, score in ranked if score >= 0.18]


def _coerce_reference_time(now: datetime | None, target: datetime) -> datetime:
    if now is None:
        return datetime.now(target.tzinfo).astimezone(target.tzinfo)
    if now.tzinfo is None and target.tzinfo is not None:
        return now.replace(tzinfo=target.tzinfo)
    return now.astimezone(target.tzinfo) if target.tzinfo and now.tzinfo else now


def _is_specific_intervention_reference(intervention: Intervention, user_message: str) -> bool:
    normalized = (user_message or "").lower()
    return intervention.skill_name.lower() in normalized if intervention.skill_name else False


def _is_generic_intervention_reference(user_message: str) -> bool:
    normalized = (user_message or "").lower()
    generic_signals = ("上次", "之前", "前几天", "那个练习", "那个方法", "之前那个")
    return any(signal in normalized for signal in generic_signals)
