"""独立会话状态模型读写辅助。"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import SessionState, SessionStateHistory


def _to_payload(record: SessionState | None) -> dict | None:
    if record is None:
        return None
    return {
        "current_focus": record.current_focus or {},
        "semantic_summary": record.semantic_summary or {},
        "stable_state": record.stable_state or {},
    }


async def load_session_state(db: AsyncSession, session_id: str) -> dict | None:
    """读取指定会话的独立状态。"""
    result = await db.execute(
        select(SessionState).where(SessionState.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    return _to_payload(record)


async def load_session_state_with_meta(db: AsyncSession, session_id: str) -> dict | None:
    """读取当前状态及更新时间。"""
    result = await db.execute(
        select(SessionState).where(SessionState.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    payload = _to_payload(record) or {}
    payload["updated_at"] = record.updated_at.isoformat() if getattr(record, "updated_at", None) else None
    return payload


async def load_session_state_history(db: AsyncSession, session_id: str) -> dict:
    """读取指定会话的状态历史。"""
    return await load_session_state_history_filtered(db, session_id)


def _normalize_limit(limit: int | None, default: int = 20, maximum: int = 100) -> int:
    if limit is None:
        return default
    return max(1, min(int(limit), maximum))


async def load_session_state_history_filtered(
    db: AsyncSession,
    session_id: str,
    *,
    limit: int | None = None,
    before_version: int | None = None,
    change_reason: str | None = None,
) -> dict:
    """读取指定会话的状态历史，支持最小分页与过滤。"""
    normalized_limit = _normalize_limit(limit)
    statement = (
        select(SessionStateHistory)
        .where(SessionStateHistory.session_id == session_id)
        .order_by(SessionStateHistory.version.desc(), SessionStateHistory.created_at.desc())
    )
    if before_version is not None:
        statement = statement.where(SessionStateHistory.version < before_version)
    if change_reason:
        statement = statement.where(SessionStateHistory.change_reason == change_reason)

    result = await db.execute(statement.limit(normalized_limit + 1))
    records = result.scalars().all()
    visible_records = records[:normalized_limit]
    has_more = len(records) > normalized_limit
    next_before_version = visible_records[-1].version if has_more and visible_records else None
    return {
        "history": [
            {
                "version": record.version,
                "current_focus": record.current_focus or {},
                "semantic_summary": record.semantic_summary or {},
                "stable_state": record.stable_state or {},
                "change_reason": record.change_reason,
                "change_summary": record.change_summary or {},
                "created_at": record.created_at.isoformat() if getattr(record, "created_at", None) else None,
            }
            for record in visible_records
        ],
        "meta": {
            "limit": normalized_limit,
            "returned": len(visible_records),
            "before_version": before_version,
            "change_reason": change_reason,
            "has_more": has_more,
            "next_before_version": next_before_version,
        },
    }


async def save_session_state(db: AsyncSession, session_id: str, payload: dict) -> SessionState:
    """保存指定会话的独立状态。"""
    result = await db.execute(
        select(SessionState).where(SessionState.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = SessionState(session_id=session_id)
        db.add(record)

    record.current_focus = payload.get("current_focus") or {}
    record.semantic_summary = payload.get("semantic_summary") or {}
    record.stable_state = payload.get("stable_state") or {}
    await db.flush()
    return record


def _normalize_list(values: list[str] | None) -> list[str]:
    return [str(value).strip() for value in (values or []) if str(value).strip()]


def should_create_state_history(previous: dict | None, current: dict) -> tuple[bool, str, dict]:
    """判断当前状态是否值得生成历史版本。"""
    previous = previous or {}
    prev_focus = ((previous.get("current_focus") or {}).get("summary") or "").strip()
    curr_focus = ((current.get("current_focus") or {}).get("summary") or "").strip()

    prev_summary = previous.get("semantic_summary") or {}
    curr_summary = current.get("semantic_summary") or {}
    prev_themes = _normalize_list(prev_summary.get("primary_themes"))
    curr_themes = _normalize_list(curr_summary.get("primary_themes"))

    added_themes = [theme for theme in curr_themes if theme not in prev_themes]
    retained_themes = [theme for theme in curr_themes if theme in prev_themes]
    resolved_themes = [theme for theme in prev_themes if theme not in curr_themes]

    prev_issue = (((previous.get("stable_state") or {}).get("formulation") or {}).get("primary_issue") or "").strip()
    curr_issue = (((current.get("stable_state") or {}).get("formulation") or {}).get("primary_issue") or "").strip()

    diff = {
        "added_themes": added_themes,
        "retained_themes": retained_themes,
        "resolved_themes": resolved_themes,
        "focus_changed": bool(prev_focus and curr_focus and prev_focus != curr_focus),
        "formulation_changed": bool(prev_issue and curr_issue and prev_issue != curr_issue),
    }

    if added_themes or resolved_themes:
        return True, "semantic_summary_changed", diff
    if diff["formulation_changed"]:
        return True, "formulation_changed", diff
    if diff["focus_changed"]:
        return True, "current_focus_changed", diff
    return False, "no_material_change", diff


async def _next_history_version(db: AsyncSession, session_id: str) -> int:
    result = await db.execute(
        select(func.max(SessionStateHistory.version)).where(SessionStateHistory.session_id == session_id)
    )
    current = result.scalar_one_or_none() or 0
    return int(current) + 1


async def save_session_state_with_history(
    db: AsyncSession,
    session_id: str,
    payload: dict,
) -> tuple[SessionState, SessionStateHistory | None]:
    """保存当前状态，并在发生明显变化时追加历史版本。"""
    previous = await load_session_state(db, session_id)
    state = await save_session_state(db, session_id, payload)
    should_create, reason, diff = should_create_state_history(previous, payload)
    if not should_create:
        return state, None

    history = SessionStateHistory(
        session_id=session_id,
        version=await _next_history_version(db, session_id),
        current_focus=payload.get("current_focus") or {},
        semantic_summary=payload.get("semantic_summary") or {},
        stable_state=payload.get("stable_state") or {},
        change_reason=reason,
        change_summary=diff,
    )
    db.add(history)
    await db.flush()
    return state, history
