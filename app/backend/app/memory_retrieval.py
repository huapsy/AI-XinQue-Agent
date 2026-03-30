"""记忆检索 backend 抽象。"""

from __future__ import annotations

from app.memory_helpers import score_memories_by_query
from app.time_freshness import sort_memories_with_time_freshness


def retrieve_memories(query: str, memories: list[dict], top_k: int) -> list[dict]:
    """统一的检索入口，当前默认走本地 backend。"""
    return _retrieve_with_local_backend(query, memories, top_k)


def _retrieve_with_local_backend(query: str, memories: list[dict], top_k: int) -> list[dict]:
    """本地默认检索 backend。"""
    return sort_memories_with_time_freshness(score_memories_by_query(query, memories))[:top_k]

