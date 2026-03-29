"""长会话上下文分层与语义压缩辅助函数。"""

from __future__ import annotations

import inspect
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.encryption_helpers import decrypt_text
from app.models.tables import CaseFormulation, Intervention, Session, User
from app.time_context import build_runtime_time_context, format_relative_time


def _clean_text(value: Any, limit: int = 48) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = text.replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _dedupe_keep_order(items: list[str], limit: int = 3) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        output.append(normalized)
        if len(output) >= limit:
            break
    return output


def _collect_role_texts(history: list[dict], role: str) -> list[str]:
    return [
        _clean_text(item.get("content", ""), limit=60)
        for item in history
        if item.get("role") == role and _clean_text(item.get("content", ""), limit=60)
    ]


def _extract_attempted_methods(history: list[dict]) -> list[str]:
    keywords = ("练习", "方法", "呼吸", "正念", "作业", "技能", "写下来", "记录")
    matches = []
    for item in history:
        content = _clean_text(item.get("content", ""), limit=60)
        if any(keyword in content for keyword in keywords):
            matches.append(content)
    return _dedupe_keep_order(matches, limit=3)


def _extract_open_loops(history: list[dict], user_message: str) -> list[str]:
    keywords = ("还", "又", "但是", "担心", "明天", "下周", "不想", "不知道", "怎么")
    candidates = []
    for content in [*_collect_role_texts(history, "user"), _clean_text(user_message, limit=60)]:
        if any(keyword in content for keyword in keywords):
            candidates.append(content)
    return _dedupe_keep_order(candidates, limit=3)


def _build_semantic_summary(history: list[dict], user_message: str) -> dict[str, list[str]]:
    user_texts = _collect_role_texts(history, "user")
    assistant_texts = _collect_role_texts(history, "assistant")

    primary_themes = _dedupe_keep_order(user_texts, limit=3)
    active_concerns = _dedupe_keep_order([*user_texts[-2:], _clean_text(user_message, limit=60)], limit=3)
    attempted_methods = _extract_attempted_methods(history)
    open_loops = _extract_open_loops(history, user_message)

    if not attempted_methods and assistant_texts:
        attempted_methods = _dedupe_keep_order(assistant_texts[-1:], limit=1)
    if not open_loops:
        open_loops = _dedupe_keep_order([_clean_text(user_message, limit=60)], limit=1)

    return {
        "primary_themes": primary_themes,
        "active_concerns": active_concerns,
        "attempted_methods": attempted_methods,
        "open_loops": open_loops,
    }


def _merge_summary_sections(
    persisted: dict[str, list[str]] | None,
    computed: dict[str, list[str]],
) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    persisted = persisted or {}
    for key in ("primary_themes", "active_concerns", "attempted_methods", "open_loops"):
        merged[key] = _dedupe_keep_order([
            *(persisted.get(key) or []),
            *(computed.get(key) or []),
        ], limit=4)
    return merged


def build_layered_context(
    history: list[dict],
    user_message: str,
    stable_state: dict[str, Any] | None,
    persisted_state: dict[str, Any] | None = None,
    keep_last: int = 4,
) -> dict[str, Any]:
    """构造长会话分层上下文。"""
    working_memory = history[-keep_last:] if len(history) > keep_last else list(history)
    persisted_state = persisted_state or {}
    semantic_summary = _merge_summary_sections(
        persisted_state.get("semantic_summary"),
        _build_semantic_summary(history, user_message),
    )

    return {
        "current_focus": {
            "priority": "current_turn",
            "summary": _clean_text(user_message, limit=80),
        },
        "working_memory": working_memory,
        "stable_state": stable_state or {},
        "retrieval_context": {
            "recall_context_role": "stable background only: profile, last session summary, pending homework, recent interventions.",
            "search_memory_role": "specific past events only: use when a concrete prior episode, trigger, or precedent must be recalled; newer and still-continuing episodes should usually outrank older background items.",
            "semantic_summary_role": "compressed continuity only: carry forward themes, attempted methods, and open loops without replaying raw history.",
        },
        "semantic_summary": semantic_summary,
    }


def build_persisted_session_state(context: dict[str, Any]) -> dict[str, Any]:
    """提取需要跨轮恢复的最小长会话状态。"""
    stable_state = context.get("stable_state", {})
    return {
        "current_focus": context.get("current_focus", {}),
        "semantic_summary": context.get("semantic_summary", {}),
        "stable_state": {
            "runtime_time_context": stable_state.get("runtime_time_context", {}),
            "profile_snapshot": stable_state.get("profile_snapshot", {}),
            "formulation": stable_state.get("formulation", {}),
            "recent_intervention": stable_state.get("recent_intervention", {}),
            "last_session_summary": stable_state.get("last_session_summary"),
        },
    }


