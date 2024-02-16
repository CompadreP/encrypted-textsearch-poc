from opensearchpy import AsyncOpenSearch
from starlette.requests import Request


async def get_opensearch_client(request: Request) -> AsyncOpenSearch:
    opensearch_client: AsyncOpenSearch = request.app.state.opensearch_client
    return opensearch_client
