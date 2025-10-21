from typing import Union

from latticeflow.go._generated.api.requirements.create_requirement import (
    asyncio as create_requirement_asyncio,
)
from latticeflow.go._generated.api.requirements.create_requirement import (
    sync as create_requirement_sync,
)
from latticeflow.go._generated.api.requirements.delete_requirement import (
    asyncio as delete_requirement_asyncio,
)
from latticeflow.go._generated.api.requirements.delete_requirement import (
    sync as delete_requirement_sync,
)
from latticeflow.go._generated.api.requirements.get_requirement import (
    asyncio as get_requirement_asyncio,
)
from latticeflow.go._generated.api.requirements.get_requirement import (
    sync as get_requirement_sync,
)
from latticeflow.go._generated.api.requirements.get_requirements import (
    asyncio as get_requirements_asyncio,
)
from latticeflow.go._generated.api.requirements.get_requirements import (
    sync as get_requirements_sync,
)
from latticeflow.go._generated.api.requirements.update_requirement import (
    asyncio as update_requirement_asyncio,
)
from latticeflow.go._generated.api.requirements.update_requirement import (
    sync as update_requirement_sync,
)
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import Requirement
from latticeflow.go._generated.models.model import Requirements
from latticeflow.go._generated.models.model import StoredRequirement
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class RequirementsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def create_requirement(self, body: Requirement) -> StoredRequirement:
        """Create a requirement

        Args:
            body (Requirement):
        """
        with self._base.get_client() as client:
            response = create_requirement_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_requirements(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Requirements:
        """Get all requirements

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_requirements_sync(
                client=client, framework_id=framework_id, key=key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_requirement(self, requirement_id: str) -> Success:
        """Delete a requirement

        Args:
            requirement_id (str):
        """
        with self._base.get_client() as client:
            response = delete_requirement_sync(
                requirement_id=requirement_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_requirement(self, requirement_id: str) -> StoredRequirement:
        """Get a requirement

        Args:
            requirement_id (str):
        """
        with self._base.get_client() as client:
            response = get_requirement_sync(
                requirement_id=requirement_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_requirement(
        self, requirement_id: str, body: Requirement
    ) -> StoredRequirement:
        """Update a requirement

        Args:
            requirement_id (str):
            body (Requirement):
        """
        with self._base.get_client() as client:
            response = update_requirement_sync(
                requirement_id=requirement_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncRequirementsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def create_requirement(self, body: Requirement) -> StoredRequirement:
        """Create a requirement

        Args:
            body (Requirement):
        """
        with self._base.get_client() as client:
            response = await create_requirement_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_requirements(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Requirements:
        """Get all requirements

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_requirements_asyncio(
                client=client, framework_id=framework_id, key=key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_requirement(self, requirement_id: str) -> Success:
        """Delete a requirement

        Args:
            requirement_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_requirement_asyncio(
                requirement_id=requirement_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_requirement(self, requirement_id: str) -> StoredRequirement:
        """Get a requirement

        Args:
            requirement_id (str):
        """
        with self._base.get_client() as client:
            response = await get_requirement_asyncio(
                requirement_id=requirement_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_requirement(
        self, requirement_id: str, body: Requirement
    ) -> StoredRequirement:
        """Update a requirement

        Args:
            requirement_id (str):
            body (Requirement):
        """
        with self._base.get_client() as client:
            response = await update_requirement_asyncio(
                requirement_id=requirement_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
