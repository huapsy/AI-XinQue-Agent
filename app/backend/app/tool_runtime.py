"""Tool runtime：统一 preflight、state、trace 与 envelope。"""

from __future__ import annotations

import inspect
import json
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.phase_profiles import get_phase_profile
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


def has_positive_sentiment_signal(user_message: str) -> bool:
    signals = (
        "开心", "高兴", "很高兴", "挺开心", "挺高兴", "轻松", "满足",
        "自豪", "兴奋", "踏实", "舒服", "成就感", "被认可", "被表扬",
    )
    return any(signal in user_message for signal in signals)


def has_negative_dominant_signal(user_message: str) -> bool:
    signals = (
        "焦虑", "难受", "痛苦", "撑不住", "崩溃", "压力很大", "害怕",
        "烦", "低落", "沮丧", "失眠", "胸闷", "想哭",
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


def resolve_active_skill_state(
    previous_active_skill: dict | None,
    tool_state: list[dict] | None,
    user_message: str,
) -> dict:
    """根据上一轮状态、本轮 tool 结果和当前用户消息，推导新的 active skill。"""
    active_skill = dict(previous_active_skill or {})
    if active_skill and has_new_method_signal(user_message):
        active_skill = {}

    for item in tool_state or []:
        if item.get("status") != "ok":
            continue
        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue

        if item.get("tool") == "load_skill" and payload.get("skill_name"):
            active_skill = {
                "skill_name": payload.get("skill_name"),
                "display_name": payload.get("display_name"),
                "completion_signals": payload.get("completion_signals", []),
                "activated_at": item.get("recorded_at"),
            }
        elif item.get("tool") == "record_outcome":
            recorded_skill_name = payload.get("skill_name") or (item.get("arguments") or {}).get("skill_name")
            if active_skill and recorded_skill_name == active_skill.get("skill_name"):
                active_skill = {}

    return active_skill


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
    active_phase: str | None = None,
    active_skill: dict | None = None,
) -> str | None:
    """高依赖工具的统一前置校验。"""
    if active_phase:
        allowed_tools = set(get_phase_profile(active_phase).allowed_tools)
        if tool_name not in allowed_tools:
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "phase_tool_not_allowed",
                "message": f"当前阶段 {active_phase} 不应调用 {tool_name}，应优先遵守该阶段子Agent的工具边界。",
                "active_phase": active_phase,
                "allowed_tools": sorted(allowed_tools),
            }, ensure_ascii=False)

    effective_active_skill = resolve_active_skill_state(active_skill, tool_state, user_message)
    active_skill_name = str(effective_active_skill.get("skill_name") or "")
    if active_skill_name and not has_new_method_signal(user_message):
        if tool_name == "match_intervention":
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "active_skill_in_progress",
                "message": f"当前已有正在执行的 skill（{active_skill_name}），未完成前应优先继续该 skill，除非用户明确要求切换方法。",
                "active_skill": active_skill_name,
            }, ensure_ascii=False)
        if tool_name == "load_skill":
            requested_skill_name = str(arguments.get("skill_name", ""))
            if requested_skill_name != active_skill_name:
                return json.dumps({
                    "status": "blocked",
                    "tool": tool_name,
                    "reason": "active_skill_in_progress",
                    "message": f"当前已有正在执行的 skill（{active_skill_name}），未完成前不应切换到新的 skill，除非用户明确要求换方法。",
                    "active_skill": active_skill_name,
                }, ensure_ascii=False)

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
        if skill_name == "positive_experience_consolidation":
            if has_positive_sentiment_signal(user_message) and not has_negative_dominant_signal(user_message):
                return None
            return json.dumps({
                "status": "blocked",
                "tool": tool_name,
                "reason": "positive_sentiment_not_clear",
                "message": "只有当用户当前明确处于积极情绪路径，且没有明显负面情绪主导时，才应直接进入积极体验巩固 skill。",
            }, ensure_ascii=False)
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
    active_phase: str | None = None,
    active_skill: dict | None = None,
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
            active_phase=active_phase,
            active_skill=active_skill,
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
