import datetime
from base64 import b64decode, b64encode

from aiomysql import Connection
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from opensearchpy import AsyncOpenSearch

from app.modules.messages.schemes import MessageScheme, OpenSearchResultScheme
from config import settings


class MessagesDAO:
    def __init__(self, mysql_connection: Connection, opensearch_client: AsyncOpenSearch):
        self._mysql_connection = mysql_connection
        self._opensearch_client = opensearch_client

    def _get_nonce(self) -> bytes:
        """
        here we can return for example client organization id to make encrypted values unique for particular
        organization
        """
        return b"11111111"

    def _get_aesgcm(self) -> AESGCM:
        aesgcm = AESGCM(b64decode(settings.MESSAGE_ENCRYPTION_KEY))
        return aesgcm

    def _encrypt_word(self, aesgcm: AESGCM, word: str) -> str:
        result = aesgcm.encrypt(
            nonce=self._get_nonce(),
            data=word.encode(),
            associated_data=None,
        )
        b64_str = b64encode(result).decode()
        return b64_str

    def _decrypt_word(self, aesgcm: AESGCM, encrypted_word: str) -> str:
        result = aesgcm.decrypt(
            nonce=self._get_nonce(),
            data=b64decode(encrypted_word),
            associated_data=None,
        )
        return result.decode()

    def _encrypt_message(self, message: str) -> str:
        aesgcm = self._get_aesgcm()
        encrypted_lines = []
        for line in message.splitlines():
            encrypted_line = []
            for word in line.split(" "):
                encrypted_line.append(self._encrypt_word(aesgcm=aesgcm, word=word))
            encrypted_lines.append(" ".join(encrypted_line))
        return "\n".join(encrypted_lines)

    def _decrypt_message(self, encrypted_message: str) -> str:
        aesgcm = self._get_aesgcm()
        decrypted_lines = []
        for line in encrypted_message.splitlines():
            decrypted_line = []
            for encrypted_word in line.split(" "):
                decrypted_line.append(self._decrypt_word(aesgcm=aesgcm, encrypted_word=encrypted_word))
            decrypted_lines.append(" ".join(decrypted_line))
        return "\n".join(decrypted_lines)

    async def _put_message_to_mysql(self, encrypted_text: str) -> int:
        query = "INSERT INTO message (text, created_at) VALUES (%(text)s, %(created_at)s)"

        async with self._mysql_connection.cursor() as cur:
            await cur.execute(query, {"text": encrypted_text, "created_at": datetime.datetime.utcnow()})
            await cur.execute("SELECT LAST_INSERT_ID() as inserted_id")
            inserted_id = (await cur.fetchone())["inserted_id"]
        return inserted_id

    async def _index_message_in_opensearch(
        self,
        message_id: int,
        encrypted_text: str,
    ) -> None:
        await self._opensearch_client.index(
            index=settings.OPENSEARCH_MESSAGES_INDEX_NAME,
            id=message_id,
            body={"encrypted_text": encrypted_text},
            refresh=True,
        )

    async def _search_encrypted_message_in_opensearch(
        self,
        encrypted_message: str,
    ):
        result = await self._opensearch_client.search(
            body={
                "query": {
                    "match": {
                        "encrypted_text": encrypted_message,
                    }
                }
            },
            index=settings.OPENSEARCH_MESSAGES_INDEX_NAME,
        )
        return result

    async def add_message(self, text: str) -> None:
        encrypted_message = self._encrypt_message(text)
        message_id = await self._put_message_to_mysql(encrypted_message)
        await self._index_message_in_opensearch(message_id=message_id, encrypted_text=encrypted_message)

    async def _search_messages_in_opensearch(self, search_string: str) -> list[OpenSearchResultScheme]:
        encrypted_message = self._encrypt_message(message=search_string)
        opensearch_response = await self._search_encrypted_message_in_opensearch(encrypted_message=encrypted_message)
        return [
            OpenSearchResultScheme(id=hit["_id"], encrypted_text=hit["_source"]["encrypted_text"])
            for hit in opensearch_response["hits"]["hits"]
        ]

    async def _get_additional_info_from_db(self, message_ids: list[int]) -> dict[int, datetime.datetime]:
        query = "SELECT id, created_at FROM message WHERE id IN %(message_ids)s"

        async with self._mysql_connection.cursor() as cur:
            await cur.execute(query, {"message_ids": message_ids})
            result = await cur.fetchall()
        return {row["id"]: row["created_at"] for row in result}

    async def search_messages(self, search_string: str) -> list[MessageScheme]:
        # response = await self._opensearch_client.indices.delete(
        #     index=settings.OPENSEARCH_MESSAGES_INDEX_NAME
        # )
        opensearch_results = await self._search_messages_in_opensearch(search_string)
        additional_info = await self._get_additional_info_from_db(
            [opensearch_result.id for opensearch_result in opensearch_results]
        )
        results = []
        for opensearch_result in opensearch_results:
            results.append(
                MessageScheme(
                    text=self._decrypt_message(opensearch_result.encrypted_text),
                    created_at=additional_info[opensearch_result.id],
                )
            )
        return results
