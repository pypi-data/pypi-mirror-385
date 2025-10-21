from __future__ import annotations

from typing import TYPE_CHECKING

from latticeflow.go.models import Error
from latticeflow.go.models import StoredFramework
from latticeflow.go.types import ApiError


if TYPE_CHECKING:
    from latticeflow.go import AsyncClient
    from latticeflow.go import Client


class FrameworksResource:
    def __init__(self, base_client: Client) -> None:
        self._base = base_client

    def get_framework_by_key(self, key: str) -> StoredFramework:
        """Get the Framework with the given name.

        Args:
            key: The key of the Framework.

        Raises:
            ApiError: If there is no Framework with the given key.
        """
        if frameworks_filtered_by_key := self._base.frameworks.get_frameworks(
            key=key
        ).frameworks:
            return frameworks_filtered_by_key[0]

        raise ApiError(Error(message=f"Framework with '{key}' not found."))


class AsyncFrameworksResource:
    def __init__(self, base_client: AsyncClient) -> None:
        self._base = base_client

    async def get_framework_by_key(self, key: str) -> StoredFramework:
        """Get the Framework with the given name.

        Args:
            key: The key of the Framework.

        Raises:
            ApiError: If there is no Framework with the given key.
        """
        if frameworks_filtered_by_key := (
            await self._base.frameworks.get_frameworks(key=key)
        ).frameworks:
            return frameworks_filtered_by_key[0]

        raise ApiError(Error(message=f"Framework with '{key}' not found."))
