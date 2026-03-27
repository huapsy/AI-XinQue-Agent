"""referral — 转介咨询师

生成咨询师转介卡片，任意阶段可调用。
"""

import json

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "referral",
        "description": (
            "当你判断用户的问题超出心雀的能力范围、"
            "或用户主动要求找真人咨询师时调用。"
            "返回结构化的转介卡片数据（含 EAP 链接和热线号码），"
            "前端会渲染为卡片展示给用户。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "转介原因，如'用户主动要求'、'问题超出心雀能力'",
                },
            },
            "required": [],
        },
    },
}

REFERRAL_CARD = {
    "type": "referral",
    "title": "专业咨询师支持",
    "description": "如果你觉得需要更专业的支持，可以联系以下资源",
    "resources": [
        {
            "name": "EAP 员工援助计划",
            "description": "专业咨询师一对一服务",
            "url": "https://www.eap.com.cn",
            "action": "预约咨询师",
        },
        {
            "name": "24小时心理援助热线",
            "phone": "400-161-9995",
        },
        {
            "name": "北京心理危机研究与干预中心",
            "phone": "010-82951332",
        },
        {
            "name": "生命热线",
            "phone": "400-821-1215",
        },
    ],
    "footer": "紧急情况请拨打 120 或 110",
}


async def execute(arguments: dict) -> str:
    """执行 referral，返回转介卡片 JSON"""
    reason = arguments.get("reason", "用户需要专业支持")

    return json.dumps({
        "card_data": REFERRAL_CARD,
        "reason": reason,
        "message": "已生成转介卡片",
    }, ensure_ascii=False)
