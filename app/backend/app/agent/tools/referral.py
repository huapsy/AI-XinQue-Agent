"""referral — 转介咨询师

生成咨询师转介卡片，任意阶段可调用。
根据场景区分普通转介（只显示 EAP）和危机转介（显示全部热线）。
"""

import json

TOOL_DEFINITION = {
    "type": "function",
    "name": "referral",
    "description": (
        "当你判断用户的问题超出心雀的能力范围、"
        "或用户主动要求找真人咨询师时调用。"
        "返回结构化的转介卡片数据，前端会渲染为卡片展示给用户。"
        "urgency 参数：'normal' 表示用户主动要求找咨询师（只显示预约入口），"
        "'crisis' 表示检测到危机风险（显示全部热线）。"
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "转介原因，如'用户主动要求'、'问题超出心雀能力'",
            },
            "urgency": {
                "type": "string",
                "description": "紧急程度：normal（普通转介）或 crisis（危机转介）",
                "enum": ["normal", "crisis"],
            },
        },
        "required": ["urgency"],
    },
}

# 普通转介：用户主动要求找咨询师
REFERRAL_CARD_NORMAL = {
    "type": "referral",
    "title": "预约专业咨询师",
    "description": "你可以通过 EAP 员工援助计划预约专业咨询师，获得一对一的支持",
    "resources": [
        {
            "name": "EAP 员工援助计划",
            "description": "专业咨询师一对一服务",
            "url": "https://www.eap.com.cn",
            "action": "预约咨询师",
        },
    ],
}

# 危机转介：检测到自杀/自伤风险
REFERRAL_CARD_CRISIS = {
    "type": "referral",
    "title": "紧急支持资源",
    "description": "如果你现在需要帮助，请联系以下资源",
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
    urgency = arguments.get("urgency", "crisis")

    card = REFERRAL_CARD_CRISIS if urgency == "crisis" else REFERRAL_CARD_NORMAL

    return json.dumps({
        "card_data": card,
        "reason": reason,
        "message": "已生成转介卡片",
    }, ensure_ascii=False)
