from __future__ import annotations

from typing import TYPE_CHECKING

from latticeflow.go.models import Error
from latticeflow.go.models import StoredControl
from latticeflow.go.types import ApiError


if TYPE_CHECKING:
    from latticeflow.go import AsyncClient
    from latticeflow.go import Client


class ControlsResource:
    def __init__(self, base_client: Client) -> None:
        self._base = base_client

    def get_control_by_key(self, framework_id: str, key: str) -> StoredControl:
        """Get the Control with the given key.

        Args:
            framework_id: The Framework ID.
            key: The key of the Control.

        Raises:
            ApiError: If there is no Control with the given key in a
                Framework with the given ID.
        """
        if controls_filtered_by_key := self._base.controls.get_controls(
            framework_id=framework_id, key=key
        ).controls:
            return controls_filtered_by_key[0]

        raise ApiError(
            Error(
                message=f"Control with key '{key}' not found in Framework '{framework_id}'."
            )
        )


class AsyncControlsResource:
    def __init__(self, base_client: AsyncClient) -> None:
        self._base = base_client

    async def get_control_by_key(self, framework_id: str, key: str) -> StoredControl:
        """Get the Control with the given key.

        Args:
            framework_id: The Framework ID.
            key: The key of the Control.

        Raises:
            ApiError: If there is no Control with the given key in a
                Framework with the given ID.
        """
        if controls_filtered_by_key := (
            await self._base.controls.get_controls(framework_id=framework_id, key=key)
        ).controls:
            return controls_filtered_by_key[0]

        raise ApiError(
            Error(
                message=f"Control with key '{key}' not found in Framework '{framework_id}'."
            )
        )