def render_layered_context_message(context: dict[str, Any]) -> str:
    """把分层上下文渲染成模型可读的上下文卡片。"""
    stable_state = context.get("stable_state", {})
    runtime_time = stable_state.get("runtime_time_context", {})
    profile = stable_state.get("profile_snapshot", {})
    formulation = stable_state.get("formulation", {})
    intervention = stable_state.get("recent_intervention", {})
    summary = context.get("semantic_summary", {})
    retrieval = context.get("retrieval_context", {})

    lines = [
        "会话状态：",
        (
            "当前时间："
            f"{runtime_time.get('current_time_iso') or '未知'} "
            f"({runtime_time.get('timezone') or 'unknown'})"
        ),
        f"当前目标：{context.get('current_focus', {}).get('summary', '')}",
        (
            "稳定状态："
            f"昵称={profile.get('nickname') or '未知'}；"
            f"风险={profile.get('risk_level') or 'unknown'}；"
            f"formulation={formulation.get('primary_issue') or '待形成'}"
            f"/{formulation.get('readiness') or 'unknown'}；"
            f"最近干预={intervention.get('skill_name') or '无'}"
            f"（{intervention.get('relative_time') or '时间未知'}）"
        ),
        (
            "语义摘要："
            f"主题={' / '.join(summary.get('primary_themes', [])) or '无'}；"
            f"当前关切={' / '.join(summary.get('active_concerns', [])) or '无'}；"
            f"已尝试方法={' / '.join(summary.get('attempted_methods', [])) or '无'}；"
            f"未完成事项={' / '.join(summary.get('open_loops', [])) or '无'}"
        ),
        (
            "检索边界："
            f"recall_context={retrieval.get('recall_context_role', '')} "
            f"search_memory={retrieval.get('search_memory_role', '')} "
            f"semantic_summary={retrieval.get('semantic_summary_role', '')}"
        ),
    ]
    return "\n".join(lines)


async def _safe_scalar_one_or_none(result: Any) -> Any | None:
    getter = getattr(result, "scalar_one_or_none", None)
    if getter is None:
        return None
    value = getter()
    if inspect.isawaitable(value):
        value = await value
    return value


async def load_runtime_session_state(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    alignment_score: int | None = None,
    persisted_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """加载当前轮需要的稳定状态。"""
    persisted_stable = dict((persisted_state or {}).get("stable_state") or {})
    stable_state: dict[str, Any] = {
        "runtime_time_context": build_runtime_time_context(),
        "profile_snapshot": {},
        "formulation": {},
        "recent_intervention": {},
        "last_session_summary": None,
    }
    for key in ("runtime_time_context", "profile_snapshot", "formulation", "recent_intervention", "last_session_summary"):
        if key in persisted_stable:
            stable_state[key] = persisted_stable[key]

    user_result = await db.execute(
        select(User).where(User.user_id == user_id).options(selectinload(User.profile))
    )
    user = await _safe_scalar_one_or_none(user_result)
    if isinstance(user, User):
        profile = user.profile
        stable_state["profile_snapshot"] = {
            "nickname": (getattr(profile, "nickname", None) or user.nickname),
            "risk_level": getattr(profile, "risk_level", None) or "none",
            "preferences": getattr(profile, "preferences", None) or {},
            "alliance": getattr(profile, "alliance", None) or {},
        }

    session_result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id, Session.ended_at.isnot(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )
    last_session = await _safe_scalar_one_or_none(session_result)
    if isinstance(last_session, Session) and last_session.summary:
        stable_state["last_session_summary"] = decrypt_text(last_session.summary)

    formulation_result = await db.execute(
        select(CaseFormulation)
        .where(CaseFormulation.session_id == session_id)
        .order_by(CaseFormulation.updated_at.desc())
        .limit(1)
    )
    formulation = await _safe_scalar_one_or_none(formulation_result)
    if isinstance(formulation, CaseFormulation):
        stable_state["formulation"] = {
            "readiness": formulation.readiness,
            "primary_issue": formulation.primary_issue,
            "mechanism": formulation.mechanism,
            "missing": formulation.missing or [],
        }

    intervention_result = await db.execute(
        select(Intervention)
        .where(Intervention.user_id == user_id)
        .order_by(Intervention.started_at.desc())
        .limit(1)
    )
    intervention = await _safe_scalar_one_or_none(intervention_result)
    if isinstance(intervention, Intervention):
        stable_state["recent_intervention"] = {
            "skill_name": intervention.skill_name,
            "started_at_iso": intervention.started_at.isoformat() if intervention.started_at else None,
            "relative_time": format_relative_time(intervention.started_at),
            "completed": intervention.completed,
            "user_feedback": intervention.user_feedback,
            "key_insight": intervention.key_insight,
        }

    if alignment_score is not None:
        alliance = stable_state["profile_snapshot"].setdefault("alliance", {})
        alliance.setdefault("alignment_score", alignment_score)

    return stable_state
