"""心雀后端服务入口"""

import os
import time
from contextlib import asynccontextmanager
from datetime import datetime

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
from app.admin_metrics_helpers import build_admin_metrics_payload, filter_sessions_for_admin_metrics
from app.alignment import detect_alignment_signal
from app.chat_service import (
    create_session_for_user,
    get_or_create_user,
    load_history_messages,
    load_previous_response_id,
    load_previous_session_state,
)
from app.combined_evaluation_store import list_combined_evaluations, save_combined_evaluation
from app.encryption_helpers import decrypt_text, encrypt_text, require_encryption_key
from app.evaluation_helpers import build_combined_evaluation_payload, run_llm_judge
from app.memory_helpers import maybe_store_episodic_memory
from app.models.database import engine, get_session
from app.models.tables import Base, EpisodicMemory, Intervention, Message, Session, TraceRecord, User, UserProfile
from app.otel_helpers import export_trace_event
from app.profile_helpers import build_alliance_patch
from app.privacy_helpers import redact_sensitive_text
from app.responses_helpers import build_text_format_json_schema, extract_response_message_text, extract_structured_output
from app.safety.input_guard import check_input
from app.schema_compat import ensure_sqlite_compat_schema
from app.settings import get_cors_origins
from app.safety.output_guard import check_output
from app.session_helpers import save_session_summary
from app.session_state_store import (
    load_session_state,
    load_session_state_history_filtered,
    load_session_state_with_meta,
    save_session_state_with_history,
)
from app.trace_helpers import (
    build_phase_flow_report,
    build_session_analysis_payload,
    serialize_phase_timeline,
    serialize_trace_records,
)
from app.trace_sink import DatabaseTraceSink
from app.mood_trend_helpers import build_mood_trend_payload

load_dotenv()

