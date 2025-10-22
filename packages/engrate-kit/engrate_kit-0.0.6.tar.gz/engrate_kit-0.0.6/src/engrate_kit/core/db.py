from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

engine: AsyncEngine | None = None
session_maker: async_sessionmaker[AsyncSession] | None = None


@asynccontextmanager
async def db_lifespan(app):
    """Set up and tear down the database engine/sessionmaker."""
    global engine, session_maker

    engine = create_async_engine(
        app.settings.DB_URL,
        echo=app.settings.DB_ECHO_SQL,
        pool_pre_ping=True,
    )
    session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    yield

    await engine.dispose()
    engine = None
    session_maker = None


async def get_session() -> AsyncIterator[AsyncSession]:
    """Provide a session for use in dependencies."""
    assert session_maker is not None, "Database not initialized"
    async with session_maker() as session:
        try:
            yield session  # <-- must yield
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
