"""record_outcome — P4 工具：记录干预结果

干预完成后记录结果，相当于咨询师在咨询结束后做记录。
"""

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import Intervention

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
    await db.flush()

    return json.dumps({
        "status": "ok",
        "intervention_id": intervention.intervention_id,
        "message": "干预记录已保存",
    }, ensure_ascii=False)
