"""聊天会话相关的数据访问辅助函数。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.encryption_helpers import decrypt_text
from app.models.tables import Message, Session, TraceRecord, User, UserProfile
from app.session_state_store import load_session_state


async def get_or_create_user(db: AsyncSession, client_id: str) -> User:
    """根据 client_id 查找用户，不存在则创建（含画像）。"""
    result = await db.execute(
        select(User).where(User.client_id == client_id).options(selectinload(User.profile))
    )
    user = result.scalar_one_or_none()
    if user is None:
        user = User(client_id=client_id)
        db.add(user)
        await db.flush()
        profile = UserProfile(user_id=user.user_id)
        db.add(profile)
        await db.flush()
        user.profile = profile
    return user


async def create_session_for_user(db: AsyncSession, user_id: str) -> Session:
    """创建新会话，并更新画像的 session_count。"""
    session = Session(user_id=user_id)
    db.add(session)
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile:
        profile.session_count += 1
    await db.flush()
    return session


async def load_history_messages(db: AsyncSession, session_id: str) -> list[dict]:
    """从数据库加载会话历史消息。"""
    result = await db.execute(
        select(Session)
        .where(Session.session_id == session_id)
        .options(selectinload(Session.messages))
    )
    session = result.scalar_one_or_none()
    if session is None:
        return []
    return [{"role": msg.role, "content": decrypt_text(msg.content)} for msg in session.messages]


async def load_previous_response_id(db: AsyncSession, session_id: str) -> str | None:
    """从最近一条 trace 恢复上一轮 Responses response_id。"""
    result = await db.execute(
        select(TraceRecord)
        .where(TraceRecord.session_id == session_id)
        .order_by(TraceRecord.created_at.desc(), TraceRecord.turn_number.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    response_ids = ((getattr(record, "llm_call", None) or {}).get("response_ids")) or []
    return response_ids[-1] if response_ids else None


async def load_previous_session_state(db: AsyncSession, session_id: str) -> dict | None:
    """优先从状态表恢复上一轮持久化状态，缺失时回退到最近 trace。"""
    stored = await load_session_state(db, session_id)
    if stored is not None:
        return stored

    result = await db.execute(
        select(TraceRecord)
        .where(TraceRecord.session_id == session_id)
        .order_by(TraceRecord.created_at.desc(), TraceRecord.turn_number.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if record is None:
        return None
    llm_call = getattr(record, "llm_call", None) or {}
    return llm_call.get("persisted_session_state") or None
