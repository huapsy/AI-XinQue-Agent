"""save_nickname — 保存用户昵称

当用户告知心雀如何称呼自己时，LLM 调用此 Tool 将昵称保存到用户画像。
"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import UserProfile

TOOL_DEFINITION = {
    "type": "function",
    "name": "save_nickname",
    "description": (
        "当用户告诉你他/她的称呼（昵称）时调用此工具保存。"
        "这样下次会话时 recall_context 能返回用户的昵称。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "nickname": {
                "type": "string",
                "description": "用户希望被称呼的名字",
            },
        },
        "required": ["nickname"],
    },
}


async def execute(user_id: str, arguments: dict, db: AsyncSession) -> str:
    """保存昵称到 user_profiles"""
    nickname = arguments.get("nickname", "")
    if not nickname:
        return json.dumps({"status": "error", "message": "nickname is empty"})

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.nickname = nickname
    else:
        db.add(UserProfile(user_id=user_id, nickname=nickname))

    await db.flush()
    return json.dumps({"status": "ok", "nickname": nickname}, ensure_ascii=False)
