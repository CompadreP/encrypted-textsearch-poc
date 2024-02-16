from types import TracebackType
from typing import Type

from opensearchpy import AsyncOpenSearch

from config import settings


class OpenSearchClientManager:
    async def __aenter__(self) -> AsyncOpenSearch:
        connection_params = {"host": settings.OPENSEARCH_HOST}
        if opensearch_port := settings.get("OPENSEARCH_PORT"):
            connection_params["port"] = opensearch_port
        client_kwargs = {
            "hosts": [connection_params],
            "use_ssl": settings.OPENSEARCH_USE_SSL,
        }
        if (opensearch_login := settings.get("OPENSEARCH_LOGIN")) and (
            opensearch_password := settings.get("OPENSEARCH_PASSWORD")
        ):
            client_kwargs["http_auth"] = opensearch_login, opensearch_password
        self._client: AsyncOpenSearch = AsyncOpenSearch(**client_kwargs)
        return self._client

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._client.close()
