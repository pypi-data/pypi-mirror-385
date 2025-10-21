from typing import Union

from latticeflow.go._generated.api.controls.create_control import (
    asyncio as create_control_asyncio,
)
from latticeflow.go._generated.api.controls.create_control import (
    sync as create_control_sync,
)
from latticeflow.go._generated.api.controls.delete_control import (
    asyncio as delete_control_asyncio,
)
from latticeflow.go._generated.api.controls.delete_control import (
    sync as delete_control_sync,
)
from latticeflow.go._generated.api.controls.get_control import (
    asyncio as get_control_asyncio,
)
from latticeflow.go._generated.api.controls.get_control import sync as get_control_sync
from latticeflow.go._generated.api.controls.get_controls import (
    asyncio as get_controls_asyncio,
)
from latticeflow.go._generated.api.controls.get_controls import (
    sync as get_controls_sync,
)
from latticeflow.go._generated.api.controls.link_control import (
    asyncio as link_control_asyncio,
)
from latticeflow.go._generated.api.controls.link_control import (
    sync as link_control_sync,
)
from latticeflow.go._generated.api.controls.unlink_control import (
    asyncio as unlink_control_asyncio,
)
from latticeflow.go._generated.api.controls.unlink_control import (
    sync as unlink_control_sync,
)
from latticeflow.go._generated.api.controls.update_control import (
    asyncio as update_control_asyncio,
)
from latticeflow.go._generated.api.controls.update_control import (
    sync as update_control_sync,
)
from latticeflow.go._generated.models.model import Control
from latticeflow.go._generated.models.model import ControlRequirementLinks
from latticeflow.go._generated.models.model import Controls
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import StoredControl
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.extensions.resources.controls import (
    AsyncControlsResource as AsyncBaseModule,
)
from latticeflow.go.extensions.resources.controls import ControlsResource as BaseModule
from latticeflow.go.types import ApiError


class ControlsResource(BaseModule):
    def create_control(self, body: Control) -> StoredControl:
        """Create a control

        Args:
            body (Control):
        """
        with self._base.get_client() as client:
            response = create_control_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_controls(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Controls:
        """Get all controls

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_controls_sync(
                client=client, framework_id=framework_id, key=key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_control(self, control_id: str, body: Control) -> StoredControl:
        """Update a control

        Args:
            control_id (str):
            body (Control):
        """
        with self._base.get_client() as client:
            response = update_control_sync(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def link_control(self, control_id: str, body: ControlRequirementLinks) -> Success:
        """Link entities to control.

        Args:
            control_id (str):
            body (ControlRequirementLinks):
        """
        with self._base.get_client() as client:
            response = link_control_sync(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_control(self, control_id: str) -> StoredControl:
        """Get a control

        Args:
            control_id (str):
        """
        with self._base.get_client() as client:
            response = get_control_sync(control_id=control_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def unlink_control(self, control_id: str, body: ControlRequirementLinks) -> Success:
        """Unlink entities from control.

        Args:
            control_id (str):
            body (ControlRequirementLinks):
        """
        with self._base.get_client() as client:
            response = unlink_control_sync(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_control(self, control_id: str) -> Success:
        """Delete a control

        Args:
            control_id (str):
        """
        with self._base.get_client() as client:
            response = delete_control_sync(control_id=control_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncControlsResource(AsyncBaseModule):
    async def create_control(self, body: Control) -> StoredControl:
        """Create a control

        Args:
            body (Control):
        """
        with self._base.get_client() as client:
            response = await create_control_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_controls(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Controls:
        """Get all controls

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_controls_asyncio(
                client=client, framework_id=framework_id, key=key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_control(self, control_id: str, body: Control) -> StoredControl:
        """Update a control

        Args:
            control_id (str):
            body (Control):
        """
        with self._base.get_client() as client:
            response = await update_control_asyncio(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def link_control(
        self, control_id: str, body: ControlRequirementLinks
    ) -> Success:
        """Link entities to control.

        Args:
            control_id (str):
            body (ControlRequirementLinks):
        """
        with self._base.get_client() as client:
            response = await link_control_asyncio(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_control(self, control_id: str) -> StoredControl:
        """Get a control

        Args:
            control_id (str):
        """
        with self._base.get_client() as client:
            response = await get_control_asyncio(control_id=control_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def unlink_control(
        self, control_id: str, body: ControlRequirementLinks
    ) -> Success:
        """Unlink entities from control.

        Args:
            control_id (str):
            body (ControlRequirementLinks):
        """
        with self._base.get_client() as client:
            response = await unlink_control_asyncio(
                control_id=control_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_control(self, control_id: str) -> Success:
        """Delete a control

        Args:
            control_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_control_asyncio(
                control_id=control_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
