"""render_card — 统一卡片渲染 payload。"""

import json

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "render_card",
        "description": "将结构化的练习、清单或书写任务转换为前端可渲染的 card_data。",
        "parameters": {
            "type": "object",
            "properties": {
                "card_type": {"type": "string", "enum": ["guided_exercise", "journal", "checklist", "referral"]},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "steps": {"type": "array"},
                "fields": {"type": "array"},
                "items": {"type": "array"},
                "resources": {"type": "array"},
                "footer": {"type": "string"},
            },
            "required": ["card_type", "title"],
        },
    },
}


def _normalize_fields(fields: list) -> list[dict]:
    normalized = []
    for field in fields:
        if isinstance(field, dict):
            normalized.append({"label": field.get("label", ""), "placeholder": field.get("placeholder", "")})
        else:
            normalized.append({"label": str(field), "placeholder": ""})
    return normalized


def _normalize_items(items: list) -> list[dict]:
    normalized = []
    for item in items:
        if isinstance(item, dict):
            normalized.append({"label": item.get("label", ""), "checked": bool(item.get("checked", False))})
        else:
            normalized.append({"label": str(item), "checked": False})
    return normalized


async def execute(arguments: dict) -> str:
    card_type = arguments.get("card_type")
    card_data = {
        "type": card_type,
        "title": arguments.get("title"),
        "description": arguments.get("description"),
    }
    if card_type == "journal":
        card_data["fields"] = _normalize_fields(arguments.get("fields", []))
    elif card_type == "checklist":
        card_data["items"] = _normalize_items(arguments.get("items", []))
    elif card_type == "referral":
        card_data["resources"] = arguments.get("resources", [])
        card_data["footer"] = arguments.get("footer")
    else:
        card_data["steps"] = arguments.get("steps", [])

    return json.dumps({"status": "ok", "card_data": card_data}, ensure_ascii=False)
