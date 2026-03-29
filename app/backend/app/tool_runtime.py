"""Tool runtime：统一 preflight、state、trace 与 envelope。"""

from __future__ import annotations

import inspect
import json
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables import CaseFormulation, Intervention
from app.responses_helpers import build_function_call_output, resolve_function_call_id
from app.time_context import format_relative_time
from app.time_freshness import intervention_needs_follow_up, select_primary_follow_up_intervention
from app.tool_contracts import dump_tool_envelope, normalize_tool_result
from app.trace_helpers import build_tool_trace_entry


def has_acceptance_signal(user_message: str) -> bool:
    signals = (
        "愿意", "可以试试", "试试", "开始吧", "开始", "来吧",
        "想做", "做一下", "带我", "试这个", "就这个", "可以做",
    )
    return any(signal in user_message for signal in signals)


def has_completion_signal(user_message: str) -> bool:
    signals = (
        "做完", "刚做完", "完成了", "做了", "试了", "刚试了",
        "感觉", "有帮助", "没帮助", "没什么用", "还行", "不太有用",
    )
    return any(signal in user_message for signal in signals)


def has_new_method_signal(user_message: str) -> bool:
    signals = (
        "别的方法", "换一个", "换种", "新的方法", "还有别的", "不适合", "没用",
        "没什么用", "不想做那个", "别的练习", "其他办法",
    )
    return any(signal in user_message for signal in signals)


def has_retry_signal(user_message: str) -> bool:
    signals = (
        "再做一次", "重新来一遍", "再来一次", "再带我做", "重做", "再练一次",
        "再试一次", "再做那个",
    )
    return any(signal in user_message for signal in signals)


async def safe_scalar_one_or_none(result):
    getter = getattr(result, "scalar_one_or_none", None)
    if getter is None:
        return None
    value = getter()
    if inspect.isawaitable(value):
        value = await value
    return value


async def load_recent_interventions(db: AsyncSession, user_id: str, limit: int = 5) -> list[Intervention]:
    result = await db.execute(
        select(Intervention)
        .where(Intervention.user_id == user_id)
        .order_by(Intervention.started_at.desc())
        .limit(limit)
    )
    scalars = getattr(result, "scalars", None)
    if scalars is not None:
        value = scalars()
        if inspect.isawaitable(value):
            value = await value
        all_getter = getattr(value, "all", None)
        if all_getter is None:
            return []
        items = all_getter()
        if inspect.isawaitable(items):
            items = await items
        return list(items or [])

    single_getter = getattr(result, "scalar_one_or_none", None)
    if single_getter is None:
        return []
    value = single_getter()
    if inspect.isawaitable(value):
        value = await value
    if value is None:
        return []
    if getattr(value, "started_at", None) is None and getattr(value, "skill_name", None) is None:
        return []
    return [value]


async def load_primary_follow_up_intervention(
    db: AsyncSession,
    user_id: str,
    user_message: str,
) -> Intervention | None:
    interventions = await load_recent_interventions(db, user_id)
    return select_primary_follow_up_intervention(interventions, user_message=user_message)


def tool_state_mentions_skill(tool_state: list[dict] | None, tool_name: str, skill_name: str) -> bool:
    for item in reversed(tool_state or []):
        if item.get("tool") != tool_name:
            continue
        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue
        if tool_name == "match_intervention":
            for plan in payload.get("plans", []):
                if isinstance(plan, dict) and plan.get("skill_name") == skill_name:
                    return True
        elif payload.get("skill_name") == skill_name:
            return True
    return False


