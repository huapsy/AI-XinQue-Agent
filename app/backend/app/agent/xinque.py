"""心雀核心 Agent

单一 LLM + Tool Use 自主推理循环（类 ReAct 模式，Thought 不外显）。
"""

import json
import os
import time

from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.system_prompt import build_system_prompt
from app.models.tables import Intervention
from app.responses_helpers import (
    extract_response_function_calls,
    extract_response_message_text,
    get_usage_counts,
)
from app.responses_contract import (
    RUNTIME_LAYER_DEFINITIONS,
    build_runtime_input,
    extend_stateless_input_with_tool_outputs,
)
from app.session_context import (
    build_layered_context,
    build_persisted_session_state,
    load_runtime_session_state,
    render_layered_context_message,
)
from app.settings import get_responses_store_enabled
from app.tool_registry import execute_registered_tool, get_response_tools
from app.tool_runtime import (
    append_tool_state as runtime_append_tool_state,
    execute_tool_runtime_call,
    has_acceptance_signal,
    has_completion_signal,
    has_new_method_signal,
    has_retry_signal,
    load_primary_follow_up_intervention,
    load_recent_interventions,
    preflight_tool_call as runtime_preflight_tool_call,
    safe_scalar_one_or_none,
    tool_state_mentions_skill as runtime_tool_state_mentions_skill,
)

TOOL_DEFINITIONS = get_response_tools()


async def _execute_tool(
    tool_name: str,
    arguments: str,
    user_id: str,
    session_id: str,
    db: AsyncSession,
) -> str:
    """根据 tool_name 执行对应的 Tool，返回结果字符串"""
    args = json.loads(arguments) if arguments else {}
    return await execute_registered_tool(
        tool_name,
        args,
        user_id=user_id,
        session_id=session_id,
        db=db,
    )


async def _preflight_tool_call(
    tool_name: str,
    arguments: dict,
    user_id: str,
    session_id: str,
    user_message: str,
    db: AsyncSession,
    messages: list[dict] | None = None,
    tool_state: list[dict] | None = None,
) -> str | None:
    """在执行高依赖工具前做轻量前置校验。"""
    return await runtime_preflight_tool_call(
        tool_name,
        arguments,
        user_id=user_id,
        session_id=session_id,
        user_message=user_message,
        db=db,
        tool_state=tool_state,
    )


def _estimate_turn_number(history: list[dict]) -> int:
    """根据历史消息估算当前轮次。"""
    user_turns = sum(1 for item in history if item.get("role") == "user")
    return user_turns + 1


def _has_acceptance_signal(user_message: str) -> bool:
    return has_acceptance_signal(user_message)


def _has_completion_signal(user_message: str) -> bool:
    return has_completion_signal(user_message)


def _has_new_method_signal(user_message: str) -> bool:
    return has_new_method_signal(user_message)


def _has_retry_signal(user_message: str) -> bool:
    return has_retry_signal(user_message)


async def _load_recent_interventions(db: AsyncSession, user_id: str, limit: int = 5) -> list[Intervention]:
    return await load_recent_interventions(db, user_id, limit=limit)


async def _load_primary_follow_up_intervention(
    db: AsyncSession,
    user_id: str,
    user_message: str,
) -> Intervention | None:
    return await load_primary_follow_up_intervention(db, user_id, user_message)


async def _safe_scalar_one_or_none(result):
    return await safe_scalar_one_or_none(result)


def _tool_output_mentions_skill(messages: list[dict], tool_name: str, skill_name: str) -> bool:
    for item in reversed(messages):
        if item.get("role") != "tool":
            continue
        content = item.get("content")
        if not isinstance(content, str):
            continue
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            continue

        if tool_name == "match_intervention":
            for plan in parsed.get("plans", []):
                if plan.get("skill_name") == skill_name:
                    return True
        elif tool_name == "load_skill":
            if parsed.get("skill_name") == skill_name:
                return True
    return False


def _tool_state_mentions_skill(tool_state: list[dict] | None, tool_name: str, skill_name: str) -> bool:
    return runtime_tool_state_mentions_skill(tool_state, tool_name, skill_name)


def _append_tool_state(tool_state: list[dict], tool_name: str, result: str) -> None:
    try:
        envelope = json.loads(result)
    except json.JSONDecodeError:
        return
    if isinstance(envelope, dict):
        runtime_append_tool_state(
            tool_state,
            tool_name=tool_name,
            arguments={},
            call_id=None,
            envelope=envelope,
        )


def _build_context_messages(context: dict) -> list[dict]:
    """把分层上下文转换为模型输入前的上下文消息。"""
    return [{
        "role": "assistant",
        "content": render_layered_context_message(context),
    }, *context.get("working_memory", [])]


