from aiomysql import Connection, InterfaceError, Pool
from fastapi import Depends
from starlette.requests import Request


async def get_mysql_pool(request: Request) -> Pool:
    mysql_pool: Pool = request.app.state.mysql_pool
    return mysql_pool


async def get_mysql_connection(mysql_pool: Pool = Depends(get_mysql_pool)) -> Connection:
    async with mysql_pool.acquire() as conn:  # type: Connection
        await conn.begin()
        try:
            yield conn
        except Exception:
            try:
                await conn.rollback()
            except InterfaceError:
                pass
