from typing import Annotated

from aiomysql import Connection
from fastapi import APIRouter, Depends
from opensearchpy import AsyncOpenSearch
from starlette.status import HTTP_204_NO_CONTENT

from app.core.mysql.dependencies import get_mysql_connection
from app.core.opensearch.dependencies import get_opensearch_client
from app.modules.messages.dao import MessagesDAO
from app.modules.messages.schemes import MessageScheme

PATH = "/messages/"

router = APIRouter(tags=["Messages"])


@router.post(PATH, status_code=HTTP_204_NO_CONTENT)
async def add_message(
    text: str,
    mysql_connection: Annotated[Connection, Depends(get_mysql_connection)],
    opensearch_client: Annotated[AsyncOpenSearch, Depends(get_opensearch_client)],
) -> None:
    dao = MessagesDAO(mysql_connection=mysql_connection, opensearch_client=opensearch_client)
    await dao.add_message(text)
    await mysql_connection.commit()
    return


@router.get(PATH)
async def search_message(
    search_string: str,
    mysql_connection: Annotated[Connection, Depends(get_mysql_connection)],
    opensearch_client: Annotated[AsyncOpenSearch, Depends(get_opensearch_client)],
) -> list[MessageScheme]:
    dao = MessagesDAO(mysql_connection=mysql_connection, opensearch_client=opensearch_client)
    result = await dao.search_messages(search_string)
    return result
