

from latticeflow.go._generated.api.framework_templates.create_framework_from_template import (
    asyncio as create_framework_from_template_asyncio,
)
from latticeflow.go._generated.api.framework_templates.create_framework_from_template import (
    sync as create_framework_from_template_sync,
)
from latticeflow.go._generated.api.framework_templates.get_framework_templates import (
    asyncio as get_framework_templates_asyncio,
)
from latticeflow.go._generated.api.framework_templates.get_framework_templates import (
    sync as get_framework_templates_sync,
)
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import FrameworkTemplates
from latticeflow.go._generated.models.model import StoredFramework
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class FrameworkTemplatesResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def create_framework_from_template(self, template_key: str) -> StoredFramework:
        """Create a new framework from a template.

        Args:
            template_key (str):
        """
        with self._base.get_client() as client:
            response = create_framework_from_template_sync(
                template_key=template_key, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_framework_templates(self) -> FrameworkTemplates:
        """Get all framework templates."""
        with self._base.get_client() as client:
            response = get_framework_templates_sync(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncFrameworkTemplatesResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def create_framework_from_template(
        self, template_key: str
    ) -> StoredFramework:
        """Create a new framework from a template.

        Args:
            template_key (str):
        """
        with self._base.get_client() as client:
            response = await create_framework_from_template_asyncio(
                template_key=template_key, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_framework_templates(self) -> FrameworkTemplates:
        """Get all framework templates."""
        with self._base.get_client() as client:
            response = await get_framework_templates_asyncio(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response
