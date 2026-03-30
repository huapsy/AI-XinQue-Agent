"""联合评估结果读写辅助。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import CombinedEvaluation


async def load_combined_evaluation(db: AsyncSession, session_id: str) -> dict | None:
    """读取指定会话的联合评估结果。"""
    result = await db.execute(
        select(CombinedEvaluation).where(CombinedEvaluation.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    return dict(record.payload or {})


async def list_combined_evaluations(db: AsyncSession) -> list[dict]:
    """读取全部已持久化的联合评估结果。"""
    result = await db.execute(select(CombinedEvaluation))
    records = result.scalars().all()
    payloads: list[dict] = []
    for record in records:
        payload = dict(record.payload or {})
        session_id = getattr(record, "session_id", None)
        if session_id:
            payload.setdefault("session_id", session_id)
        payloads.append(payload)
    return payloads


async def save_combined_evaluation(
    db: AsyncSession,
    session_id: str,
    payload: dict,
) -> CombinedEvaluation:
    """保存指定会话的联合评估结果。"""
    result = await db.execute(
        select(CombinedEvaluation).where(CombinedEvaluation.session_id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        record = CombinedEvaluation(session_id=session_id)
        db.add(record)

    record.payload = payload or {}
    await db.flush()
    return record
