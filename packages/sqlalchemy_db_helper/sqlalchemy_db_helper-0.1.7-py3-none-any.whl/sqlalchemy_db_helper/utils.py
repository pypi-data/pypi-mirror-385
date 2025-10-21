__all__ = (
    "db_startup",
    "db_shutdown",
    "get_async_session",
    "get_async_connection",
)

from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection

from .helper import AsyncDatabase

logger = getLogger(__name__)

db = AsyncDatabase()


async def db_startup(*args, **kwargs) -> None:
    await db.init(*args, **kwargs)


async def db_shutdown() -> None:
    await db.close()


@asynccontextmanager
async def get_async_connection() -> AbstractAsyncContextManager[AsyncConnection]:
    async with db.connect() as conn:  # type: AsyncConnection
        yield conn


@asynccontextmanager
async def get_async_session() -> AbstractAsyncContextManager[AsyncSession]:
    async with db.session() as async_session:  # type: AsyncSession
        yield async_session
