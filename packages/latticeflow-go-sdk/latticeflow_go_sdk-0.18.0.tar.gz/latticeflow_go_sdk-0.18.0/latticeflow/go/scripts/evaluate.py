from __future__ import annotations

import argparse
import json
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import cast
from typing import Iterable
from typing import Literal

import questionary
import yaml
from pydantic import ValidationError

from latticeflow.go.client import Client
from latticeflow.go.models import AISystem
from latticeflow.go.models import AssessmentStatus
from latticeflow.go.models import EvaluatedEntityType
from latticeflow.go.models import IntegrationModelProviderId
from latticeflow.go.models import LFBaseModel
from latticeflow.go.models import MetricEvaluation
from latticeflow.go.models import Modality
from latticeflow.go.models import Model
from latticeflow.go.models import ModelProviderConnectionConfig
from latticeflow.go.models import RequirementEvaluation
from latticeflow.go.models import Status2
from latticeflow.go.models import Task
from latticeflow.go.models import TechnicalRiskAssessment
from latticeflow.go.utils.connection import check_connection
from latticeflow.go.utils.scripts import get_arg_or_prompt


MetricEvaluationStrategy = Literal["debug", "fast", "full"]
GENERATED_CONFIGS_DIR = Path(__file__).parent / "generated_configs"


def get_available_evaluators() -> list[str]:
    if not GENERATED_CONFIGS_DIR.exists() or not GENERATED_CONFIGS_DIR.is_dir():
        return []
    return [d.stem for d in GENERATED_CONFIGS_DIR.iterdir() if d.name.endswith(".json")]


def get_configs(evaluator_key: str) -> dict[str, dict[str, Any]]:
    """
    Returns a dictionary mapping config names to their loaded JSON content
    from the generated_configs/<evaluator_key>.json file.
    """
    config_path = GENERATED_CONFIGS_DIR / (evaluator_key + ".json")
    configs: dict[str, Any] = {}
    if not config_path.exists():
        return configs

    try:
        with open(config_path, mode="r") as fp:
            configs = json.load(fp)
    except Exception as e:
        print(f"Failed to load configs {config_path}: {e}")
    return configs


class EvaluatorConfigs(LFBaseModel):
    configs: list[str]
    evaluation_strategy: MetricEvaluationStrategy | None = None


class EvaluationConfig(LFBaseModel):
    benchmarks: dict[str, EvaluatorConfigs]
    evaluation_strategy: MetricEvaluationStrategy | None = None

    @classmethod
    def from_configuration_file(cls, config_file_path: Path) -> EvaluationConfig:
        """Load an `EvaluationConfig` from a YAML configuration file.

        Args:
            config_file_path: Path to the YAML configuration file.

        Returns:
            An EvaluationConfig instance loaded from the file.

        SystemExit:
            Exits the program if the file is not found, cannot be loaded, or fails
            validation.
        """
        error_message = None
        evaluation_config = None

        if not config_file_path.exists():
            error_message = f"YAML config file '{config_file_path}' not found."
        else:
            try:
                with open(config_file_path, "r") as fp:
                    raw_config = yaml.safe_load(fp)
                evaluation_config = EvaluationConfig.model_validate(raw_config)
            except yaml.YAMLError as e:
                error_message = f"Error loading YAML file '{config_file_path}': {e}"
            except ValidationError as e:
                error_message = f"Error validating batch config with Pydantic:\n{e}"
            except Exception as e:
                error_message = f"Unexpected error: {e}"

        if error_message is not None:
            print(error_message)
            exit(1)

        assert evaluation_config is not None
        return evaluation_config

    def to_configurations(
        self, default_strategy: MetricEvaluationStrategy = "debug"
    ) -> Iterable[RunConfiguration]:
        """Generate `RunConfiguration` objects from the evaluation config.

        Args:
            default_strategy: The default metric evaluation strategy to use if not.
            specified.

        Yields:
            `RunConfiguration` objects for each combination of provider, model,
            evaluator, and config.
        """
        for evaluator_key, evaluator_configs in self.benchmarks.items():
            # Which models to use for evaluator
            evaluator_strategy = (
                evaluator_configs.evaluation_strategy
                or self.evaluation_strategy
                or default_strategy
            )
            for config_key in evaluator_configs.configs:
                yield RunConfiguration(
                    metric_evaluator_key=evaluator_key,
                    config_key=config_key,
                    evaluation_strategy=evaluator_strategy,
                )


