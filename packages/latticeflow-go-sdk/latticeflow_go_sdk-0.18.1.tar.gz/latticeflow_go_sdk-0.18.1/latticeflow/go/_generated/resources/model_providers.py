

from latticeflow.go._generated.api.model_providers.get_model_providers import (
    asyncio as get_model_providers_asyncio,
)
from latticeflow.go._generated.api.model_providers.get_model_providers import (
    sync as get_model_providers_sync,
)
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import ModelProviders
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class ModelProvidersResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def get_model_providers(self) -> ModelProviders:
        """Get all model providers"""
        with self._base.get_client() as client:
            response = get_model_providers_sync(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncModelProvidersResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def get_model_providers(self) -> ModelProviders:
        """Get all model providers"""
        with self._base.get_client() as client:
            response = await get_model_providers_asyncio(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response
