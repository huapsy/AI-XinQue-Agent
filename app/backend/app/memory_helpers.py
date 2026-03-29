"""情景记忆提取与检索辅助函数。"""

from __future__ import annotations

import re
from collections import Counter
from hashlib import sha256
from math import sqrt

from app.encryption_helpers import decrypt_text, encrypt_text
from app.privacy_helpers import redact_sensitive_text


def embed_text(text: str, dims: int = 16) -> list[float]:
    """将文本映射为固定长度向量。"""
    vector = [0.0] * dims
    for index, token in enumerate(_tokenize(text)):
        digest = sha256(f"{index}:{token}".encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % dims
        vector[bucket] += 1.0
    norm = sqrt(sum(value * value for value in vector)) or 1.0
    return [round(value / norm, 6) for value in vector]


def _tokenize(text: str) -> list[str]:
    """对中英文混合文本做轻量切词。"""
    normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", text.lower())
    tokens = [token for token in normalized.split() if token]
    chars = [char for char in text if "\u4e00" <= char <= "\u9fff"]
    bigrams = ["".join(chars[index:index + 2]) for index in range(len(chars) - 1)]
    if tokens:
        return tokens + chars + bigrams
    return chars + bigrams


def _infer_topic(text: str, context: dict | None) -> str:
    """根据上下文和文本推断 topic。"""
    domain = (context or {}).get("domain")
    if domain:
        return domain
    if any(keyword in text for keyword in ("妈妈", "爸爸", "家里", "住院", "老公", "老婆")):
        return "family_health"
    if any(keyword in text for keyword in ("领导", "同事", "开会", "上班", "工作")):
        return "workplace"
    return "other"


def build_memory_candidate(message: str, context: dict | None = None) -> dict | None:
    """从用户消息中提取值得沉淀的情景记忆候选。"""
    stripped = message.strip()
    if len(stripped) < 8:
        return None
    low_information = {"嗯", "好的", "知道了", "是的", "不是", "谢谢", "还行"}
    if stripped in low_information:
        return None

    important_keywords = (
        "住院", "离职", "分手", "结婚", "离婚", "去世", "手术",
        "换领导", "裁员", "开会", "妈妈", "爸爸", "孩子", "老公", "老婆",
    )
    if not any(keyword in stripped for keyword in important_keywords) and len(stripped) < 18:
        return None

    emotions = list((context or {}).get("emotions", []))
    sanitized = redact_sensitive_text(stripped, limit=240)
    return {
        "content": sanitized,
        "topic": _infer_topic(stripped, context),
        "emotions": emotions,
        "embedding": embed_text(sanitized),
    }


def _similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
    """基于 token 重叠的轻量相似度。"""
    if not tokens_a or not tokens_b:
        return 0.0
    count_a = Counter(tokens_a)
    count_b = Counter(tokens_b)
    overlap = sum(min(count_a[token], count_b[token]) for token in set(count_a) & set(count_b))
    return overlap / max(len(tokens_a), len(tokens_b))


def is_duplicate_memory(candidate: dict, existing_memories: list[dict], threshold: float = 0.5) -> bool:
    """判断候选记忆是否与现有内容近似重复。"""
    candidate_tokens = _tokenize(candidate.get("content", ""))
    for memory in existing_memories:
        score = _similarity(candidate_tokens, _tokenize(memory.get("content", "")))
        if score >= threshold:
            return True
    return False


def rank_memories_by_query(query: str, memories: list[dict]) -> list[dict]:
    """按 query 相似度对 memories 排序。"""
    return [memory for memory, _score in score_memories_by_query(query, memories) if _score >= 0.18]


def score_memories_by_query(query: str, memories: list[dict]) -> list[tuple[dict, float]]:
    """计算 query 与 memories 的相似度分数。"""
    query_embedding = embed_text(query)
    query_tokens = _tokenize(query)

    def score(memory: dict) -> float:
        embedding = memory.get("embedding")
        if isinstance(embedding, list) and embedding and isinstance(embedding[0], (int, float)):
            compare = embedding
            semantic_score = sum(a * b for a, b in zip(query_embedding, compare))
            lexical_score = _similarity(query_tokens, _tokenize(memory.get("content", "")))
        elif isinstance(embedding, list) and embedding:
            semantic_score = 0.0
            lexical_score = _similarity(query_tokens, [str(item) for item in embedding])
        else:
            compare = embed_text(memory.get("content", ""))
            semantic_score = sum(a * b for a, b in zip(query_embedding, compare))
            lexical_score = _similarity(query_tokens, _tokenize(memory.get("content", "")))
        if lexical_score == 0:
            return semantic_score * 0.2
        return semantic_score * 0.6 + lexical_score * 0.4

    scored = [(memory, score(memory)) for memory in memories]
    return sorted(scored, key=lambda item: item[1], reverse=True)


async def maybe_store_episodic_memory(
    db,
    memory_model,
    user_id: str,
    session_id: str,
    user_message: str,
    formulation_context: dict | None = None,
) -> None:
    """按最小策略沉淀情景记忆。"""
    candidate = build_memory_candidate(user_message, formulation_context)
    if candidate is None:
        return

    result = await db.execute(memory_model.select_by_user(user_id))
    existing = result.scalars().all()
    if is_duplicate_memory(candidate, [{"content": decrypt_text(item.content)} for item in existing]):
        return

    db.add(memory_model(
        user_id=user_id,
        session_id=session_id,
        content=encrypt_text(candidate["content"]),
        topic=candidate["topic"],
        emotions=candidate["emotions"],
        embedding=candidate["embedding"],
    ))