class RunConfiguration(LFBaseModel):
    config_key: str
    metric_evaluator_key: str
    evaluation_strategy: MetricEvaluationStrategy = "debug"


class ModelConfiguration(LFBaseModel):
    model_key: str
    model_provider_key: str


class EvaluationClient(Client):
    def __init__(
        self, *, base_url: str, api_key: str, run_name: str, verify_ssl: bool = True
    ) -> None:
        super().__init__(base_url, api_key, verify_ssl)
        self.run_name = run_name

    def _get_or_create_model(
        self,
        *,
        model_provider_key: str,
        model_key: str,
        model_adapter_id: str,
        overwrite: bool = False,
    ) -> int:
        """Get or create a model for testing.

        If a model with the given model_key and model_provider_key already exists and
        overwrite is False, returns its ID. If overwrite is True, deletes all existing
        models with that key and provider, after deleting any associated AI systems,
        before creating a new one.
        """
        # Unique key for model consists of model_key and model_provider_key
        test_model_name = f"testing_{model_key}_{model_provider_key}"
        test_ai_system_name = f"testing_ai_system_{self.run_name}"

        models = self.models.get_models()

        filtered_models = [
            model
            for model in models.models
            if model.config.model_key == model_key
            and isinstance(model.config, ModelProviderConnectionConfig)
            and model.config.provider_id == model_provider_key
        ]
        if len(filtered_models) > 0:
            if not overwrite:
                return int(filtered_models[0].id)

            # AI system needs to be deleted first since model cannot be deleted if it is
            # associated with an AI System.
            try:
                ai_system = self.ai_systems.get_ai_system_by_name(test_ai_system_name)
                self.ai_systems.delete_ai_system(ai_system.id)
            except ValueError:
                pass

            for model in filtered_models:
                self.models.delete_model(model.id)

        body = Model(
            display_name=test_model_name,
            modality=Modality.TEXT,
            task=Task.CHAT_COMPLETION,
            adapter_id="latticeflow:together",
            config=ModelProviderConnectionConfig(
                provider_id=IntegrationModelProviderId(model_provider_key),
                model_key=model_key,
            ),
        )
        model = self.models.create_model(body=body)
        return int(model.id)

    def _get_or_create_ai_system(self, model_id: int, overwrite: bool = False) -> int:
        """Get or create an AI system for testing.

        If an AI system with the generated name already exists and overwrite is False,
        returns its ID. If overwrite is True, deletes all existing AI systems with that
        name before creating a new one.
        """
        ai_system_name = f"testing_ai_system_{self.run_name}"

        ai_systems = self.ai_systems.get_ai_systems()

        filtered_ai_systems = [
            ai_system
            for ai_system in ai_systems.ai_systems
            if ai_system.display_name == ai_system_name
        ]
        if len(filtered_ai_systems) > 0:
            if not overwrite:
                return int(filtered_ai_systems[0].id)

            for ai_system in filtered_ai_systems:
                self.ai_systems.delete_ai_system(ai_system.id)

        body = AISystem(
            display_name=ai_system_name,
            model_ids=[str(model_id)],
            dataset_ids=[],
            use_case="testing",
            description="AI System for testing",
        )
        ai_system = self.ai_systems.create_ai_system(body=body)
        return int(ai_system.id)

    def create_assessment(
        self,
        *,
        configs: list[RunConfiguration],
        model_id: int | None,
        model_config: ModelConfiguration | None,
        framework_key: str = "complai",
    ) -> int:
        """Create technical risk assessment.

        The following steps will be carried out:
        1) Model is created.
        2) AI System is created.
        3) Both requirements and metric evaluators are fetched such that requirement
            corresponding to the metric evaluation can be fetched.
        4) Metric evaluations and Requirement evaluations datastructures are populated.
        5) Technical risk assessment is created.
        """
        # Step 1) Create model if id not provided
        if model_id is None:
            assert model_config is not None
            model_id = self._get_or_create_model(
                model_provider_key=model_config.model_provider_key,
                model_key=model_config.model_key,
                model_adapter_id=model_config.model_provider_key,
            )

        # Step 2) Create AI System
        ai_system_id = self._get_or_create_ai_system(model_id)

        # Step 3) Fetch available requirements and metric evaluators
        frameworks = self.frameworks.get_frameworks(key=framework_key)
        assert len(frameworks.frameworks) == 1
        framework_id = frameworks.frameworks[0].id
        requirements = self.requirements.get_requirements(framework_id=framework_id)
        metric_evaluators = self.metric_evaluators.get_metric_evaluators()

        requirement_id_to_metric_evaluations: dict[str, list[MetricEvaluation]] = (
            defaultdict(list)
        )
        # Step 4) Populate metric and requirement evaluation datastructures
        for config in configs:
            metric_evaluator_id, metric_key = next(
                (metric_evaluator.id, metric_evaluator.metric_key)
                for metric_evaluator in metric_evaluators.metric_evaluators
                if metric_evaluator.key == config.metric_evaluator_key
            )
            requirement_id = next(
                requirement.id
                for requirement in requirements.requirements
                if requirement.metric_key == metric_key
            )

            metric_evaluator_configs = get_configs(config.metric_evaluator_key)
            metric_evaluator_config = metric_evaluator_configs[config.config_key].copy()
            metric_evaluator_config["evaluation_strategy"] = config.evaluation_strategy
            metric_evaluation = MetricEvaluation(
                evaluated_entity_type=EvaluatedEntityType.MODEL,
                evaluated_entity_id=str(model_id),
                display_name="Testing Evaluation",
                metric_evaluator_id=metric_evaluator_id,
                metric_evaluator_config=metric_evaluator_config,
            )
            requirement_id_to_metric_evaluations[requirement_id].append(
                metric_evaluation
            )

        requirement_evaluations: list[RequirementEvaluation] = []
        for (
            requirement_id,
            metric_evaluations,
        ) in requirement_id_to_metric_evaluations.items():
            requirement_evaluation = RequirementEvaluation(
                requirement_id=requirement_id,
                status=AssessmentStatus(reason="pending", status=Status2.PENDING),
                metric_evaluations=metric_evaluations,
            )
            requirement_evaluations.append(requirement_evaluation)

        # Step 5) Create technical risk assessment
        body = TechnicalRiskAssessment(
            assessment_type="technical_risk_assessment",
            display_name=str(uuid.uuid4()),
            ai_system_id=str(ai_system_id),
            framework_id=framework_id,
            requirement_evaluations=requirement_evaluations,
        )
        technical_risk_assessment = self.assessments.create_assessment(body=body)
        return int(technical_risk_assessment.id)


