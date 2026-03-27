"""心雀核心 Agent

单一 LLM + Tool Use 自主推理循环（类 ReAct 模式，Thought 不外显）。
"""

import json
import os

from openai import AsyncAzureOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.system_prompt import build_system_prompt
from app.agent.tools import (
    formulate,
    load_skill,
    match_intervention,
    recall_context,
    record_outcome,
    referral,
    save_nickname,
)

# 注册的 Tool 定义列表
TOOL_DEFINITIONS = [
    recall_context.TOOL_DEFINITION,
    formulate.TOOL_DEFINITION,
    save_nickname.TOOL_DEFINITION,
    match_intervention.TOOL_DEFINITION,
    load_skill.TOOL_DEFINITION,
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
    if tool_name == "formulate":
        return await formulate.execute(session_id, user_id, args, db)
    if tool_name == "save_nickname":
        return await save_nickname.execute(user_id, args, db)
    if tool_name == "match_intervention":
        return await match_intervention.execute(session_id, user_id, db)
    if tool_name == "load_skill":
        return await load_skill.execute(args)
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
) -> dict:
    """执行一轮对话，返回 {"reply": str, "card_data": dict | None}"""
    messages = [
        {"role": "system", "content": build_system_prompt(alignment_score)},
        *history,
        {"role": "user", "content": user_message},
    ]

    card_data = None  # 本轮是否有卡片数据

    # Tool Use 自主推理循环
    max_iterations = 10
    for _ in range(max_iterations):
        response = await client.chat.completions.create(
            model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            messages=messages,
            tools=TOOL_DEFINITIONS,
        )

        choice = response.choices[0]

        # LLM 决定调用 Tool
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls:
                result = await _execute_tool(
                    tool_name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                    user_id=user_id,
                    session_id=session_id,
                    db=db,
                )

                # 如果 load_skill 或 referral 返回了 card_data，提取出来
                if tool_call.function.name in ("load_skill", "referral"):
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
            continue

        # LLM 生成了最终回复
        return {
            "reply": choice.message.content or "",
            "card_data": card_data,
        }

    return {
        "reply": "抱歉，我需要一点时间整理思路。你刚才说的是什么呢？",
        "card_data": None,
    }
