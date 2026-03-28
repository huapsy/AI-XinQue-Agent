"""update_profile — 保存用户明确表达的偏好。"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import UserProfile
from app.profile_helpers import apply_profile_patch

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "update_profile",
        "description": (
            "当用户明确表达沟通或干预偏好时调用。"
            "只允许更新 preferences，不要用它写风险或临床判断。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "preferences": {
                    "type": "object",
                    "properties": {
                        "communication_style": {
                            "type": "string",
                            "enum": ["gentle", "direct"],
                        },
                        "preferred_techniques": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "disliked_techniques": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["preferences"],
        },
    },
}


async def execute(user_id: str, arguments: dict, db: AsyncSession) -> str:
    """更新用户的偏好类画像。"""
    patch = arguments.get("preferences") or {}
    allowed_keys = {"communication_style", "preferred_techniques", "disliked_techniques"}
    unsupported = sorted(set(patch) - allowed_keys)
    if unsupported:
        return json.dumps({
            "status": "error",
            "message": f"unsupported preference fields: {', '.join(unsupported)}",
        }, ensure_ascii=False)

    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if profile is None:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    profile.preferences = apply_profile_patch(profile.preferences, patch)
    await db.flush()
    return json.dumps({"status": "ok", "preferences": profile.preferences}, ensure_ascii=False)
