from __future__ import annotations

from typing import TYPE_CHECKING

from latticeflow.go.models import Error
from latticeflow.go.models import StoredDataset
from latticeflow.go.types import ApiError


if TYPE_CHECKING:
    from latticeflow.go import AsyncClient
    from latticeflow.go import Client


class DatasetsResource:
    def __init__(self, base_client: Client) -> None:
        self._base = base_client

    def get_dataset_by_name(self, name: str) -> StoredDataset:
        """Get the Dataset with the given name.

        Args:
            name: The name of the Dataset.

        Raises:
            ApiError: If there are multiple or no Datasets with the name.
        """
        datasets_with_name = [
            dataset
            for dataset in self._base.datasets.get_datasets().datasets
            if dataset.display_name == name
        ]
        if len(datasets_with_name) == 0:
            raise ApiError(
                Error(message=f"Dataset with display name '{name}' not found.")
            )
        elif len(datasets_with_name) > 1:
            raise ApiError(
                Error(
                    message=f"There are multiple Datasets with display name '{name}'."
                )
            )
        else:
            return datasets_with_name[0]


class AsyncDatasetsResource:
    def __init__(self, base_client: AsyncClient) -> None:
        self._base = base_client

    async def get_dataset_by_name(self, name: str) -> StoredDataset:
        """Get the Dataset with the given name.

        Args:
            name: The name of the Dataset.

        Raises:
            ApiError: If there are multiple or no Datasets with the name.
        """
        datasets_with_name = [
            dataset
            for dataset in (await self._base.datasets.get_datasets()).datasets
            if dataset.display_name == name
        ]
        if len(datasets_with_name) == 0:
            raise ApiError(
                Error(message=f"Dataset with display name '{name}' not found.")
            )
        elif len(datasets_with_name) > 1:
            raise ApiError(
                Error(
                    message=f"There are multiple Datasets with display name '{name}'."
                )
            )
        else:
            return datasets_with_name[0]
