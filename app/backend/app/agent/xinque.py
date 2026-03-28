"""心雀核心 Agent

单一 LLM + Tool Use 自主推理循环（类 ReAct 模式，Thought 不外显）。
"""

import json
import os
import time

from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.system_prompt import build_system_prompt
from app.agent.tools import (
    formulate,
    load_skill,
    match_intervention,
    recall_context,
    render_card,
    record_outcome,
    referral,
    save_session,
    search_memory,
    save_nickname,
    update_profile,
)
from app.trace_helpers import build_tool_trace_entry

# 注册的 Tool 定义列表
TOOL_DEFINITIONS = [
    recall_context.TOOL_DEFINITION,
    search_memory.TOOL_DEFINITION,
    formulate.TOOL_DEFINITION,
    save_nickname.TOOL_DEFINITION,
    update_profile.TOOL_DEFINITION,
    save_session.TOOL_DEFINITION,
    match_intervention.TOOL_DEFINITION,
    load_skill.TOOL_DEFINITION,
    render_card.TOOL_DEFINITION,
    record_outcome.TOOL_DEFINITION,
    referral.TOOL_DEFINITION,
]


async def _execute_tool(
    tool_name: str,
    arguments: str,
    user_id: str,
    session_id: str,
    db: AsyncSession,
) -> str:
    """根据 tool_name 执行对应的 Tool，返回结果字符串"""
    args = json.loads(arguments) if arguments else {}

    if tool_name == "recall_context":
        return await recall_context.execute(user_id, db)
    if tool_name == "search_memory":
        return await search_memory.execute(user_id, args, db)
    if tool_name == "formulate":
        return await formulate.execute(session_id, user_id, args, db)
    if tool_name == "save_nickname":
        return await save_nickname.execute(user_id, args, db)
    if tool_name == "update_profile":
        return await update_profile.execute(user_id, args, db)
    if tool_name == "save_session":
        return await save_session.execute(session_id, db)
    if tool_name == "match_intervention":
        return await match_intervention.execute(session_id, user_id, db)
    if tool_name == "load_skill":
        return await load_skill.execute(args)
    if tool_name == "render_card":
        return await render_card.execute(args)
    if tool_name == "record_outcome":
        return await record_outcome.execute(session_id, user_id, args, db)
    if tool_name == "referral":
        return await referral.execute(args)

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


async def chat(
    client: AsyncAzureOpenAI,
    history: list[dict],
    user_message: str,
    user_id: str,
    session_id: str,
    db: AsyncSession,
    alignment_score: int | None = None,
    trace_collector: list[dict] | None = None,
) -> dict:
    """执行一轮对话，返回 {"reply": str, "card_data": dict | None}"""
    messages = [
        {"role": "system", "content": build_system_prompt(alignment_score)},
        *history,
        {"role": "user", "content": user_message},
    ]

    card_data = None  # 本轮是否有卡片数据
    llm_trace = {
        "model": os.environ["AZURE_OPENAI_DEPLOYMENT"],
        "request_count": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency_ms": 0,
    }

    # Tool Use 自主推理循环
    max_iterations = 10
    for _ in range(max_iterations):
        llm_started = time.perf_counter()
        response = await client.chat.completions.create(
            model=llm_trace["model"],
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )
        llm_trace["request_count"] += 1
        llm_trace["latency_ms"] += int((time.perf_counter() - llm_started) * 1000)
        usage = getattr(response, "usage", None)
        llm_trace["prompt_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
        llm_trace["completion_tokens"] += getattr(usage, "completion_tokens", 0) or 0
        llm_trace["total_tokens"] += getattr(usage, "total_tokens", 0) or 0

        choice = response.choices[0]

        # LLM 决定调用 Tool
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls:
                started = time.perf_counter()
                try:
                    result = await _execute_tool(
                        tool_name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                        user_id=user_id,
                        session_id=session_id,
                        db=db,
                    )
                    latency_ms = int((time.perf_counter() - started) * 1000)

                    if trace_collector is not None:
                        trace_collector.append(build_tool_trace_entry(
                            tool_name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                            result=result,
                            success=True,
                            latency_ms=latency_ms,
                        ))

                    # 如果 load_skill 或 referral 返回了 card_data，提取出来
                    if tool_call.function.name in ("load_skill", "referral", "render_card"):
                        try:
                            parsed = json.loads(result)
                            if parsed.get("card_data"):
                                card_data = parsed["card_data"]
                        except (json.JSONDecodeError, KeyError):
                            pass

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                except Exception as exc:
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    if trace_collector is not None:
                        trace_collector.append(build_tool_trace_entry(
                            tool_name=tool_call.function.name,
                            arguments=tool_call.function.arguments,
                            result=str(exc),
                            success=False,
                            latency_ms=latency_ms,
                        ))
                    raise

            continue

        # LLM 生成了最终回复
        return {
            "reply": choice.message.content or "",
            "card_data": card_data,
            "llm_trace": llm_trace,
        }

    return {
        "reply": "抱歉，我需要一点时间整理思路。你刚才说的是什么呢？",
        "card_data": None,
        "llm_trace": llm_trace,
    }
