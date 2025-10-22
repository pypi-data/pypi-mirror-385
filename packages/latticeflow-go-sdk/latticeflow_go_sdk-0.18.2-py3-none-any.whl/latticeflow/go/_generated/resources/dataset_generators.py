

from latticeflow.go._generated.api.dataset_generators.generate_dataset import (
    asyncio as generate_dataset_asyncio,
)
from latticeflow.go._generated.api.dataset_generators.generate_dataset import (
    sync as generate_dataset_sync,
)
from latticeflow.go._generated.api.dataset_generators.get_dataset_generator import (
    asyncio as get_dataset_generator_asyncio,
)
from latticeflow.go._generated.api.dataset_generators.get_dataset_generator import (
    sync as get_dataset_generator_sync,
)
from latticeflow.go._generated.api.dataset_generators.get_dataset_generators import (
    asyncio as get_dataset_generators_asyncio,
)
from latticeflow.go._generated.api.dataset_generators.get_dataset_generators import (
    sync as get_dataset_generators_sync,
)
from latticeflow.go._generated.api.dataset_generators.preview_dataset_generation import (
    asyncio as preview_dataset_generation_asyncio,
)
from latticeflow.go._generated.api.dataset_generators.preview_dataset_generation import (
    sync as preview_dataset_generation_sync,
)
from latticeflow.go._generated.models.model import DatasetData
from latticeflow.go._generated.models.model import DatasetGenerationRequest
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import GeneratedDataset
from latticeflow.go._generated.models.model import StoredDataset
from latticeflow.go._generated.models.model import StoredDatasetGenerator
from latticeflow.go._generated.models.model import StoredDatasetGenerators
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class DatasetGeneratorsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def preview_dataset_generation(
        self, dataset_generator_id: str, body: DatasetGenerationRequest
    ) -> DatasetData:
        """Preview dataset generation

         Preview dataset generation without creating a new dataset.

        Args:
            dataset_generator_id (str):
            body (DatasetGenerationRequest):
        """
        with self._base.get_client() as client:
            response = preview_dataset_generation_sync(
                dataset_generator_id=dataset_generator_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_dataset_generators(self) -> StoredDatasetGenerators:
        """Get all dataset generators

        Get all available dataset generators.
        """
        with self._base.get_client() as client:
            response = get_dataset_generators_sync(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def generate_dataset(
        self, dataset_generator_id: str, body: GeneratedDataset
    ) -> StoredDataset:
        """Generate a dataset

         Generate a dataset using a dataset generator.

        Args:
            dataset_generator_id (str):
            body (GeneratedDataset):
        """
        with self._base.get_client() as client:
            response = generate_dataset_sync(
                dataset_generator_id=dataset_generator_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_dataset_generator(
        self, dataset_generator_id: str
    ) -> StoredDatasetGenerator:
        """Get a dataset generator

         Get information about a dataset generator.

        Args:
            dataset_generator_id (str):
        """
        with self._base.get_client() as client:
            response = get_dataset_generator_sync(
                dataset_generator_id=dataset_generator_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncDatasetGeneratorsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def preview_dataset_generation(
        self, dataset_generator_id: str, body: DatasetGenerationRequest
    ) -> DatasetData:
        """Preview dataset generation

         Preview dataset generation without creating a new dataset.

        Args:
            dataset_generator_id (str):
            body (DatasetGenerationRequest):
        """
        with self._base.get_client() as client:
            response = await preview_dataset_generation_asyncio(
                dataset_generator_id=dataset_generator_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_dataset_generators(self) -> StoredDatasetGenerators:
        """Get all dataset generators

        Get all available dataset generators.
        """
        with self._base.get_client() as client:
            response = await get_dataset_generators_asyncio(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def generate_dataset(
        self, dataset_generator_id: str, body: GeneratedDataset
    ) -> StoredDataset:
        """Generate a dataset

         Generate a dataset using a dataset generator.

        Args:
            dataset_generator_id (str):
            body (GeneratedDataset):
        """
        with self._base.get_client() as client:
            response = await generate_dataset_asyncio(
                dataset_generator_id=dataset_generator_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_dataset_generator(
        self, dataset_generator_id: str
    ) -> StoredDatasetGenerator:
        """Get a dataset generator

         Get information about a dataset generator.

        Args:
            dataset_generator_id (str):
        """
        with self._base.get_client() as client:
            response = await get_dataset_generator_asyncio(
                dataset_generator_id=dataset_generator_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