def append_tool_state(
    tool_state: list[dict],
    *,
    tool_name: str,
    arguments: dict,
    call_id: str | None,
    envelope: dict,
    phase: str = "tool_result",
) -> dict:
    """追加统一 tool state 记录。"""
    entry = {
        "tool": tool_name,
        "arguments": arguments,
        "call_id": call_id,
        "payload": envelope.get("payload"),
        "error": envelope.get("error"),
        "status": envelope.get("status", "ok"),
        "phase": phase,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    tool_state.append(entry)
    return entry


async def preflight_tool_call(
    tool_name: str,
    arguments: dict,
    *,
    user_id: str,
    session_id: str,
    user_message: str,
    db: AsyncSession,
    tool_state: list[dict] | None = None,
) -> str | None:
    """高依赖工具的统一前置校验。"""
    if tool_name == "referral" and not arguments.get("urgency"):
        return json.dumps({
            "status": "blocked",
            "tool": tool_name,
            "reason": "missing_urgency",
            "message": "转介前必须显式给出 urgency，避免普通转介和危机转介混淆。",
        }, ensure_ascii=False)

    if tool_name == "save_session":
        end_keywords = ("先到这里", "先这样", "先聊到这里", "下次继续", "今天差不多了", "先这样吧", "结束吧", "不聊了")
        if not any(keyword in user_message for keyword in end_keywords):
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "missing_end_signal",
                "message": "只有当用户明确表达结束或暂停意图时，才应保存并结束会话。",
            }, ensure_ascii=False)

    if tool_name == "load_skill":
        skill_name = str(arguments.get("skill_name", ""))
        accepted_now = has_acceptance_signal(user_message)
        matched_in_context = tool_state_mentions_skill(tool_state, "match_intervention", skill_name)
        if not accepted_now and not matched_in_context:
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "missing_acceptance_signal",
                "message": "只有当用户已经接受方案、主动要求练习，或当前回合已先完成方案匹配时，才应加载具体 skill。",
            }, ensure_ascii=False)
        primary_intervention = await load_primary_follow_up_intervention(db, user_id, user_message)
        if (
            primary_intervention is not None
            and primary_intervention.skill_name == skill_name
            and intervention_needs_follow_up(primary_intervention)
        ):
            if not has_retry_signal(user_message) and not has_new_method_signal(user_message):
                return json.dumps({
                    "status": "blocked",
                    "tool": tool_name,
                    "reason": "recent_intervention_needs_follow_up",
                    "message": "这个练习刚在近 48 小时内做过，应该先跟进用户是否尝试、效果如何，再决定是否重复带做。",
                    "recent_skill_name": primary_intervention.skill_name,
                    "recent_relative_time": format_relative_time(primary_intervention.started_at),
                }, ensure_ascii=False)

    if tool_name == "record_outcome":
        skill_name = str(arguments.get("skill_name", ""))
        has_meaningful_payload = bool(
            arguments.get("completed")
            or arguments.get("user_feedback")
            or arguments.get("key_insight")
            or arguments.get("homework_description")
        )
        if not has_meaningful_payload:
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "insufficient_outcome_payload",
                "message": "记录干预结果前，至少需要完成态、用户反馈、关键洞察或作业信息中的一项。",
            }, ensure_ascii=False)
        has_skill_context = tool_state_mentions_skill(tool_state, "load_skill", skill_name)
        if not has_skill_context and not has_completion_signal(user_message):
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "missing_intervention_context",
                "message": "记录干预结果前，需要当前回合已加载对应 skill，或用户明确反馈已完成/已体验该练习。",
            }, ensure_ascii=False)

    if tool_name != "match_intervention":
        return None

    result = await db.execute(select(CaseFormulation).where(CaseFormulation.session_id == session_id))
    formulation = await safe_scalar_one_or_none(result)
    readiness = getattr(formulation, "readiness", None)
    if readiness in {"sufficient", "solid"}:
        primary_intervention = await load_primary_follow_up_intervention(db, user_id, user_message)
        if primary_intervention is not None and intervention_needs_follow_up(primary_intervention):
            if not has_new_method_signal(user_message) and not has_completion_signal(user_message):
                return json.dumps({
                    "status": "blocked",
                    "tool": tool_name,
                    "reason": "recent_intervention_needs_follow_up",
                    "message": "用户最近 48 小时内有尚未收口的干预，当前应先 follow-up 完成情况和效果，而不是立即重新推荐方案。",
                    "recent_skill_name": primary_intervention.skill_name,
                    "recent_relative_time": format_relative_time(primary_intervention.started_at),
                }, ensure_ascii=False)
        return None

    missing = []
    if formulation is not None and formulation.missing:
        missing = list(formulation.missing)

    return json.dumps({
        "status": "blocked",
        "tool": tool_name,
        "reason": "formulation_not_ready",
        "message": "当前 formulation 尚未成熟，应继续探索而不是立即推荐干预。",
        "missing": missing,
        "readiness": readiness or "missing",
    }, ensure_ascii=False)


async def execute_tool_runtime_call(
    tool_call,
    *,
    user_id: str,
    session_id: str,
    user_message: str,
    db: AsyncSession,
    tool_state: list[dict],
    execute_tool,
    preflight_tool,
    trace_collector: list[dict] | None = None,
) -> tuple[dict, dict, dict | None]:
    """执行单次 tool call，统一处理 guardrail、envelope、trace 与 tool state。"""
    started = time.perf_counter()
    parsed_args = json.loads(tool_call.arguments) if tool_call.arguments else {}
    raw_result = None
    try:
        raw_result = await preflight_tool(
            tool_name=tool_call.name,
            arguments=parsed_args,
            user_id=user_id,
            session_id=session_id,
            user_message=user_message,
            db=db,
            tool_state=tool_state,
        )
        if raw_result is None:
            raw_result = await execute_tool(
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                user_id=user_id,
                session_id=session_id,
                db=db,
            )
        envelope = normalize_tool_result(tool_call.name, raw_result)
        call_id = resolve_function_call_id(tool_call)
        append_tool_state(
            tool_state,
            tool_name=tool_call.name,
            arguments=parsed_args,
            call_id=call_id,
            envelope=envelope,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        serialized = dump_tool_envelope(envelope)
        if trace_collector is not None:
            trace_collector.append(build_tool_trace_entry(
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                result=serialized,
                success=True,
                latency_ms=latency_ms,
            ))
        if not call_id:
            raise ValueError(f"missing function call identifier for tool {tool_call.name}")
        pending_output = build_function_call_output(call_id, serialized)
        card_data = None
        payload = envelope.get("payload")
        if isinstance(payload, dict) and payload.get("card_data"):
            card_data = payload["card_data"]
        return envelope, pending_output, card_data
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        if trace_collector is not None:
            trace_collector.append(build_tool_trace_entry(
                tool_name=tool_call.name,
                arguments=tool_call.arguments,
                result=dump_tool_envelope(normalize_tool_result(tool_call.name, raw_result or str(exc))),
                success=False,
                latency_ms=latency_ms,
            ))
        raise
