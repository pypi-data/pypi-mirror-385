from __future__ import annotations

from typing import TYPE_CHECKING

from latticeflow.go.models import Error
from latticeflow.go.models import StoredAISystem
from latticeflow.go.types import ApiError


if TYPE_CHECKING:
    from latticeflow.go import AsyncClient
    from latticeflow.go import Client


class AiSystemsResource:
    def __init__(self, base_client: Client) -> None:
        self._base = base_client

    def get_ai_system_by_name(self, name: str) -> StoredAISystem:
        """Get the first AI System with the given name.

        Args:
            name: The name of the AI System.

        Raises:
            ApiError: If there is no AI System with the given name.
        """
        for ai_system in self._base.ai_systems.get_ai_systems().ai_systems:
            if ai_system.display_name == name:
                return ai_system
        raise ApiError(Error(message=f"AI System with name '{name}' not found."))


class AsyncAiSystemsResource:
    def __init__(self, base_client: AsyncClient) -> None:
        self._base = base_client

    async def get_ai_system_by_name(self, name: str) -> StoredAISystem:
        """Get the first AI System with the given name.

        Args:
            name: The name of the AI System.

        Raises:
            ApiError: If there is no AI System with the given name.
        """
        for ai_system in (await self._base.ai_systems.get_ai_systems()).ai_systems:
            if ai_system.display_name == name:
                return ai_system
        raise ApiError(Error(message=f"AI System with name '{name}' not found."))
