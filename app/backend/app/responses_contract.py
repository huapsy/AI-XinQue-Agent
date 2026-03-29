"""Responses-first 运行时分层契约。"""

from __future__ import annotations

from app.responses_helpers import build_response_input, make_response_message


RUNTIME_LAYER_DEFINITIONS = {
    "instructions": "当前请求级高优先级行为约束。适用于本次生成，不自动跨轮继承。",
    "working_contract": "跨轮必须可见的最小行为契约。当走 stateful previous_response_id 时，以 assistant message 注入。",
    "working_context": "分层会话状态、语义摘要与稳定背景的运行时上下文。",
    "previous_response_id": "Responses 服务端上下文串接标识。仅负责串接，不替代产品级 contract；只在 stateful store=true 模式下启用。",
    "store": "是否启用 Responses 的服务端状态。关闭时必须回退到 stateless 完整输入路径。",
}


def build_working_contract_message(alignment_score: int | None, turn_number: int) -> str:
    """构造跨轮仍需可见的最小契约。"""
    lines = [
        "最小系统契约：保持自然中文；遵守安全边界；不要越级推进；工具调用必须满足前置条件。",
        "回复风格：默认自然 prose，不使用列表、编号或文档腔；句子普遍较短，认知负担低。",
        "推进方式：默认探索驱动，而不是建议驱动；尤其在负向 flow 中优先接住、正常化、收束到更具体的问题点，再问一个具体问题。",
        "表达要求：所有总结、归因、机制判断都按工作性假设表达，不写成确定事实或诊断式结论。",
    ]
    if turn_number <= 2:
        lines.append("回合纪律：当前仍属早期轮次，优先建立理解与上下文，不要过早推荐干预。")
    if turn_number >= 6:
        lines.append("长会话纪律：优先复用已有总结与状态，不要机械重放完整历史。")
    if alignment_score is not None:
        if alignment_score <= 0:
            lines.append("对齐警告：用户当前高度不对齐，只做接纳和倾听，不做功能性推进。")
        elif alignment_score <= 5:
            lines.append("对齐状态较低：先修复理解和关系，不要直接推进新的建议或干预。")
    return "\n".join(lines)


def should_use_stateful_responses(store_enabled: bool, previous_response_id: str | None) -> bool:
    """判断当前是否应走 stateful Responses 模式。"""
    return bool(store_enabled and previous_response_id)


def build_runtime_input(
    *,
    effective_history: list[dict],
    user_message: str,
    alignment_score: int | None,
    turn_number: int,
    previous_response_id: str | None,
    store_enabled: bool,
) -> tuple[list[dict], str | None]:
    """根据 store/previous_response_id 构造本轮 Responses 输入。"""
    if should_use_stateful_responses(store_enabled, previous_response_id):
        return [
            make_response_message(
                "assistant",
                build_working_contract_message(alignment_score, turn_number),
                phase="commentary",
            ),
            make_response_message("assistant", effective_history[0]["content"], phase="commentary"),
            make_response_message("user", user_message),
        ], previous_response_id

    return build_response_input(effective_history, user_message), None


def extend_stateless_input_with_tool_outputs(pending_input: list[dict], tool_outputs: list[dict]) -> list[dict]:
    """在 stateless 模式下把 tool output 累积进下一次请求输入。"""
    return [*pending_input, *tool_outputs]
