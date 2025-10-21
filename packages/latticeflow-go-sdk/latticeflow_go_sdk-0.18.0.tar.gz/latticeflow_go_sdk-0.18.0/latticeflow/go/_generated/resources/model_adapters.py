from typing import Union

from latticeflow.go._generated.api.model_adapters.create_model_adapter import (
    asyncio as create_model_adapter_asyncio,
)
from latticeflow.go._generated.api.model_adapters.create_model_adapter import (
    sync as create_model_adapter_sync,
)
from latticeflow.go._generated.api.model_adapters.delete_model_adapter import (
    asyncio as delete_model_adapter_asyncio,
)
from latticeflow.go._generated.api.model_adapters.delete_model_adapter import (
    sync as delete_model_adapter_sync,
)
from latticeflow.go._generated.api.model_adapters.get_model_adapter import (
    asyncio as get_model_adapter_asyncio,
)
from latticeflow.go._generated.api.model_adapters.get_model_adapter import (
    sync as get_model_adapter_sync,
)
from latticeflow.go._generated.api.model_adapters.get_model_adapters import (
    asyncio as get_model_adapters_asyncio,
)
from latticeflow.go._generated.api.model_adapters.get_model_adapters import (
    sync as get_model_adapters_sync,
)
from latticeflow.go._generated.api.model_adapters.update_model_adapter import (
    asyncio as update_model_adapter_asyncio,
)
from latticeflow.go._generated.api.model_adapters.update_model_adapter import (
    sync as update_model_adapter_sync,
)
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import ModelAdapter
from latticeflow.go._generated.models.model import StoredModelAdapter
from latticeflow.go._generated.models.model import StoredModelAdapters
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class ModelAdaptersResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def get_model_adapter(self, model_adapter_id: str) -> StoredModelAdapter:
        """Get the model adapter

        Args:
            model_adapter_id (str):
        """
        with self._base.get_client() as client:
            response = get_model_adapter_sync(
                model_adapter_id=model_adapter_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_model_adapters(
        self, *, key: Union[Unset, str] = UNSET
    ) -> StoredModelAdapters:
        """Get all model adapters

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_model_adapters_sync(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_model_adapter(self, model_adapter_id: str) -> Success:
        """Delete the model adapter

        Args:
            model_adapter_id (str):
        """
        with self._base.get_client() as client:
            response = delete_model_adapter_sync(
                model_adapter_id=model_adapter_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_model_adapter(self, body: ModelAdapter) -> StoredModelAdapter:
        """Create a model adapter

        Args:
            body (ModelAdapter):
        """
        with self._base.get_client() as client:
            response = create_model_adapter_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_model_adapter(
        self, model_adapter_id: str, body: ModelAdapter
    ) -> StoredModelAdapter:
        """Update the model adapter

        Args:
            model_adapter_id (str):
            body (ModelAdapter):
        """
        with self._base.get_client() as client:
            response = update_model_adapter_sync(
                model_adapter_id=model_adapter_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncModelAdaptersResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def get_model_adapter(self, model_adapter_id: str) -> StoredModelAdapter:
        """Get the model adapter

        Args:
            model_adapter_id (str):
        """
        with self._base.get_client() as client:
            response = await get_model_adapter_asyncio(
                model_adapter_id=model_adapter_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_model_adapters(
        self, *, key: Union[Unset, str] = UNSET
    ) -> StoredModelAdapters:
        """Get all model adapters

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_model_adapters_asyncio(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_model_adapter(self, model_adapter_id: str) -> Success:
        """Delete the model adapter

        Args:
            model_adapter_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_model_adapter_asyncio(
                model_adapter_id=model_adapter_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_model_adapter(self, body: ModelAdapter) -> StoredModelAdapter:
        """Create a model adapter

        Args:
            body (ModelAdapter):
        """
        with self._base.get_client() as client:
            response = await create_model_adapter_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_model_adapter(
        self, model_adapter_id: str, body: ModelAdapter
    ) -> StoredModelAdapter:
        """Update the model adapter

        Args:
            model_adapter_id (str):
            body (ModelAdapter):
        """
        with self._base.get_client() as client:
            response = await update_model_adapter_asyncio(
                model_adapter_id=model_adapter_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
