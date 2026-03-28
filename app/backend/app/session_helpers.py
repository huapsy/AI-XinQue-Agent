"""会话摘要与持久化辅助函数。"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.encryption_helpers import decrypt_text, encrypt_text
from app.models.tables import Message, Session
from app.privacy_helpers import redact_sensitive_text


def build_session_summary(messages: list[Message]) -> str:
    """从会话消息构建最小摘要。"""
    user_texts = [decrypt_text(msg.content) for msg in messages if msg.role == "user"]
    assistant_texts = [decrypt_text(msg.content) for msg in messages if msg.role == "assistant"]
    if not user_texts:
        return ""
    fragments = [user_texts[0]]
    if len(user_texts) > 1:
        fragments.append(user_texts[-1])
    if assistant_texts:
        fragments.append(f"心雀回应：{assistant_texts[-1]}")
    return redact_sensitive_text(" / ".join(fragment for fragment in fragments if fragment), limit=240)


async def save_session_summary(db, session_id: str) -> dict:
    """为指定 session 生成摘要并结束会话。"""
    session_result = await db.execute(select(Session).where(Session.session_id == session_id))
    session = session_result.scalar_one_or_none()
    if session is None:
        return {"status": "not_found", "session_id": session_id, "summary": None}

    message_result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    )
    messages = message_result.scalars().all()
    summary = build_session_summary(messages)
    session.summary = encrypt_text(summary)
    if session.ended_at is None:
        session.ended_at = datetime.now(timezone.utc)
    await db.flush()
    return {"status": "ok", "session_id": session_id, "summary": summary}
