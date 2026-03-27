"""数据库引擎和会话工厂"""

import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# 数据库文件存放在 app/backend/data/ 目录
_data_dir = Path(__file__).resolve().parent.parent.parent / "data"
_data_dir.mkdir(exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{_data_dir / 'xinque.db'}",
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """FastAPI 依赖注入用的异步数据库会话"""
    async with async_session() as session:
        yield session
