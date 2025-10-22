

from latticeflow.go._generated.api.evaluations.cancel_metric_evaluation import (
    asyncio as cancel_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.cancel_metric_evaluation import (
    sync as cancel_metric_evaluation_sync,
)
from latticeflow.go._generated.api.evaluations.create_metric_evaluation import (
    asyncio as create_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.create_metric_evaluation import (
    sync as create_metric_evaluation_sync,
)
from latticeflow.go._generated.api.evaluations.create_metric_evaluation_report import (
    asyncio as create_metric_evaluation_report_asyncio,
)
from latticeflow.go._generated.api.evaluations.create_metric_evaluation_report import (
    sync as create_metric_evaluation_report_sync,
)
from latticeflow.go._generated.api.evaluations.delete_metric_evaluation import (
    asyncio as delete_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.delete_metric_evaluation import (
    sync as delete_metric_evaluation_sync,
)
from latticeflow.go._generated.api.evaluations.download_metric_evaluation_evidence import (
    asyncio as download_metric_evaluation_evidence_asyncio,
)
from latticeflow.go._generated.api.evaluations.download_metric_evaluation_evidence import (
    sync as download_metric_evaluation_evidence_sync,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation import (
    asyncio as get_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation import (
    sync as get_metric_evaluation_sync,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation_evidence import (
    asyncio as get_metric_evaluation_evidence_asyncio,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation_evidence import (
    sync as get_metric_evaluation_evidence_sync,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation_report import (
    asyncio as get_metric_evaluation_report_asyncio,
)
from latticeflow.go._generated.api.evaluations.get_metric_evaluation_report import (
    sync as get_metric_evaluation_report_sync,
)
from latticeflow.go._generated.api.evaluations.invalidate_metric_evaluation_cache import (
    asyncio as invalidate_metric_evaluation_cache_asyncio,
)
from latticeflow.go._generated.api.evaluations.invalidate_metric_evaluation_cache import (
    sync as invalidate_metric_evaluation_cache_sync,
)
from latticeflow.go._generated.api.evaluations.run_metric_evaluation import (
    asyncio as run_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.run_metric_evaluation import (
    sync as run_metric_evaluation_sync,
)
from latticeflow.go._generated.api.evaluations.update_metric_evaluation import (
    asyncio as update_metric_evaluation_asyncio,
)
from latticeflow.go._generated.api.evaluations.update_metric_evaluation import (
    sync as update_metric_evaluation_sync,
)
from latticeflow.go._generated.models.body import CreateMetricEvaluationBody
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import MetricEvaluation
from latticeflow.go._generated.models.model import MetricEvaluationEvidence
from latticeflow.go._generated.models.model import Report
from latticeflow.go._generated.models.model import StoredMetricEvaluation
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.types import File
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class EvaluationsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def get_metric_evaluation_evidence(
        self, metric_evaluation_id: str
    ) -> MetricEvaluationEvidence:
        """Get the metric evaluation evidence by ID in JSON format.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = get_metric_evaluation_evidence_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def run_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Schedule a metric evaluation run

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = run_metric_evaluation_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def download_metric_evaluation_evidence(self, metric_evaluation_id: str) -> File:
        """Download a metric evaluation's evidence ZIP file containing one or many CSV and/or JSON files.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = download_metric_evaluation_evidence_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def cancel_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Cancel a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = cancel_metric_evaluation_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_metric_evaluation(
        self, metric_evaluation_id: str, body: MetricEvaluation
    ) -> StoredMetricEvaluation:
        """Update a metric evaluation.

        Args:
            metric_evaluation_id (str):
            body (MetricEvaluation):
        """
        with self._base.get_client() as client:
            response = update_metric_evaluation_sync(
                metric_evaluation_id=metric_evaluation_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Delete a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = delete_metric_evaluation_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_metric_evaluation(
        self, body: CreateMetricEvaluationBody
    ) -> StoredMetricEvaluation:
        """Create a metric evaluation

        Args:
            body (CreateMetricEvaluationBody):
        """
        with self._base.get_client() as client:
            response = create_metric_evaluation_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_metric_evaluation_report(self, metric_evaluation_id: str) -> Report:
        """Retrieves the report, associated to a metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = get_metric_evaluation_report_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def invalidate_metric_evaluation_cache(self, metric_evaluation_id: str) -> Report:
        """Invalidates the cache for a metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = invalidate_metric_evaluation_cache_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_metric_evaluation_report(self, metric_evaluation_id: str) -> Report:
        """Creates a new report for metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = create_metric_evaluation_report_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_metric_evaluation(
        self, metric_evaluation_id: str
    ) -> StoredMetricEvaluation:
        """Get a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = get_metric_evaluation_sync(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncEvaluationsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def get_metric_evaluation_evidence(
        self, metric_evaluation_id: str
    ) -> MetricEvaluationEvidence:
        """Get the metric evaluation evidence by ID in JSON format.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await get_metric_evaluation_evidence_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def run_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Schedule a metric evaluation run

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await run_metric_evaluation_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def download_metric_evaluation_evidence(
        self, metric_evaluation_id: str
    ) -> File:
        """Download a metric evaluation's evidence ZIP file containing one or many CSV and/or JSON files.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await download_metric_evaluation_evidence_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def cancel_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Cancel a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await cancel_metric_evaluation_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_metric_evaluation(
        self, metric_evaluation_id: str, body: MetricEvaluation
    ) -> StoredMetricEvaluation:
        """Update a metric evaluation.

        Args:
            metric_evaluation_id (str):
            body (MetricEvaluation):
        """
        with self._base.get_client() as client:
            response = await update_metric_evaluation_asyncio(
                metric_evaluation_id=metric_evaluation_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_metric_evaluation(self, metric_evaluation_id: str) -> Success:
        """Delete a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_metric_evaluation_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_metric_evaluation(
        self, body: CreateMetricEvaluationBody
    ) -> StoredMetricEvaluation:
        """Create a metric evaluation

        Args:
            body (CreateMetricEvaluationBody):
        """
        with self._base.get_client() as client:
            response = await create_metric_evaluation_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_metric_evaluation_report(self, metric_evaluation_id: str) -> Report:
        """Retrieves the report, associated to a metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await get_metric_evaluation_report_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def invalidate_metric_evaluation_cache(
        self, metric_evaluation_id: str
    ) -> Report:
        """Invalidates the cache for a metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await invalidate_metric_evaluation_cache_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_metric_evaluation_report(
        self, metric_evaluation_id: str
    ) -> Report:
        """Creates a new report for metric evaluation.

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await create_metric_evaluation_report_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_metric_evaluation(
        self, metric_evaluation_id: str
    ) -> StoredMetricEvaluation:
        """Get a metric evaluation

        Args:
            metric_evaluation_id (str):
        """
        with self._base.get_client() as client:
            response = await get_metric_evaluation_asyncio(
                metric_evaluation_id=metric_evaluation_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
