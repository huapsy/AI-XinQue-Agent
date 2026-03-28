"""应用层字段加密辅助函数。"""

from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

_PREFIX = "enc::"


def require_encryption_key() -> str:
    """读取加密密钥；缺失时显式失败。"""
    secret = os.getenv("XINQUE_ENCRYPTION_KEY")
    if not secret:
        raise RuntimeError("XINQUE_ENCRYPTION_KEY is required")
    return secret


def _build_fernet() -> Fernet:
    secret = require_encryption_key().encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
    return Fernet(key)


def is_encrypted(value: str | None) -> bool:
    return bool(value and value.startswith(_PREFIX))


def encrypt_text(value: str | None) -> str:
    text = value or ""
    if not text or is_encrypted(text):
        return text
    token = _build_fernet().encrypt(text.encode("utf-8")).decode("utf-8")
    return _PREFIX + token


def decrypt_text(value: str | None) -> str:
    text = value or ""
    if not is_encrypted(text):
        return text
    token = text[len(_PREFIX):]
    try:
        return _build_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return text
