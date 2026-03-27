"""心雀后端服务入口"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncAzureOpenAI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from app.agent import xinque
from app.alignment import detect_alignment_signal
from app.models.database import engine, get_session
from app.models.tables import Base, Message, Session, User, UserProfile
from app.safety.input_guard import check_input
from app.safety.output_guard import check_output

load_dotenv()

client: AsyncAzureOpenAI | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：初始化 OpenAI 客户端 + 确保数据库表存在"""
    global client
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await client.close()


app = FastAPI(title="心雀 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response 模型 ──────────────────────────────────────


class CreateSessionRequest(BaseModel):
    client_id: str


class CreateSessionResponse(BaseModel):
    session_id: str
    user_id: str


class ChatRequest(BaseModel):
    client_id: str
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    card_data: dict | None = None


# ── 辅助函数 ──────────────────────────────────────────────────


async def _get_or_create_user(db: AsyncSession, client_id: str) -> User:
    """根据 client_id 查找用户，不存在则创建（含画像）"""
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


async def _create_session(db: AsyncSession, user_id: str) -> Session:
    """创建新会话，并更新画像的 session_count"""
    session = Session(user_id=user_id)
    db.add(session)
    # 更新 session_count
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.session_count += 1
    await db.flush()
    return session


async def _load_history(db: AsyncSession, session_id: str) -> list[dict]:
    """从数据库加载会话的历史消息"""
    result = await db.execute(
        select(Session)
        .where(Session.session_id == session_id)
        .options(selectinload(Session.messages))
    )
    session = result.scalar_one_or_none()
    if session is None:
        return []
    return [
        {"role": msg.role, "content": msg.content}
        for msg in session.messages
    ]


async def _generate_summary(db: AsyncSession, session_id: str) -> str:
    """调用 LLM 生成结构化会话摘要"""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    all_msgs = result.scalars().all()
    if not all_msgs:
        return ""

    # 构建对话文本（截断到合理长度）
    dialogue_lines = []
    for m in all_msgs:
        role_label = "用户" if m.role == "user" else "心雀"
        dialogue_lines.append(f"{role_label}: {m.content}")
    dialogue_text = "\n".join(dialogue_lines)
    # 截断到 3000 字，避免 token 浪费
    if len(dialogue_text) > 3000:
        dialogue_text = dialogue_text[:3000] + "\n..."

    try:
        response = await client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个会话摘要助手。请用简洁的中文总结以下心理咨询对话，"
                        "包含：1）本次讨论的主题 2）用户的核心困扰 "
                        "3）做了什么干预及效果 4）布置了什么作业。"
                        "摘要控制在 200 字以内，用自然语言，不用 JSON。"
                    ),
                },
                {"role": "user", "content": dialogue_text},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        # LLM 调用失败时降级为简单拼接
        import traceback
        traceback.print_exc()
        user_msgs = [m.content for m in all_msgs if m.role == "user"]
        return " / ".join(user_msgs)[:500]


# ── API 路由 ──────────────────────────────────────────────────


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_session),
):
    """创建新会话"""
    user = await _get_or_create_user(db, request.client_id)
    session = await _create_session(db, user.user_id)
    await db.commit()
    return CreateSessionResponse(session_id=session.session_id, user_id=user.user_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
):
    """接收用户消息，经安全层检测后调用心雀 Agent，返回回复"""
    # 获取或创建用户
    user = await _get_or_create_user(db, request.client_id)

    # 获取或创建会话
    if request.session_id:
        session_id = request.session_id
    else:
        session = await _create_session(db, user.user_id)
        session_id = session.session_id

    # ── 输入安全层（LLM 之前） ──
    guard = check_input(request.message)
    if guard.blocked:
        # 危机/注入 → 绕过 LLM，直接返回预设响应
        if guard.reason == "crisis" and user.profile:
            user.profile.risk_level = "crisis"
        db.add(Message(session_id=session_id, role="user", content=request.message))
        db.add(Message(session_id=session_id, role="assistant", content=guard.response))
        await db.commit()
        return ChatResponse(reply=guard.response, session_id=session_id)

    # 加载历史消息
    history = await _load_history(db, session_id)

    # ── 对齐分数追踪（LLM 之前） ──
    alignment_score = None
    # 重新加载 profile 以确保数据新鲜
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.user_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile:
        alliance = dict(profile.alliance) if profile.alliance else {}
        alignment_score = alliance.get("alignment_score", 15)  # 默认 15

        # 检测本轮用户消息的对齐信号
        score_delta, signal_type = detect_alignment_signal(request.message)
        if score_delta != 0:
            alignment_score = max(-10, min(30, alignment_score + score_delta))
            alliance["alignment_score"] = alignment_score
            if signal_type:
                # 记录不对齐历史
                history_list = alliance.get("misalignment_history", [])
                history_list.append({
                    "type": signal_type,
                    "session_id": session_id,
                })
                # 只保留最近 10 条
                alliance["misalignment_history"] = history_list[-10:]
            profile.alliance = alliance
            flag_modified(profile, "alliance")

    # 调用心雀 Agent
    result = await xinque.chat(
        client=client,
        history=history,
        user_message=request.message,
        user_id=user.user_id,
        session_id=session_id,
        db=db,
        alignment_score=alignment_score,
    )

    reply_text = result["reply"]
    card_data = result.get("card_data")

    # ── 输出安全层（LLM 之后） ──
    output = check_output(reply_text)
    final_reply = output.output

    # 持久化
    db.add(Message(session_id=session_id, role="user", content=request.message))
    db.add(Message(session_id=session_id, role="assistant", content=final_reply))
    await db.commit()

    return ChatResponse(reply=final_reply, session_id=session_id, card_data=card_data)


@app.post("/api/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """结束会话，生成摘要"""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        return {"status": "not_found"}

    if session.ended_at is None:
        session.ended_at = datetime.now(timezone.utc)
        session.summary = await _generate_summary(db, session_id)
        await db.commit()

    return {"status": "ok", "summary": session.summary}


@app.get("/api/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """获取会话的历史消息（前端刷新恢复用）"""
    history = await _load_history(db, session_id)
    return {"messages": history}


@app.get("/api/users/{client_id}/sessions")
async def list_sessions(
    client_id: str,
    db: AsyncSession = Depends(get_session),
):
    """获取用户的所有会话列表"""
    result = await db.execute(
        select(User).where(User.client_id == client_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return {"sessions": []}

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user.user_id)
        .order_by(Session.started_at.desc())
    )
    sessions = result.scalars().all()

    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "summary_preview": (s.summary[:30] + "…") if s.summary and len(s.summary) > 30 else s.summary,
                "opening_mood_score": s.opening_mood_score,
            }
            for s in sessions
        ]
    }


class MoodRequest(BaseModel):
    mood_score: int


@app.patch("/api/sessions/{session_id}/mood")
async def set_mood(
    session_id: str,
    request: MoodRequest,
    db: AsyncSession = Depends(get_session),
):
    """记录会话的情绪签到分数"""
    result = await db.execute(
        select(Session).where(Session.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        return {"status": "not_found"}

    session.opening_mood_score = max(1, min(5, request.mood_score))
    await db.commit()
    return {"status": "ok", "mood_score": session.opening_mood_score}
