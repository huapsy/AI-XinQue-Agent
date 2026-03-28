"""record_outcome — P4 工具：记录干预结果

干预完成后记录结果，相当于咨询师在咨询结束后做记录。
"""

import json

from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import Intervention, UserProfile
from app.profile_helpers import apply_profile_patch, build_alliance_patch, build_preference_patch_from_outcome

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "record_outcome",
        "description": (
            "干预完成后调用，记录干预结果。"
            "包括是否完成、用户反馈、关键洞察、布置的作业等。"
            "在询问用户感受之后调用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "执行的 Skill 名称",
                },
                "completed": {
                    "type": "boolean",
                    "description": "用户是否完成了干预练习",
                },
                "user_feedback": {
                    "type": "string",
                    "description": "用户反馈：helpful / neutral / unhelpful",
                },
                "key_insight": {
                    "type": "string",
                    "description": "用户在干预中的关键洞察或发现",
                },
                "target_issue": {
                    "type": "string",
                    "description": "干预针对的问题",
                },
                "homework_description": {
                    "type": "string",
                    "description": "布置的作业描述（如有）",
                },
                "homework_frequency": {
                    "type": "string",
                    "description": "作业频率（如有），如'每天一次'、'本周遇到时'",
                },
            },
            "required": ["skill_name", "completed"],
        },
    },
}

SKILLS_DIR = Path(__file__).resolve().parents[4] / "skills"


def _get_skill_category(skill_name: str) -> str | None:
    """从 skill frontmatter 中读取类别。"""
    for md_file in SKILLS_DIR.rglob("*.skill.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            end = text.index("---", 3)
            frontmatter = text[3:end].splitlines()
            fields = {}
            for line in frontmatter:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
            if fields.get("name") == skill_name:
                return fields.get("category")
        except Exception:
            continue
    return None


async def execute(
    session_id: str,
    user_id: str,
    arguments: dict,
    db: AsyncSession,
) -> str:
    """执行 record_outcome，写入干预记录"""
    skill_name = arguments.get("skill_name", "")
    completed = arguments.get("completed", False)
    user_feedback = arguments.get("user_feedback")
    key_insight = arguments.get("key_insight")
    target_issue = arguments.get("target_issue")

    # 构建作业数据
    homework = None
    hw_desc = arguments.get("homework_description")
    if hw_desc:
        homework = {
            "description": hw_desc,
            "frequency": arguments.get("homework_frequency"),
        }

    intervention = Intervention(
        session_id=session_id,
        user_id=user_id,
        skill_name=skill_name,
        target_issue=target_issue,
        completed=completed,
        user_feedback=user_feedback,
        key_insight=key_insight,
        homework_assigned=homework,
    )
    db.add(intervention)

    if completed or user_feedback in {"helpful", "unhelpful"}:
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is not None:
            current_score = (profile.alliance or {}).get("alignment_score", 15)
            if user_feedback in {"helpful", "unhelpful"}:
                preference_patch = build_preference_patch_from_outcome(
                    _get_skill_category(skill_name),
                    skill_name,
                    user_feedback,
                )
                profile.preferences = apply_profile_patch(profile.preferences, preference_patch)
            if completed:
                profile.alliance = build_alliance_patch(
                    existing=profile.alliance or {},
                    next_score=min(30, current_score + 5),
                    signal_type=None,
                    session_id=session_id,
                )

    await db.flush()

    return json.dumps({
        "status": "ok",
        "intervention_id": intervention.intervention_id,
        "message": "干预记录已保存",
    }, ensure_ascii=False)
