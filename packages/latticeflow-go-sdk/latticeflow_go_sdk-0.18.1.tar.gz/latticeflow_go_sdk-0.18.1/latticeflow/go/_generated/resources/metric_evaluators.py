from typing import Union

from latticeflow.go._generated.api.metric_evaluators.create_metric_evaluator import (
    asyncio as create_metric_evaluator_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.create_metric_evaluator import (
    sync as create_metric_evaluator_sync,
)
from latticeflow.go._generated.api.metric_evaluators.delete_metric_evaluator import (
    asyncio as delete_metric_evaluator_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.delete_metric_evaluator import (
    sync as delete_metric_evaluator_sync,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluator import (
    asyncio as get_metric_evaluator_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluator import (
    sync as get_metric_evaluator_sync,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluator_keys import (
    asyncio as get_metric_evaluator_keys_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluator_keys import (
    sync as get_metric_evaluator_keys_sync,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluators import (
    asyncio as get_metric_evaluators_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.get_metric_evaluators import (
    sync as get_metric_evaluators_sync,
)
from latticeflow.go._generated.api.metric_evaluators.update_metric_evaluator import (
    asyncio as update_metric_evaluator_asyncio,
)
from latticeflow.go._generated.api.metric_evaluators.update_metric_evaluator import (
    sync as update_metric_evaluator_sync,
)
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import MetricEvaluator
from latticeflow.go._generated.models.model import MetricEvaluatorKeys
from latticeflow.go._generated.models.model import StoredMetricEvaluator
from latticeflow.go._generated.models.model import StoredMetricEvaluators
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.extensions.resources.metric_evaluators import (
    AsyncMetricEvaluatorsResource as AsyncBaseModule,
)
from latticeflow.go.extensions.resources.metric_evaluators import (
    MetricEvaluatorsResource as BaseModule,
)
from latticeflow.go.types import ApiError


class MetricEvaluatorsResource(BaseModule):
    def delete_metric_evaluator(
        self, metric_evaluator_id: str, *, delete_evaluations: bool
    ) -> Success:
        """Delete metric evaluator

        Args:
            metric_evaluator_id (str):
            delete_evaluations (bool):
        """
        with self._base.get_client() as client:
            response = delete_metric_evaluator_sync(
                metric_evaluator_id=metric_evaluator_id,
                client=client,
                delete_evaluations=delete_evaluations,
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_metric_evaluators(
        self, *, key: Union[Unset, str] = UNSET, metric_key: Union[Unset, str] = UNSET
    ) -> StoredMetricEvaluators:
        """Get all metric evaluators

        Args:
            key (Union[Unset, str]):
            metric_key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_metric_evaluators_sync(
                client=client, key=key, metric_key=metric_key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_metric_evaluator(self, body: MetricEvaluator) -> StoredMetricEvaluator:
        """Create a metric evaluator

        Args:
            body (MetricEvaluator):
        """
        with self._base.get_client() as client:
            response = create_metric_evaluator_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_metric_evaluator_keys(self) -> MetricEvaluatorKeys:
        """Get all metric evaluator keys currently defined in AI GO!."""
        with self._base.get_client() as client:
            response = get_metric_evaluator_keys_sync(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_metric_evaluator(
        self,
        metric_evaluator_id: str,
        body: MetricEvaluator,
        *,
        invalidate_evaluations: bool,
    ) -> StoredMetricEvaluator:
        """Update a metric evaluator

        Args:
            metric_evaluator_id (str):
            invalidate_evaluations (bool):
            body (MetricEvaluator):
        """
        with self._base.get_client() as client:
            response = update_metric_evaluator_sync(
                metric_evaluator_id=metric_evaluator_id,
                body=body,
                client=client,
                invalidate_evaluations=invalidate_evaluations,
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_metric_evaluator(self, metric_evaluator_id: str) -> StoredMetricEvaluator:
        """Get a metric evaluator

        Args:
            metric_evaluator_id (str):
        """
        with self._base.get_client() as client:
            response = get_metric_evaluator_sync(
                metric_evaluator_id=metric_evaluator_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncMetricEvaluatorsResource(AsyncBaseModule):
    async def delete_metric_evaluator(
        self, metric_evaluator_id: str, *, delete_evaluations: bool
    ) -> Success:
        """Delete metric evaluator

        Args:
            metric_evaluator_id (str):
            delete_evaluations (bool):
        """
        with self._base.get_client() as client:
            response = await delete_metric_evaluator_asyncio(
                metric_evaluator_id=metric_evaluator_id,
                client=client,
                delete_evaluations=delete_evaluations,
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_metric_evaluators(
        self, *, key: Union[Unset, str] = UNSET, metric_key: Union[Unset, str] = UNSET
    ) -> StoredMetricEvaluators:
        """Get all metric evaluators

        Args:
            key (Union[Unset, str]):
            metric_key (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_metric_evaluators_asyncio(
                client=client, key=key, metric_key=metric_key
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_metric_evaluator(
        self, body: MetricEvaluator
    ) -> StoredMetricEvaluator:
        """Create a metric evaluator

        Args:
            body (MetricEvaluator):
        """
        with self._base.get_client() as client:
            response = await create_metric_evaluator_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_metric_evaluator_keys(self) -> MetricEvaluatorKeys:
        """Get all metric evaluator keys currently defined in AI GO!."""
        with self._base.get_client() as client:
            response = await get_metric_evaluator_keys_asyncio(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_metric_evaluator(
        self,
        metric_evaluator_id: str,
        body: MetricEvaluator,
        *,
        invalidate_evaluations: bool,
    ) -> StoredMetricEvaluator:
        """Update a metric evaluator

        Args:
            metric_evaluator_id (str):
            invalidate_evaluations (bool):
            body (MetricEvaluator):
        """
        with self._base.get_client() as client:
            response = await update_metric_evaluator_asyncio(
                metric_evaluator_id=metric_evaluator_id,
                body=body,
                client=client,
                invalidate_evaluations=invalidate_evaluations,
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_metric_evaluator(
        self, metric_evaluator_id: str
    ) -> StoredMetricEvaluator:
        """Get a metric evaluator

        Args:
            metric_evaluator_id (str):
        """
        with self._base.get_client() as client:
            response = await get_metric_evaluator_asyncio(
                metric_evaluator_id=metric_evaluator_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
