from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from typing import BinaryIO
from typing import TYPE_CHECKING


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef, import-not-found]
from latticeflow.go.models import ChatCompletionModelInputBuilderConfig
from latticeflow.go.models import ConfigModelBenchmarkDefinition
from latticeflow.go.models import CreateDatasetBody
from latticeflow.go.models import CustomModelBenchmarkDefinitionKind
from latticeflow.go.models import Dataset
from latticeflow.go.models import Error
from latticeflow.go.models import EvaluatedEntityType
from latticeflow.go.models import GenericModelInputBuilderConfig
from latticeflow.go.models import MetricEvaluator
from latticeflow.go.models import MetricEvaluatorProvider
from latticeflow.go.models import Modality
from latticeflow.go.models import ModelInputBuilderKey
from latticeflow.go.models import ParameterSpec
from latticeflow.go.models import StoredDataset
from latticeflow.go.models import StoredMetricEvaluator
from latticeflow.go.models import Task
from latticeflow.go.types import ApiError
from latticeflow.go.types import File


if TYPE_CHECKING:
    from latticeflow.go import AsyncClient
    from latticeflow.go import Client


def _check_no_user_provider_evaluator_with_key_already_uploaded(
    key: str, metric_evaluators: list[StoredMetricEvaluator]
) -> None:
    if any(
        evaluator.key == key and evaluator.provider == MetricEvaluatorProvider.USER
        for evaluator in metric_evaluators
    ):
        raise ApiError(
            Error(
                message=f"An existing user-provided Metric Evaluator with key '{key}' already exists."
            )
        )


def _build_create_dataset_body(
    data: dict[str, Any], csv_file: BinaryIO
) -> CreateDatasetBody:
    info = data["info"]
    definition = data["definition"]
    return CreateDatasetBody(
        request=Dataset(
            display_name=definition["dataset"]["key"],
            description=f"Dataset for evaluator '{info['display_name']}'",
        ),
        file=File(
            payload=csv_file,
            file_name=Path(definition["dataset"]["path"]).name,
            mime_type="text/csv",
        ),
    )


def _convert_config_to_model_input_builder_config(
    model_input_builder_key: ModelInputBuilderKey, config: dict
) -> ChatCompletionModelInputBuilderConfig | GenericModelInputBuilderConfig:
    if model_input_builder_key == ModelInputBuilderKey.CHAT_COMPLETION:
        return ChatCompletionModelInputBuilderConfig.model_validate(config)
    else:
        return GenericModelInputBuilderConfig.model_validate(config)


def _build_metric_evaluator(
    *, data: dict[str, Any], dataset_id: str
) -> MetricEvaluator:
    info = data["info"]
    definition = data["definition"]
    model_input_builder_key = ModelInputBuilderKey(
        definition["model_input_builder_key"]
    )
    return MetricEvaluator(
        provider=MetricEvaluatorProvider.USER,
        key=info["key"],
        display_name=info["display_name"],
        description=info["description"],
        evaluated_entity_type=EvaluatedEntityType.MODEL,
        tags=info.get("tags", []),
        metric_key=info["metric_key"],
        parameter_spec=ParameterSpec(parameters=[]),
        long_description=info.get("long_description", ""),
        definition=ConfigModelBenchmarkDefinition(
            kind=CustomModelBenchmarkDefinitionKind.USER,
            tasks=[Task(task) for task in info["tasks"]],
            modalities=[Modality(modality) for modality in info["modalities"]],
            dataset_id=dataset_id,
            model_input_builder_key=model_input_builder_key,
            model_input_builder_config=_convert_config_to_model_input_builder_config(
                model_input_builder_key, definition["model_input_builder_config"]
            ),
            fast_subset_size=definition["fast_subset_size"],
            metric_id=definition["metric_id"],
            metric_config=definition["metric_config"],
        ),
    )


def get_dataset_with_key(
    *, key: str, datasets: list[StoredDataset]
) -> StoredDataset | None:
    datasets_with_key = [dataset for dataset in datasets if dataset.key == key]
    if len(datasets_with_key) == 0:
        return None
    elif len(datasets_with_key) == 1:
        return datasets_with_key[0]
    else:
        raise ApiError(
            Error(
                message=f"Multiple Datasets with the key '{key}' found. This should not happen."
            )
        )


class MetricEvaluatorsResource:
    def __init__(self, base_client: Client) -> None:
        self._base = base_client

    def create_metric_evaluator_from_toml(
        self, path: str | Path
    ) -> StoredMetricEvaluator:
        """Creates a Metric Evaluator from a TOML configuration file

        Args:
            path: The path of the TOML configuration file.

        Raises:
            Exception: If a user-provided Metric Evaluator with the given
                key already exists.
            ValueError: If multiple Datasets with a provided key already existed
                before the function was called (i.e., existing issue).

        """
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)
        evaluators = self._base.metric_evaluators.get_metric_evaluators()
        _check_no_user_provider_evaluator_with_key_already_uploaded(
            key=data["info"]["key"], metric_evaluators=evaluators.metric_evaluators
        )
        definition = data["definition"]
        dataset_key = definition["dataset_key"]
        dataset_path = Path(definition["dataset_path"])
        if not dataset_path.is_absolute():
            dataset_path = path.parent / dataset_path
        dataset = get_dataset_with_key(
            key=dataset_key, datasets=self._base.datasets.get_datasets().datasets
        )
        if dataset is None:
            with open(dataset_path, "rb") as csv_file:
                dataset = self._base.datasets.create_dataset(
                    body=_build_create_dataset_body(data=data, csv_file=csv_file)
                )
        else:
            logging.info(
                "Dataset with key '%s' already uploaded. Skipping Dataset upload.",
                dataset_key,
            )
        metric_evaluator = _build_metric_evaluator(data=data, dataset_id=dataset.id)
        return self._base.metric_evaluators.create_metric_evaluator(
            body=metric_evaluator
        )


class AsyncMetricEvaluatorsResource:
    def __init__(self, base_client: AsyncClient) -> None:
        self._base = base_client

    async def create_metric_evaluator_from_toml(
        self, path: str | Path
    ) -> StoredMetricEvaluator | None:
        """Creates a Metric Evaluator from a TOML configuration file

        Args:
            path: The path of the TOML configuration file.

        Raises:
            Exception: If a user-provided Metric Evaluator with the given
                key already exists.
            ValueError: If multiple Datasets with a provided key already existed
                before the function was called (i.e., existing issue).

        """
        path = Path(path)
        with open(path, "rb") as f:
            data = tomllib.load(f)
        evaluators = await self._base.metric_evaluators.get_metric_evaluators()
        _check_no_user_provider_evaluator_with_key_already_uploaded(
            key=data["info"]["key"], metric_evaluators=evaluators.metric_evaluators
        )
        dataset_definition = data["definition"]["dataset"]
        dataset_key = dataset_definition["key"]
        dataset_path = Path(dataset_definition["path"])
        dataset = get_dataset_with_key(
            key=dataset_key,
            datasets=(await self._base.datasets.get_datasets()).datasets,
        )
        if dataset is None:
            with open(dataset_path, "rb") as csv_file:
                dataset = await self._base.datasets.create_dataset(
                    body=_build_create_dataset_body(data=data, csv_file=csv_file)
                )
        else:
            logging.info(
                "Dataset with key '%s' already uploaded. Skipping Dataset upload.",
                dataset_key,
            )
            return None
        metric_evaluator = _build_metric_evaluator(data=data, dataset_id=dataset.id)
        return await self._base.metric_evaluators.create_metric_evaluator(
            body=metric_evaluator
        )
