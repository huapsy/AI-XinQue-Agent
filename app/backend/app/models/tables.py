"""SQLAlchemy ORM 模型定义"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    nickname: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_id: Mapped[str] = mapped_column(Text, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    profile: Mapped["UserProfile | None"] = relationship(back_populates="user", uselist=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.user_id"), primary_key=True)
    nickname: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_count: Mapped[int] = mapped_column(default=0)
    risk_level: Mapped[str] = mapped_column(Text, default="none")  # none|low|medium|high|crisis
    alliance: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {alignment_score, misalignment_history}
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    clinical_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    user: Mapped["User"] = relationship(back_populates="profile")


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.user_id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opening_mood_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    closing_mood_score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship(back_populates="session", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"))
    role: Mapped[str] = mapped_column(Text)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text)
    tool_calls: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    session: Mapped["Session"] = relationship(back_populates="messages")


class CaseFormulation(Base):
    __tablename__ = "case_formulations"

    formulation_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"))
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.user_id"))
    readiness: Mapped[str] = mapped_column(Text, default="exploring")  # exploring|sufficient|solid
    primary_issue: Mapped[str | None] = mapped_column(Text, nullable=True)
    mechanism: Mapped[str | None] = mapped_column(Text, nullable=True)
    cognitive_patterns: Mapped[list | None] = mapped_column(JSON, nullable=True)
    emotional_state: Mapped[list | None] = mapped_column(JSON, nullable=True)
    behavioral_patterns: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
    alliance_quality: Mapped[str | None] = mapped_column(Text, nullable=True)
    missing: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class Intervention(Base):
    __tablename__ = "interventions"

    intervention_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"))
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.user_id"))
    skill_name: Mapped[str] = mapped_column(Text)
    target_issue: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed: Mapped[bool] = mapped_column(default=False)
    user_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)  # helpful|neutral|unhelpful
    key_insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    homework_assigned: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    homework_completed: Mapped[bool] = mapped_column(default=False)


class EpisodicMemory(Base):
    __tablename__ = "episodic_memories"

    memory_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(Text, ForeignKey("users.user_id"))
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"))
    content: Mapped[str] = mapped_column(Text)
    topic: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    @classmethod
    def select_by_user(cls, user_id: str):
        """按用户查询情景记忆。"""
        from sqlalchemy import select

        return select(cls).where(cls.user_id == user_id)


class TraceRecord(Base):
    __tablename__ = "traces"

    trace_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"))
    turn_number: Mapped[int] = mapped_column(Integer, default=1)
    input_safety: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    llm_call: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_safety: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    total_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    @classmethod
    def select_by_session(cls, session_id: str):
        """按会话查询 trace。"""
        from sqlalchemy import select

        return select(cls).where(cls.session_id == session_id).order_by(cls.turn_number)


class SessionState(Base):
    __tablename__ = "session_states"

    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"), primary_key=True)
    current_focus: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    semantic_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    stable_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class SessionStateHistory(Base):
    __tablename__ = "session_state_history"

    history_id: Mapped[str] = mapped_column(Text, primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(Text, ForeignKey("sessions.session_id"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    current_focus: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    semantic_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    stable_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
