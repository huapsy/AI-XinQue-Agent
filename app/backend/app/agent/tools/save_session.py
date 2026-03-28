"""save_session — 主动保存摘要并结束当前会话。"""

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.session_helpers import save_session_summary

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "save_session",
        "description": "在对话自然结束、用户表示先到这里时调用，生成摘要并结束当前会话。",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


async def execute(session_id: str, db: AsyncSession) -> str:
    payload = await save_session_summary(db, session_id)
    return json.dumps(payload, ensure_ascii=False)
