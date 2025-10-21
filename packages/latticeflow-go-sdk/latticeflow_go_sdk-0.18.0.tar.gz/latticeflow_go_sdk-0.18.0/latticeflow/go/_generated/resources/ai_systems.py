from typing import Union

from latticeflow.go._generated.api.ai_systems.create_ai_system import (
    asyncio as create_ai_system_asyncio,
)
from latticeflow.go._generated.api.ai_systems.create_ai_system import (
    sync as create_ai_system_sync,
)
from latticeflow.go._generated.api.ai_systems.delete_ai_system import (
    asyncio as delete_ai_system_asyncio,
)
from latticeflow.go._generated.api.ai_systems.delete_ai_system import (
    sync as delete_ai_system_sync,
)
from latticeflow.go._generated.api.ai_systems.delete_ai_system_artifact import (
    asyncio as delete_ai_system_artifact_asyncio,
)
from latticeflow.go._generated.api.ai_systems.delete_ai_system_artifact import (
    sync as delete_ai_system_artifact_sync,
)
from latticeflow.go._generated.api.ai_systems.get_ai_system import (
    asyncio as get_ai_system_asyncio,
)
from latticeflow.go._generated.api.ai_systems.get_ai_system import (
    sync as get_ai_system_sync,
)
from latticeflow.go._generated.api.ai_systems.get_ai_system_artifact import (
    asyncio as get_ai_system_artifact_asyncio,
)
from latticeflow.go._generated.api.ai_systems.get_ai_system_artifact import (
    sync as get_ai_system_artifact_sync,
)
from latticeflow.go._generated.api.ai_systems.get_ai_systems import (
    asyncio as get_ai_systems_asyncio,
)
from latticeflow.go._generated.api.ai_systems.get_ai_systems import (
    sync as get_ai_systems_sync,
)
from latticeflow.go._generated.api.ai_systems.update_ai_system import (
    asyncio as update_ai_system_asyncio,
)
from latticeflow.go._generated.api.ai_systems.update_ai_system import (
    sync as update_ai_system_sync,
)
from latticeflow.go._generated.api.ai_systems.upload_ai_system_artifact import (
    asyncio as upload_ai_system_artifact_asyncio,
)
from latticeflow.go._generated.api.ai_systems.upload_ai_system_artifact import (
    sync as upload_ai_system_artifact_sync,
)
from latticeflow.go._generated.models.body import UploadAISystemArtifactBody
from latticeflow.go._generated.models.model import AISystem
from latticeflow.go._generated.models.model import AISystems
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import StoredAISystem
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import File
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.extensions.resources.ai_systems import (
    AiSystemsResource as BaseModule,
)
from latticeflow.go.extensions.resources.ai_systems import (
    AsyncAiSystemsResource as AsyncBaseModule,
)
from latticeflow.go.types import ApiError


class AiSystemsResource(BaseModule):
    def get_ai_system_artifact(self, ai_system_id: str, artifact_id: str) -> File:
        """Gets an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            artifact_id (str):
        """
        with self._base.get_client() as client:
            response = get_ai_system_artifact_sync(
                ai_system_id=ai_system_id, artifact_id=artifact_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_ai_system(self, ai_system_id: str, body: AISystem) -> StoredAISystem:
        """Update an AI System

        Args:
            ai_system_id (str):
            body (AISystem): An AI System defines a collection of datasets and models that solve a
                target use case.
        """
        with self._base.get_client() as client:
            response = update_ai_system_sync(
                ai_system_id=ai_system_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_ai_system(self, ai_system_id: str) -> StoredAISystem:
        """Get an AI System

        Args:
            ai_system_id (str):
        """
        with self._base.get_client() as client:
            response = get_ai_system_sync(ai_system_id=ai_system_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_ai_system(self, body: AISystem) -> StoredAISystem:
        """Create an AI System

        Args:
            body (AISystem): An AI System defines a collection of datasets and models that solve a
                target use case.
        """
        with self._base.get_client() as client:
            response = create_ai_system_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_ai_system_artifact(self, ai_system_id: str, artifact_id: str) -> Success:
        """Deletes an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            artifact_id (str):
        """
        with self._base.get_client() as client:
            response = delete_ai_system_artifact_sync(
                ai_system_id=ai_system_id, artifact_id=artifact_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_ai_system(self, ai_system_id: str) -> Success:
        """Delete an AI system

        Args:
            ai_system_id (str):
        """
        with self._base.get_client() as client:
            response = delete_ai_system_sync(ai_system_id=ai_system_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def upload_ai_system_artifact(
        self, ai_system_id: str, body: UploadAISystemArtifactBody
    ) -> Success:
        """Uploads an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            body (UploadAISystemArtifactBody):
        """
        with self._base.get_client() as client:
            response = upload_ai_system_artifact_sync(
                ai_system_id=ai_system_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_ai_systems(self, *, key: Union[Unset, str] = UNSET) -> AISystems:
        """Get all AI Systems

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_ai_systems_sync(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncAiSystemsResource(AsyncBaseModule):
    async def get_ai_system_artifact(self, ai_system_id: str, artifact_id: str) -> File:
        """Gets an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            artifact_id (str):
        """
        with self._base.get_client() as client:
            response = await get_ai_system_artifact_asyncio(
                ai_system_id=ai_system_id, artifact_id=artifact_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_ai_system(
        self, ai_system_id: str, body: AISystem
    ) -> StoredAISystem:
        """Update an AI System

        Args:
            ai_system_id (str):
            body (AISystem): An AI System defines a collection of datasets and models that solve a
                target use case.
        """
        with self._base.get_client() as client:
            response = await update_ai_system_asyncio(
                ai_system_id=ai_system_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_ai_system(self, ai_system_id: str) -> StoredAISystem:
        """Get an AI System

        Args:
            ai_system_id (str):
        """
        with self._base.get_client() as client:
            response = await get_ai_system_asyncio(
                ai_system_id=ai_system_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_ai_system(self, body: AISystem) -> StoredAISystem:
        """Create an AI System

        Args:
            body (AISystem): An AI System defines a collection of datasets and models that solve a
                target use case.
        """
        with self._base.get_client() as client:
            response = await create_ai_system_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_ai_system_artifact(
        self, ai_system_id: str, artifact_id: str
    ) -> Success:
        """Deletes an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            artifact_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_ai_system_artifact_asyncio(
                ai_system_id=ai_system_id, artifact_id=artifact_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_ai_system(self, ai_system_id: str) -> Success:
        """Delete an AI system

        Args:
            ai_system_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_ai_system_asyncio(
                ai_system_id=ai_system_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def upload_ai_system_artifact(
        self, ai_system_id: str, body: UploadAISystemArtifactBody
    ) -> Success:
        """Uploads an artifact, associated with an AI system.

        Args:
            ai_system_id (str):
            body (UploadAISystemArtifactBody):
        """
        with self._base.get_client() as client:
            response = await upload_ai_system_artifact_asyncio(
                ai_system_id=ai_system_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_ai_systems(self, *, key: Union[Unset, str] = UNSET) -> AISystems:
        """Get all AI Systems

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_ai_systems_asyncio(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response