def question_user_model(
    evaluation_client: EvaluationClient,
    *,
    model_provider_key: str | None = None,
    model_key: str | None = None,
) -> ModelConfiguration:
    model_provider_keys = [
        provider.id.value
        for provider in evaluation_client.model_providers.get_model_providers().model_providers
    ]
    model_provider_key = get_arg_or_prompt(
        model_provider_key,
        "What model provider do you want to use?",
        choices=model_provider_keys,
        default="openai",
    )

    model_key = get_arg_or_prompt(model_key, "What model do you want to use?")

    return ModelConfiguration(
        model_key=model_key, model_provider_key=model_provider_key
    )


def question_user_run(
    evaluation_client: EvaluationClient,
    *,
    evaluator_key: str | None = None,
    config_key: str | None = None,
    evaluation_strategy: str | None = None,
) -> RunConfiguration:
    evaluator_keys = get_available_evaluators()
    metric_evaluator_key = get_arg_or_prompt(
        evaluator_key,
        "What evaluator do you want to use?",
        choices=evaluator_keys,
        default=evaluator_keys[0] if len(evaluator_keys) > 0 else None,
    )

    available_config_keys = list(get_configs(metric_evaluator_key).keys())
    assert len(available_config_keys) >= 1

    config_key = get_arg_or_prompt(
        config_key,
        "What config do you want to use?",
        choices=available_config_keys,
        default=available_config_keys[0],
        allow_all=True,
    )

    evaluation_strategy = get_arg_or_prompt(
        evaluation_strategy,
        "What evaluation strategy do you want to use?",
        choices=["debug", "fast", "full"],
        default="debug",
    )

    return RunConfiguration(
        metric_evaluator_key=metric_evaluator_key,
        config_key=config_key,
        evaluation_strategy=cast(MetricEvaluationStrategy, evaluation_strategy),
    )