client: AsyncAzureOpenAI | None = None
TRACE_SINK = DatabaseTraceSink(TraceRecord)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：初始化 OpenAI 客户端 + 确保数据库表存在"""
    global client
    require_encryption_key()
    client = AsyncAzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(ensure_sqlite_compat_schema)
    yield
    await client.close()


app = FastAPI(title="心雀 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
        dialogue_lines.append(f"{role_label}: {decrypt_text(m.content)}")
    dialogue_text = "\n".join(dialogue_lines)
    # 截断到 3000 字，避免 token 浪费
    if len(dialogue_text) > 3000:
        dialogue_text = dialogue_text[:3000] + "\n..."

    summary_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "themes": {"type": "array", "items": {"type": "string"}},
            "interventions": {"type": "array", "items": {"type": "string"}},
            "follow_up": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["summary", "themes", "interventions", "follow_up"],
        "additionalProperties": False,
    }

    try:
        response = await client.responses.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            instructions=(
                "你是一个会话摘要助手。请生成结构化摘要，"
                "summary 为不超过 200 字的中文自然语言摘要；"
                "themes 为本次主题列表；interventions 为本次使用的方法或练习；"
                "follow_up 为下次应跟进的事项。"
            ),
            input=dialogue_text,
            text=build_text_format_json_schema("session_summary", summary_schema),
        )
        structured = extract_structured_output(response)
        if isinstance(structured, dict) and structured.get("summary"):
            return redact_sensitive_text(str(structured["summary"]), limit=240)

        summary_text, _phase = extract_response_message_text(response)
        if summary_text:
            return redact_sensitive_text(summary_text, limit=240)
        raise ValueError("missing_structured_summary")
    except Exception as e:
        # LLM 调用失败时降级为简单拼接
        if not isinstance(e, ValueError):
            import traceback
            traceback.print_exc()
        user_msgs = [decrypt_text(m.content) for m in all_msgs if m.role == "user"]
        return redact_sensitive_text(" / ".join(user_msgs), limit=240)


async def _store_trace(
    db: AsyncSession,
    session_id: str,
    turn_number: int,
    input_safety: dict,
    llm_call: dict,
    output_safety: dict,
    total_latency_ms: int,
) -> None:
    """写入一条 trace。"""
    db.add(TRACE_SINK.build_record(
        session_id=session_id,
        turn_number=turn_number,
        input_safety=input_safety,
        llm_call=llm_call,
        output_safety=output_safety,
        total_latency_ms=total_latency_ms,
    ))
    export_trace_event("xinque.trace", {
        "session_id": session_id,
        "turn_number": turn_number,
        "input_safety": input_safety,
        "llm_call": llm_call,
        "output_safety": output_safety,
        "total_latency_ms": total_latency_ms,
    })


# ── API 路由 ──────────────────────────────────────────────────


@app.post("/api/sessions", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_session),
):
    """创建新会话"""
    user = await get_or_create_user(db, request.client_id)
    session = await create_session_for_user(db, user.user_id)
    await db.commit()
    return CreateSessionResponse(session_id=session.session_id, user_id=user.user_id)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_session),
):
    """接收用户消息，经安全层检测后调用心雀 Agent，返回回复"""
    request_started = time.perf_counter()
    # 获取或创建用户
    user = await get_or_create_user(db, request.client_id)

    # 获取或创建会话
    if request.session_id:
        session_id = request.session_id
    else:
        session = await create_session_for_user(db, user.user_id)
        session_id = session.session_id

    # ── 输入安全层（LLM 之前） ──
    input_started = time.perf_counter()
    guard = check_input(request.message)
    input_latency_ms = int((time.perf_counter() - input_started) * 1000)
    if guard.blocked:
        # 危机/注入 → 绕过 LLM，直接返回预设响应
        if guard.reason == "crisis" and user.profile:
            user.profile.risk_level = "crisis"
        history = await load_history_messages(db, session_id)
        db.add(Message(session_id=session_id, role="user", content=encrypt_text(request.message)))
        db.add(Message(session_id=session_id, role="assistant", content=encrypt_text(guard.response)))
        await _store_trace(
            db=db,
            session_id=session_id,
            turn_number=len(history) // 2 + 1,
            input_safety={"triggered": True, "reason": guard.reason, "latency_ms": input_latency_ms},
            llm_call={
                "model": None,
                "skipped": True,
                "reason": "input_guard_blocked",
                "latency_ms": 0,
                "request_count": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "tool_calls": [],
            },
            output_safety={"triggered": False, "reason": None, "latency_ms": 0},
            total_latency_ms=int((time.perf_counter() - request_started) * 1000),
        )
        await db.commit()
        return ChatResponse(reply=guard.response, session_id=session_id)

    # 加载历史消息
    history = await load_history_messages(db, session_id)
    previous_response_id = await load_previous_response_id(db, session_id)
    previous_session_state = await load_previous_session_state(db, session_id)

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
            profile.alliance = build_alliance_patch(
                existing=alliance,
                next_score=alignment_score,
                signal_type=signal_type,
                session_id=session_id,
            )
            flag_modified(profile, "alliance")

    # 调用心雀 Agent
    tool_traces: list[dict] = []
    result = await xinque.chat(
        client=client,
        history=history,
        user_message=request.message,
        user_id=user.user_id,
        session_id=session_id,
        db=db,
        alignment_score=alignment_score,
        trace_collector=tool_traces,
        previous_response_id=previous_response_id,
        persisted_session_state=previous_session_state,
    )

    reply_text = result["reply"]
    card_data = result.get("card_data")
    llm_trace = result.get("llm_trace", {})

    # ── 输出安全层（LLM 之后） ──
    output_started = time.perf_counter()
    output = check_output(reply_text)
    output_latency_ms = int((time.perf_counter() - output_started) * 1000)
    final_reply = output.output

    # 持久化
    db.add(Message(session_id=session_id, role="user", content=encrypt_text(request.message)))
    db.add(Message(session_id=session_id, role="assistant", content=encrypt_text(final_reply)))
    await maybe_store_episodic_memory(db, EpisodicMemory, user.user_id, session_id, request.message)
    await save_session_state_with_history(
        db=db,
        session_id=session_id,
        payload=llm_trace.get("persisted_session_state") or {},
    )
    await _store_trace(
        db=db,
        session_id=session_id,
        turn_number=len(history) // 2 + 1,
        input_safety={"triggered": False, "reason": None, "latency_ms": input_latency_ms},
        llm_call={
            "model": llm_trace.get("model", os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")),
            "endpoint": llm_trace.get("endpoint", "responses"),
            "skipped": False,
            "request_count": llm_trace.get("request_count", 0),
            "prompt_tokens": llm_trace.get("prompt_tokens", 0),
            "completion_tokens": llm_trace.get("completion_tokens", 0),
            "total_tokens": llm_trace.get("total_tokens", 0),
            "latency_ms": llm_trace.get("latency_ms", 0),
            "final_phase": llm_trace.get("final_phase"),
            "response_ids": llm_trace.get("response_ids", []),
            "phase_timeline": llm_trace.get("phase_timeline", []),
            "persisted_session_state": llm_trace.get("persisted_session_state"),
            "tool_calls": tool_traces,
        },
        output_safety={
            "triggered": final_reply != reply_text,
            "reason": output.reason,
            "latency_ms": output_latency_ms,
        },
        total_latency_ms=int((time.perf_counter() - request_started) * 1000),
    )
    await db.commit()

    return ChatResponse(reply=final_reply, session_id=session_id, card_data=card_data)


@app.post("/api/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """结束会话，生成摘要"""
    payload = await save_session_summary(db, session_id)
    if payload["status"] == "not_found":
        return {"status": "not_found"}
    await db.commit()
    return payload


@app.get("/api/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """获取会话的历史消息（前端刷新恢复用）"""
    result = await db.execute(
        select(Session.session_id).where(Session.session_id == session_id)
    )
    exists = result.scalar_one_or_none() is not None
    history = await load_history_messages(db, session_id) if exists else []
    return {"exists": exists, "messages": history}


@app.get("/api/sessions/{session_id}/traces")
async def get_session_traces(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """获取指定会话的 trace 列表。"""
    result = await db.execute(TraceRecord.select_by_session(session_id))
    traces = result.scalars().all()
    return serialize_trace_records(traces)


@app.get("/api/sessions/{session_id}/state")
async def get_session_state(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """读取当前会话状态。"""
    payload = await load_session_state_with_meta(db, session_id)
    return {"state": payload}


@app.get("/api/sessions/{session_id}/state-history")
async def get_session_state_history(
    session_id: str,
    db: AsyncSession = Depends(get_session),
    limit: int = 20,
    before_version: int | None = None,
    change_reason: str | None = None,
):
    """读取会话状态历史。"""
    return await load_session_state_history_filtered(
        db,
        session_id,
        limit=limit,
        before_version=before_version,
        change_reason=change_reason,
    )


@app.get("/api/sessions/{session_id}/timeline")
async def get_session_timeline(
    session_id: str,
    db: AsyncSession = Depends(get_session),
    limit: int = 20,
    before_turn: int | None = None,
    phase: str | None = None,
):
    """读取会话 phase timeline。"""
    result = await db.execute(TraceRecord.select_by_session(session_id))
    traces = result.scalars().all()
    return serialize_phase_timeline(
        traces,
        limit=limit,
        before_turn=before_turn,
        phase=phase,
    )


@app.get("/api/sessions/{session_id}/analysis")
async def get_session_analysis(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """读取会话级聚合分析载荷。"""
    state_payload = await load_session_state_history_filtered(db, session_id, limit=5)
    state_history = state_payload.get("history", [])
    result = await db.execute(TraceRecord.select_by_session(session_id))
    traces = result.scalars().all()
    return build_session_analysis_payload(
        session_id=session_id,
        state_history=state_history,
        traces=traces,
    )


@app.get("/api/sessions/{session_id}/phase-flow")
async def get_session_phase_flow(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """读取会话级 phase flow report。"""
    result = await db.execute(TraceRecord.select_by_session(session_id))
    traces = result.scalars().all()
    return {
        "session_id": session_id,
        "phase_flow": build_phase_flow_report(traces),
    }


@app.get("/api/sessions/{session_id}/combined-evaluation")
async def get_session_combined_evaluation(
    session_id: str,
    db: AsyncSession = Depends(get_session),
):
    """读取会话级联合评估载荷。"""
    result = await db.execute(TraceRecord.select_by_session(session_id))
    traces = result.scalars().all()
    phase_flow = build_phase_flow_report(traces)
    messages = await load_history_messages(db, session_id)
    judge_result = await run_llm_judge(
        client=client,
        model=os.environ.get("XINQUE_JUDGE_MODEL", os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")),
        session_id=session_id,
        messages=messages,
    )
    payload = build_combined_evaluation_payload(
        judge_result=judge_result,
        phase_flow_report=phase_flow,
    )
    await save_combined_evaluation(db, session_id, payload)
    return payload


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
                "summary_preview": (
                    (decrypt_text(s.summary)[:30] + "…")
                    if decrypt_text(s.summary) and len(decrypt_text(s.summary)) > 30
                    else decrypt_text(s.summary)
                ),
                "opening_mood_score": s.opening_mood_score,
            }
            for s in sessions
        ]
    }


@app.get("/api/users/{client_id}/mood-trend")
async def get_mood_trend(
    client_id: str,
    db: AsyncSession = Depends(get_session),
):
    """获取用户情绪签到趋势。"""
    result = await db.execute(
        select(User).where(User.client_id == client_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return build_mood_trend_payload([])

    result = await db.execute(
        select(Session)
        .where(Session.user_id == user.user_id)
        .order_by(Session.started_at)
    )
    sessions = result.scalars().all()
    return build_mood_trend_payload(sessions)


@app.get("/api/admin/metrics")
async def get_admin_metrics(
    db: AsyncSession = Depends(get_session),
    recent_sessions: int | None = None,
    since_days: int | None = None,
    now: datetime | None = None,
):
    """获取匿名汇总指标。"""
    all_sessions = (await db.execute(select(Session))).scalars().all()
    interventions = (await db.execute(select(Intervention))).scalars().all()
    traces = (await db.execute(select(TraceRecord))).scalars().all()
    message_rows = (await db.execute(select(Message.session_id))).scalars().all()
    combined_evaluations = await list_combined_evaluations(db)
    sessions = filter_sessions_for_admin_metrics(
        all_sessions,
        recent_sessions=recent_sessions,
        since_days=since_days,
        now=now,
    )
    scoped_session_ids = {session.session_id for session in sessions}
    interventions = [
        item for item in interventions
        if getattr(item, "session_id", None) in scoped_session_ids
    ]
    traces = [
        trace for trace in traces
        if getattr(trace, "session_id", None) in scoped_session_ids
    ]
    message_counts: dict[str, int] = {}
    for session_id in message_rows:
        if session_id in scoped_session_ids:
            message_counts[session_id] = message_counts.get(session_id, 0) + 1
    combined_evaluations = [
        payload for payload in combined_evaluations
        if payload.get("session_id") in scoped_session_ids
    ]
    return build_admin_metrics_payload(
        sessions,
        interventions,
        traces,
        message_counts,
        combined_evaluations=combined_evaluations,
    )


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
