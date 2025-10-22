

from latticeflow.go._generated.api.chat.create_chat_completion import (
    asyncio as create_chat_completion_asyncio,
)
from latticeflow.go._generated.api.chat.create_chat_completion import (
    sync as create_chat_completion_sync,
)
from latticeflow.go._generated.models.model import CreateChatCompletionRequest
from latticeflow.go._generated.models.model import CreateChatCompletionResponse
from latticeflow.go._generated.models.model import Error
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class ChatResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def create_chat_completion(
        self, body: CreateChatCompletionRequest
    ) -> CreateChatCompletionResponse:
        """Create an assistant chat completion

        Args:
            body (CreateChatCompletionRequest):
        """
        with self._base.get_client() as client:
            response = create_chat_completion_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncChatResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def create_chat_completion(
        self, body: CreateChatCompletionRequest
    ) -> CreateChatCompletionResponse:
        """Create an assistant chat completion

        Args:
            body (CreateChatCompletionRequest):
        """
        with self._base.get_client() as client:
            response = await create_chat_completion_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response