def print_command_for_reference(
    host: str,
    api_key: str,
    run_configuration: RunConfiguration,
    model_configuration: ModelConfiguration,
) -> None:
    cmd = (
        f"\nTo run the script without user input, use the following command:"
        f"python3 evaluate.py --host '{host}' --api_key '{api_key}' "
        f"--model_provider_key '{model_configuration.model_provider_key}' "
        f"--model_key '{model_configuration.model_key}' "
        f"--evaluator_key '{run_configuration.metric_evaluator_key}' "
        f"--config_key '{run_configuration.config_key}'"
    )
    print(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="Run metric evaluation",
        description="A script for easily running metric evaluations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--run_name",
        type=str,
        help=(
            "Name of the run, used to identify the AI System. If not provided, a "
            "default ISO timestamp (e.g., 2024-06-13T12:34:56Z) will be used."
        ),
    )
    parser.add_argument("--host", type=str, help="URL of the LatticeFlow instance.")
    parser.add_argument(
        "--api_key",
        type=str,
        help="LatticeFlow API key (can be obtained from settings page).",
    )
    parser.add_argument(
        "--model_id",
        type=int,
        help=(
            "The id of the model to use. If provided, the `model_provider_key` and "
            "`model_key` are ignored."
        ),
    )
    parser.add_argument(
        "--model_provider_key", type=str, help="The key of the model provider."
    )
    parser.add_argument("--model_key", type=str, help="The model key.")
    parser.add_argument("--metric_key", type=str, help="The metric key.")
    parser.add_argument("--evaluator_key", type=str, help="The metric evaluator key.")
    parser.add_argument(
        "--config_key", type=str, help="The metric evaluator config key."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Continue execution even if host cannot be reached.",
    )
    parser.add_argument(
        "--evaluation_strategy",
        type=str,
        help="The evaluation strategy.",
        choices=["debug", "fast", "full"],
    )
    parser.add_argument(
        "--config_file", type=Path, help="YAML file for batch evaluation configuration."
    )
    args = parser.parse_args()

    # Before anything else, check if folder 'generated_configs' with json files exists
    confis_dir_exists = (
        GENERATED_CONFIGS_DIR.exists() and GENERATED_CONFIGS_DIR.is_dir()
    )
    config_dir_contains_json_files = any(
        f.name.endswith(".json") for f in GENERATED_CONFIGS_DIR.iterdir()
    )
    if not confis_dir_exists or not config_dir_contains_json_files:
        print(
            "Error: folder 'generated_configs' does not exist or does not contain "
            "any json files. Please run 'lf_generate_config_files' to generate the "
            "configs from within the scripts directory."
        )
        exit(1)

    if args.host is None:
        args.host = questionary.text("Choose a host:", default="localhost:5005").ask()
    if args.host is None:
        exit()

    if not args.host.startswith("http"):
        args.host = f"http://{args.host}"  # noqa

    if not check_connection(args.host):
        print(
            f"Warning: host '{args.host}' seems unreachable, please check your "
            f"connection. Use --force to ignore this error and continue."
        )
        if not args.force:
            exit(1)

    if args.api_key is None:
        args.api_key = questionary.text(
            f"Paste LatticeFlow api key '{args.host}/settings/api_keys':"
        ).ask()
    if args.api_key is None:
        exit()

    if args.run_name is None:
        # Generate ISO timestamp for better semantic meaning and chronological ordering
        args.run_name = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    args.evaluation_strategy = cast(MetricEvaluationStrategy, args.evaluation_strategy)

    evaluation_client = EvaluationClient(
        base_url=args.host,
        api_key=args.api_key,
        run_name=args.run_name,
        verify_ssl=False,
    )

    model_config = None
    if args.model_id is None:
        model_config = question_user_model(
            evaluation_client,
            model_provider_key=args.model_provider_key,
            model_key=args.model_key,
        )
    if args.config_file:
        batch_config = EvaluationConfig.from_configuration_file(args.config_file)
        run_configs = list(batch_config.to_configurations(args.evaluation_strategy))
    else:
        run_configs = [
            question_user_run(
                evaluation_client,
                evaluator_key=args.evaluator_key,
                config_key=args.config_key,
                evaluation_strategy=args.evaluation_strategy,
            )
        ]

    assessment_id = evaluation_client.create_assessment(
        configs=run_configs, model_id=args.model_id, model_config=model_config
    )
    evaluation_client.assessments.run_assessment(str(assessment_id))
    print(f"Results: {evaluation_client.base_url}/assessments/{assessment_id}/results")


if __name__ == "__main__":
    main()
