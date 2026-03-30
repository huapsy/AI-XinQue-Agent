"""运行时配置。"""

from __future__ import annotations

import os


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"0", "false", "off", "no"}:
        return False
    if value in {"1", "true", "on", "yes"}:
        return True
    return default


def get_cors_origins() -> list[str]:
    """读取允许的 CORS 来源，未配置时回退到本地开发端口。"""
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or DEFAULT_CORS_ORIGINS


def get_responses_store_enabled() -> bool:
    """读取 Responses store 开关。"""
    return _env_flag("XINQUE_RESPONSES_STORE", True)


def get_otel_enabled() -> bool:
    """读取 OTel 导出开关。"""
    return _env_flag("XINQUE_OTEL_ENABLED", False)


def get_otel_exporter_endpoint() -> str | None:
    """读取 OTel exporter endpoint。"""
    raw = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    return raw or None


def get_encryption_key_version() -> str:
    """读取当前写入使用的加密密钥版本。"""
    raw = os.getenv("XINQUE_ENCRYPTION_KEY_VERSION", "").strip()
    return raw or "v1"
