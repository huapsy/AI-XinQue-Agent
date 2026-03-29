"""Tool registry：统一注册 tool definition 与执行入口。"""

from __future__ import annotations

from functools import lru_cache

from app.agent.tools import (
    formulate,
    load_skill,
    match_intervention,
    recall_context,
    record_outcome,
    referral,
    render_card,
    save_nickname,
    save_session,
    search_memory,
    update_profile,
)


async def _run_recall_context(arguments: dict, *, user_id: str, session_id: str, db):
    return await recall_context.execute(user_id, db)


async def _run_search_memory(arguments: dict, *, user_id: str, session_id: str, db):
    return await search_memory.execute(user_id, arguments, db)


async def _run_formulate(arguments: dict, *, user_id: str, session_id: str, db):
    return await formulate.execute(session_id, user_id, arguments, db)


async def _run_save_nickname(arguments: dict, *, user_id: str, session_id: str, db):
    return await save_nickname.execute(user_id, arguments, db)


async def _run_update_profile(arguments: dict, *, user_id: str, session_id: str, db):
    return await update_profile.execute(user_id, arguments, db)


async def _run_save_session(arguments: dict, *, user_id: str, session_id: str, db):
    return await save_session.execute(session_id, db)


async def _run_match_intervention(arguments: dict, *, user_id: str, session_id: str, db):
    return await match_intervention.execute(session_id, user_id, db)


async def _run_load_skill(arguments: dict, *, user_id: str, session_id: str, db):
    return await load_skill.execute(arguments)


async def _run_render_card(arguments: dict, *, user_id: str, session_id: str, db):
    return await render_card.execute(arguments)


async def _run_record_outcome(arguments: dict, *, user_id: str, session_id: str, db):
    return await record_outcome.execute(session_id, user_id, arguments, db)


async def _run_referral(arguments: dict, *, user_id: str, session_id: str, db):
    return await referral.execute(arguments)


@lru_cache(maxsize=1)
def get_tool_registry() -> dict[str, dict]:
    """返回统一 tool registry。"""
    entries = [
        ("recall_context", recall_context.TOOL_DEFINITION, _run_recall_context),
        ("search_memory", search_memory.TOOL_DEFINITION, _run_search_memory),
        ("formulate", formulate.TOOL_DEFINITION, _run_formulate),
        ("save_nickname", save_nickname.TOOL_DEFINITION, _run_save_nickname),
        ("update_profile", update_profile.TOOL_DEFINITION, _run_update_profile),
        ("save_session", save_session.TOOL_DEFINITION, _run_save_session),
        ("match_intervention", match_intervention.TOOL_DEFINITION, _run_match_intervention),
        ("load_skill", load_skill.TOOL_DEFINITION, _run_load_skill),
        ("render_card", render_card.TOOL_DEFINITION, _run_render_card),
        ("record_outcome", record_outcome.TOOL_DEFINITION, _run_record_outcome),
        ("referral", referral.TOOL_DEFINITION, _run_referral),
    ]
    return {
        name: {
            "definition": definition,
            "execute": execute,
        }
        for name, definition, execute in entries
    }


def get_response_tools() -> list[dict]:
    """返回供 Responses API 使用的 tool definitions。"""
    return [entry["definition"] for entry in get_tool_registry().values()]


async def execute_registered_tool(
    tool_name: str,
    arguments: dict,
    *,
    user_id: str,
    session_id: str,
    db,
) -> str:
    """执行已注册 tool。"""
    entry = get_tool_registry().get(tool_name)
    if entry is None:
        raise ValueError(f"unknown tool: {tool_name}")
    return await entry["execute"](arguments, user_id=user_id, session_id=session_id, db=db)
