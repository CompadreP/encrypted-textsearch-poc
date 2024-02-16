import logging
from types import TracebackType
from typing import Type

import aiomysql
from aiomysql import DictCursor, Pool

from app.core.mysql.errors import MySQLPoolIsAlreadyInitializedError, MySQLPoolIsNotInitializedError
from config import settings

logger = logging.getLogger(__name__)


class MySQLPoolManager:
    def __init__(self) -> None:
        self._pool: Pool | None = None

    async def __aenter__(self) -> Pool:
        if self._pool:
            raise MySQLPoolIsAlreadyInitializedError()
        try:
            self._pool = await aiomysql.create_pool(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                db=settings.MYSQL_DB_NAME,
                minsize=settings.MYSQL_MIN_POOL_SIZE,
                maxsize=settings.MYSQL_MAX_POOL_SIZE,
                pool_recycle=settings.MYSQL_POOL_RECYCLE_SECONDS,
                autocommit=False,
                cursorclass=DictCursor,
            )
            return self._pool
        except Exception:
            raise MySQLPoolIsNotInitializedError

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        if exc_type is not None and exc_val is not None:
            logger.exception(
                "Could not close MySQL connection.",
                exc_info=(
                    exc_type,
                    exc_val,
                    exc_tb,
                ),
            )
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
