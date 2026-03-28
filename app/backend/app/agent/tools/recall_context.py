"""recall_context — P1 主力工具：回顾用户上下文

会话开始时一次性加载用户的全部相关上下文，相当于咨询师在接待来访者前翻阅案例档案。
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tables import Intervention, Session, User, UserProfile

# Tool 定义（OpenAI Function Calling 格式）
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "recall_context",
        "description": (
            "会话开始时调用，回顾用户的历史上下文。"
            "返回用户基本信息（昵称、会话次数）、上次会话摘要、"
            "未完成的作业、最近的干预历史、用户偏好。"
            "首次对话的新用户也应调用，会返回空上下文。"
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


async def execute(user_id: str, db: AsyncSession) -> str:
    """执行 recall_context，返回 JSON 字符串供 LLM 阅读"""

    # 加载用户 + 画像
    result = await db.execute(
        select(User)
        .where(User.user_id == user_id)
        .options(selectinload(User.profile))
    )
    user = result.scalar_one_or_none()

    if user is None:
        return json.dumps({"status": "new_user"}, ensure_ascii=False)

    # 加载上次已结束的会话
    sess_result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id, Session.ended_at.isnot(None))
        .order_by(Session.started_at.desc())
        .limit(1)
    )
    last_session = sess_result.scalar_one_or_none()

    # 加载未完成的作业
    homework_result = await db.execute(
        select(Intervention)
        .where(
            Intervention.user_id == user_id,
            Intervention.homework_assigned.isnot(None),
            Intervention.homework_completed == False,
        )
        .order_by(Intervention.started_at.desc())
        .limit(5)
    )
    pending_homeworks = homework_result.scalars().all()

    # 加载最近干预历史
    history_result = await db.execute(
        select(Intervention)
        .where(Intervention.user_id == user_id)
        .order_by(Intervention.started_at.desc())
        .limit(3)
    )
    recent_interventions = history_result.scalars().all()

    profile = user.profile
    context = {
        "profile_snapshot": {
            "nickname": (profile.nickname if profile else None) or user.nickname,
            "session_count": profile.session_count if profile else 0,
            "risk_level": profile.risk_level if profile else "none",
            "alliance": profile.alliance if profile else None,
            "preferences": (profile.preferences if profile else None) or {},
            "clinical_profile": (profile.clinical_profile if profile else None) or {},
        },
        "last_session_summary": None,
        "pending_homework": [],
        "recent_interventions": [],
    }

    if last_session:
        context["last_session_summary"] = last_session.summary

    # 未完成作业
    for hw in pending_homeworks:
        homework_data = hw.homework_assigned or {}
        context["pending_homework"].append({
            "skill_name": hw.skill_name,
            "assigned_date": hw.started_at.strftime("%Y-%m-%d") if hw.started_at else None,
            "description": homework_data.get("description", ""),
            "frequency": homework_data.get("frequency"),
        })

    # 最近干预历史
    for iv in recent_interventions:
        context["recent_interventions"].append({
            "skill_name": iv.skill_name,
            "date": iv.started_at.strftime("%Y-%m-%d") if iv.started_at else None,
            "completed": iv.completed,
            "user_feedback": iv.user_feedback,
            "key_insight": iv.key_insight,
        })

    return json.dumps(context, ensure_ascii=False)
