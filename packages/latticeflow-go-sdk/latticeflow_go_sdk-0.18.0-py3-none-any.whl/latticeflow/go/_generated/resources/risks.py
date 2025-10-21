from typing import Union

from latticeflow.go._generated.api.risks.create_risk import (
    asyncio as create_risk_asyncio,
)
from latticeflow.go._generated.api.risks.create_risk import sync as create_risk_sync
from latticeflow.go._generated.api.risks.delete_risk import (
    asyncio as delete_risk_asyncio,
)
from latticeflow.go._generated.api.risks.delete_risk import sync as delete_risk_sync
from latticeflow.go._generated.api.risks.get_risk import asyncio as get_risk_asyncio
from latticeflow.go._generated.api.risks.get_risk import sync as get_risk_sync
from latticeflow.go._generated.api.risks.get_risks import asyncio as get_risks_asyncio
from latticeflow.go._generated.api.risks.get_risks import sync as get_risks_sync
from latticeflow.go._generated.api.risks.link_risk import asyncio as link_risk_asyncio
from latticeflow.go._generated.api.risks.link_risk import sync as link_risk_sync
from latticeflow.go._generated.api.risks.unlink_risk import (
    asyncio as unlink_risk_asyncio,
)
from latticeflow.go._generated.api.risks.unlink_risk import sync as unlink_risk_sync
from latticeflow.go._generated.api.risks.update_risk import (
    asyncio as update_risk_asyncio,
)
from latticeflow.go._generated.api.risks.update_risk import sync as update_risk_sync
from latticeflow.go._generated.models.model import ControlRiskLinks
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import Risk
from latticeflow.go._generated.models.model import Risks
from latticeflow.go._generated.models.model import StoredRisk
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class RisksResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def delete_risk(self, risk_id: str) -> Success:
        """Delete a risk

        Args:
            risk_id (str):
        """
        with self._base.get_client() as client:
            response = delete_risk_sync(risk_id=risk_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_risk(self, body: Risk) -> StoredRisk:
        """Create a risk.

        Args:
            body (Risk):
        """
        with self._base.get_client() as client:
            response = create_risk_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_risk(self, risk_id: str, body: Risk) -> StoredRisk:
        """Update a risk

        Args:
            risk_id (str):
            body (Risk):
        """
        with self._base.get_client() as client:
            response = update_risk_sync(risk_id=risk_id, body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_risk(self, risk_id: str) -> StoredRisk:
        """Get a risk

        Args:
            risk_id (str):
        """
        with self._base.get_client() as client:
            response = get_risk_sync(risk_id=risk_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_risks(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Risks:
        """Get all risks

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_risks_sync(client=client, framework_id=framework_id, key=key)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def unlink_risk(self, risk_id: str, body: ControlRiskLinks) -> Success:
        """Unlink entities from risk.

        Args:
            risk_id (str):
            body (ControlRiskLinks):
        """
        with self._base.get_client() as client:
            response = unlink_risk_sync(risk_id=risk_id, body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def link_risk(self, risk_id: str, body: ControlRiskLinks) -> Success:
        """Link entities to risk.

        Args:
            risk_id (str):
            body (ControlRiskLinks):
        """
        with self._base.get_client() as client:
            response = link_risk_sync(risk_id=risk_id, body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncRisksResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def delete_risk(self, risk_id: str) -> Success:
        """Delete a risk

        Args:
            risk_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_risk_asyncio(risk_id=risk_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_risk(self, body: Risk) -> StoredRisk:
        """Create a risk.

        Args:
            body (Risk):
        """
        with self._base.get_client() as client:
            response = await create_risk_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_risk(self, risk_id: str, body: Risk) -> StoredRisk:
        """Update a risk

        Args:
            risk_id (str):
            body (Risk):
        """
        with self._base.get_client() as client:
            response = await update_risk_asyncio(
                risk_id=risk_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_risk(self, risk_id: str) -> StoredRisk:
        """Get a risk

        Args:
            risk_id (str):
        """
        with self._base.get_client() as client:
            response = await get_risk_asyncio(risk_id=risk_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_risks(
        self, *, framework_id: Union[Unset, str] = UNSET, key: Union[Unset, str] = UNSET
    ) -> Risks:
        """Get all risks

        Args:
            framework_id (Union[Unset, str]):
            key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_risks_asyncio(
                client=client, framework_id=framework_id, key=key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def unlink_risk(self, risk_id: str, body: ControlRiskLinks) -> Success:
        """Unlink entities from risk.

        Args:
            risk_id (str):
            body (ControlRiskLinks):
        """
        with self._base.get_client() as client:
            response = await unlink_risk_asyncio(
                risk_id=risk_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def link_risk(self, risk_id: str, body: ControlRiskLinks) -> Success:
        """Link entities to risk.

        Args:
            risk_id (str):
            body (ControlRiskLinks):
        """
        with self._base.get_client() as client:
            response = await link_risk_asyncio(
                risk_id=risk_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
