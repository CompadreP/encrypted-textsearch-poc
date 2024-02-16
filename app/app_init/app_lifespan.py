from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.mysql.pool_manager import MySQLPoolManager
from app.core.opensearch.client import OpenSearchClientManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with (
        MySQLPoolManager() as mysql_pool,
        OpenSearchClientManager() as opensearch_client,
    ):
        app.state.mysql_pool = mysql_pool
        app.state.opensearch_client = opensearch_client
        yield
