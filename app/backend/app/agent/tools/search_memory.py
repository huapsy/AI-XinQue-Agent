"""search_memory — 检索更早的关键历史事件片段。"""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.encryption_helpers import decrypt_text
from app.memory_helpers import rank_memories_by_query
from app.models.tables import EpisodicMemory

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_memory",
        "description": (
            "当用户提到旧话题、人物或场景，需要回忆更早的关键历史事件时调用。"
            "不要每轮都调用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer"},
                "topic": {"type": "string"},
            },
            "required": ["query"],
        },
    },
}


async def execute(user_id: str, arguments: dict, db: AsyncSession) -> str:
    """检索用户的情景记忆。"""
    query = arguments.get("query", "")
    top_k = max(1, min(int(arguments.get("top_k", 3)), 5))
    topic = arguments.get("topic")

    result = await db.execute(
        select(EpisodicMemory).where(EpisodicMemory.user_id == user_id)
    )
    memories = result.scalars().all()
    payload = [
        {
            "content": decrypt_text(memory.content),
            "topic": memory.topic,
            "emotions": getattr(memory, "emotions", None) or [],
            "created_at": memory.created_at.isoformat() if memory.created_at else None,
            "embedding": getattr(memory, "embedding", None) or [],
        }
        for memory in memories
        if not topic or memory.topic == topic
    ]

    ranked = rank_memories_by_query(query, payload)[:top_k]
    for item in ranked:
        item.pop("embedding", None)
    return json.dumps({"results": ranked}, ensure_ascii=False)
