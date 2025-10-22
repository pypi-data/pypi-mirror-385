from typing import Union

from latticeflow.go._generated.api.frameworks.create_framework import (
    asyncio as create_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.create_framework import (
    sync as create_framework_sync,
)
from latticeflow.go._generated.api.frameworks.delete_framework import (
    asyncio as delete_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.delete_framework import (
    sync as delete_framework_sync,
)
from latticeflow.go._generated.api.frameworks.export_framework import (
    asyncio as export_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.export_framework import (
    sync as export_framework_sync,
)
from latticeflow.go._generated.api.frameworks.get_framework import (
    asyncio as get_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.get_framework import (
    sync as get_framework_sync,
)
from latticeflow.go._generated.api.frameworks.get_frameworks import (
    asyncio as get_frameworks_asyncio,
)
from latticeflow.go._generated.api.frameworks.get_frameworks import (
    sync as get_frameworks_sync,
)
from latticeflow.go._generated.api.frameworks.import_framework import (
    asyncio as import_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.import_framework import (
    sync as import_framework_sync,
)
from latticeflow.go._generated.api.frameworks.link_framework import (
    asyncio as link_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.link_framework import (
    sync as link_framework_sync,
)
from latticeflow.go._generated.api.frameworks.unlink_framework import (
    asyncio as unlink_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.unlink_framework import (
    sync as unlink_framework_sync,
)
from latticeflow.go._generated.api.frameworks.update_framework import (
    asyncio as update_framework_asyncio,
)
from latticeflow.go._generated.api.frameworks.update_framework import (
    sync as update_framework_sync,
)
from latticeflow.go._generated.models.body import ImportFrameworkBody
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import Framework
from latticeflow.go._generated.models.model import FrameworkRiskLinks
from latticeflow.go._generated.models.model import Frameworks
from latticeflow.go._generated.models.model import StoredFramework
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import File
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.extensions.resources.frameworks import (
    AsyncFrameworksResource as AsyncBaseModule,
)
from latticeflow.go.extensions.resources.frameworks import (
    FrameworksResource as BaseModule,
)
from latticeflow.go.types import ApiError


class FrameworksResource(BaseModule):
    def create_framework(self, body: Framework) -> StoredFramework:
        """Create a framework

        Args:
            body (Framework):
        """
        with self._base.get_client() as client:
            response = create_framework_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def export_framework(self, framework_id: str) -> File:
        """Export a framework and all its risks/controls/requirements as a zip file.

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = export_framework_sync(framework_id=framework_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_framework(self, framework_id: str, body: Framework) -> StoredFramework:
        """Update a framework

        Args:
            framework_id (str):
            body (Framework):
        """
        with self._base.get_client() as client:
            response = update_framework_sync(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_framework(self, framework_id: str) -> StoredFramework:
        """Get a framework

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = get_framework_sync(framework_id=framework_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_frameworks(self, *, key: Union[Unset, str] = UNSET) -> Frameworks:
        """Get all frameworks

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_frameworks_sync(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def import_framework(self, body: ImportFrameworkBody) -> StoredFramework:
        """Uploads a zip file, containing a framework and all its risks/controls/requirements.

        Args:
            body (ImportFrameworkBody):
        """
        with self._base.get_client() as client:
            response = import_framework_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def unlink_framework(self, framework_id: str, body: FrameworkRiskLinks) -> Success:
        """Unlink entities from framework.

        Args:
            framework_id (str):
            body (FrameworkRiskLinks):
        """
        with self._base.get_client() as client:
            response = unlink_framework_sync(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def link_framework(self, framework_id: str, body: FrameworkRiskLinks) -> Success:
        """Link entities to framework.

        Args:
            framework_id (str):
            body (FrameworkRiskLinks):
        """
        with self._base.get_client() as client:
            response = link_framework_sync(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_framework(self, framework_id: str) -> Success:
        """Delete a framework

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = delete_framework_sync(framework_id=framework_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncFrameworksResource(AsyncBaseModule):
    async def create_framework(self, body: Framework) -> StoredFramework:
        """Create a framework

        Args:
            body (Framework):
        """
        with self._base.get_client() as client:
            response = await create_framework_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def export_framework(self, framework_id: str) -> File:
        """Export a framework and all its risks/controls/requirements as a zip file.

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = await export_framework_asyncio(
                framework_id=framework_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_framework(
        self, framework_id: str, body: Framework
    ) -> StoredFramework:
        """Update a framework

        Args:
            framework_id (str):
            body (Framework):
        """
        with self._base.get_client() as client:
            response = await update_framework_asyncio(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_framework(self, framework_id: str) -> StoredFramework:
        """Get a framework

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = await get_framework_asyncio(
                framework_id=framework_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_frameworks(self, *, key: Union[Unset, str] = UNSET) -> Frameworks:
        """Get all frameworks

        Args:
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_frameworks_asyncio(client=client, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def import_framework(self, body: ImportFrameworkBody) -> StoredFramework:
        """Uploads a zip file, containing a framework and all its risks/controls/requirements.

        Args:
            body (ImportFrameworkBody):
        """
        with self._base.get_client() as client:
            response = await import_framework_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def unlink_framework(
        self, framework_id: str, body: FrameworkRiskLinks
    ) -> Success:
        """Unlink entities from framework.

        Args:
            framework_id (str):
            body (FrameworkRiskLinks):
        """
        with self._base.get_client() as client:
            response = await unlink_framework_asyncio(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def link_framework(
        self, framework_id: str, body: FrameworkRiskLinks
    ) -> Success:
        """Link entities to framework.

        Args:
            framework_id (str):
            body (FrameworkRiskLinks):
        """
        with self._base.get_client() as client:
            response = await link_framework_asyncio(
                framework_id=framework_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_framework(self, framework_id: str) -> Success:
        """Delete a framework

        Args:
            framework_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_framework_asyncio(
                framework_id=framework_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