async def chat(
    client: AsyncAzureOpenAI,
    history: list[dict],
    user_message: str,
    user_id: str,
    session_id: str,
    db: AsyncSession,
    alignment_score: int | None = None,
    trace_collector: list[dict] | None = None,
    previous_response_id: str | None = None,
    persisted_session_state: dict | None = None,
) -> dict:
    """执行一轮对话，返回 {"reply": str, "card_data": dict | None}"""
    turn_number = _estimate_turn_number(history)
    stable_state = await load_runtime_session_state(
        db=db,
        user_id=user_id,
        session_id=session_id,
        alignment_score=alignment_score,
        persisted_state=persisted_session_state,
    )
    layered_context = build_layered_context(
        history=history,
        user_message=user_message,
        stable_state=stable_state,
        persisted_state=persisted_session_state,
    )
    effective_history = _build_context_messages(layered_context)
    messages = [
        {"role": "system", "content": build_system_prompt(alignment_score, turn_number=turn_number)},
        *effective_history,
        {"role": "user", "content": user_message},
    ]

    card_data = None  # 本轮是否有卡片数据
    store_enabled = get_responses_store_enabled()
    llm_trace = {
        "model": os.environ["AZURE_OPENAI_DEPLOYMENT"],
        "endpoint": "responses",
        "request_count": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "latency_ms": 0,
        "final_phase": None,
        "response_ids": [],
        "phase_timeline": [
            {
                "phase": "working_contract",
                "kind": "input",
                "source": "runtime_injection" if (previous_response_id and store_enabled) else "system_prompt",
            },
            {
                "phase": "working_context",
                "kind": "input",
                "source": "persisted_state" if persisted_session_state else "live_refresh",
            },
            {
                "phase": "state_refresh",
                "kind": "state",
                "source": "merged_runtime_state",
            },
        ],
        "persisted_session_state": build_persisted_session_state(layered_context),
        "runtime_layers": dict(RUNTIME_LAYER_DEFINITIONS),
        "runtime_mode": "stateful" if (previous_response_id and store_enabled) else "stateless",
    }
    current_turn_tool_state: list[dict] = []
    pending_input, active_previous_response_id = build_runtime_input(
        effective_history=effective_history,
        user_message=user_message,
        alignment_score=alignment_score,
        turn_number=turn_number,
        previous_response_id=previous_response_id,
        store_enabled=store_enabled,
    )

    # Tool Use 自主推理循环
    max_iterations = 10
    for _ in range(max_iterations):
        llm_started = time.perf_counter()
        create_kwargs = {
            "model": llm_trace["model"],
            "tools": get_response_tools(),
            "instructions": messages[0]["content"],
            "input": pending_input,
            "store": store_enabled,
        }
        if active_previous_response_id is not None:
            create_kwargs["previous_response_id"] = active_previous_response_id
            create_kwargs.pop("instructions", None)

        response = await client.responses.create(**create_kwargs)
        if getattr(response, "id", None):
            llm_trace["response_ids"].append(response.id)
        llm_trace["request_count"] += 1
        llm_trace["latency_ms"] += int((time.perf_counter() - llm_started) * 1000)
        prompt_tokens, completion_tokens, total_tokens = get_usage_counts(response)
        llm_trace["prompt_tokens"] += prompt_tokens
        llm_trace["completion_tokens"] += completion_tokens
        llm_trace["total_tokens"] += total_tokens

        tool_calls = extract_response_function_calls(response)
        if tool_calls:
            pending_tool_outputs: list[dict] = []
            active_previous_response_id = getattr(response, "id", None) if store_enabled else None
            llm_trace["phase_timeline"].append({
                "phase": "tool_call",
                "kind": "output",
                "count": len(tool_calls),
            })

            for tool_call in tool_calls:
                try:
                    envelope, pending_tool_output, produced_card_data = await execute_tool_runtime_call(
                        tool_call,
                        user_id=user_id,
                        session_id=session_id,
                        user_message=user_message,
                        db=db,
                        tool_state=current_turn_tool_state,
                        execute_tool=_execute_tool,
                        preflight_tool=_preflight_tool_call,
                        trace_collector=trace_collector,
                    )
                    if produced_card_data:
                        card_data = produced_card_data

                    llm_trace["phase_timeline"].append({
                        "phase": "tool_result",
                        "kind": "state",
                        "tool": tool_call.name,
                    })
                    pending_tool_outputs.append(pending_tool_output)
                except Exception as exc:
                    raise

            pending_input = (
                pending_tool_outputs
                if store_enabled
                else extend_stateless_input_with_tool_outputs(pending_input, pending_tool_outputs)
            )
            continue

        reply_text, final_phase = extract_response_message_text(response)
        llm_trace["final_phase"] = final_phase
        llm_trace["phase_timeline"].append({
            "phase": final_phase or "final_answer",
            "kind": "output",
        })
        return {
            "reply": reply_text,
            "card_data": card_data,
            "llm_trace": llm_trace,
        }

    return {
        "reply": "抱歉，我需要一点时间整理思路。你刚才说的是什么呢？",
        "card_data": None,
        "llm_trace": llm_trace,
    }
