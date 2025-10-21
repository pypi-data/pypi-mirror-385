from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess  # nosec: B404
import time
from pathlib import Path

import requests
import yaml
from pydantic import SecretStr
from pydantic import TypeAdapter
from pydantic import ValidationError

from latticeflow.go.models import AISystem
from latticeflow.go.models import AISystems
from latticeflow.go.models import AssessmentStatus
from latticeflow.go.models import Control
from latticeflow.go.models import Controls
from latticeflow.go.models import CredentialType
from latticeflow.go.models import Dataset
from latticeflow.go.models import EvaluatedEntityType
from latticeflow.go.models import Framework
from latticeflow.go.models import Frameworks
from latticeflow.go.models import InitialSetupRequest
from latticeflow.go.models import Integration
from latticeflow.go.models import MetricEvaluation
from latticeflow.go.models import MetricEvaluator
from latticeflow.go.models import Model
from latticeflow.go.models import ModelAdapter
from latticeflow.go.models import OpenAIIntegration
from latticeflow.go.models import PasswordUserCredential
from latticeflow.go.models import Requirement
from latticeflow.go.models import RequirementEvaluation
from latticeflow.go.models import Requirements
from latticeflow.go.models import Risk
from latticeflow.go.models import Risks
from latticeflow.go.models import State
from latticeflow.go.models import StoredAISystem
from latticeflow.go.models import StoredAssessments
from latticeflow.go.models import StoredDatasets
from latticeflow.go.models import StoredFramework
from latticeflow.go.models import StoredMetricEvaluators
from latticeflow.go.models import StoredModelAdapters
from latticeflow.go.models import StoredModels
from latticeflow.go.models import TechnicalRiskAssessment


def complete_initial_setup(host: str) -> SecretStr:
    with requests.Session() as session:
        response = session.post(
            f"{host}/api/initial-setup",
            json=InitialSetupRequest(
                name="admin",
                email="admin@latticeflow.ai",
                credentials=PasswordUserCredential(
                    credential_type=CredentialType.password,
                    value=SecretStr(
                        os.environ.get("LF_AIGO_PASS", "Uplifted8-Hydrated-Tribesman")
                    ),
                ),
            ).model_dump(mode="json"),
        )
        if response.status_code == 400 and "already complete" in response.text:
            print("Initial setup already complete. You might need to pass '--api-key'.")
        response.raise_for_status()
        response = session.get(f"{host}/api/state")
        response.raise_for_status()
        state = State.model_validate(response.json())
        if state.api_key is None:
            raise Exception("State did not contain the API key!")
        return state.api_key


# TODO: this is copied from docker.py. Should be unified.
def get_command_output(*args: str) -> str:
    return subprocess.check_output(  # nosec: B603
        list(args), stderr=subprocess.DEVNULL, universal_newlines=True
    ).strip()


# TODO: this is copied from docker.py. Should be unified.
def get_core_path() -> Path:
    remote_origin_url = get_command_output(
        "git", "config", "--get", "remote.origin.url"
    )
    # Origin can be `.git` if checked out through ssh or without `.git` if through HTTP.
    if not remote_origin_url.endswith(
        "latticeflow-one/latticeflow-core.git"
    ) and not remote_origin_url.endswith("latticeflow-one/latticeflow-core"):
        raise RuntimeError("The script must be run from within the core repository.")

    core_repo_path = get_command_output("git", "rev-parse", "--show-toplevel")
    os.putenv("CORE_REPO_PATH", core_repo_path)
    return Path(core_repo_path)


def get_headers(api_key: str) -> dict[str, str]:
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "X-LatticeFlow-API-Key": api_key,
    }


def wait_for_host_up(host: str, api_key: str, timeout: int = 60) -> bool:
    headers = get_headers(api_key)
    start = time.time()
    while True:
        try:
            response = requests.get(
                f"{host}/api/ping", headers=headers, timeout=timeout
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            if time.time() - start > timeout:
                return False
        time.sleep(0.1)


def create_requirements(
    *, host: str, api_key: str, requirements_dir: Path
) -> dict[str, str]:
    if not requirements_dir.exists():
        print(f"Requirements directory '{requirements_dir}' does not exist.")
        return {}

    headers = get_headers(api_key)
    requirement_key_to_id = get_requirement_key_to_id(host=host, api_key=api_key)
    for file_path in sorted(requirements_dir.glob("*.y*ml")):
        with open(file_path, "r") as file:
            requirement_data = yaml.safe_load(file)

        try:
            requirement = Requirement.model_validate(requirement_data)
        except ValidationError as error:
            print(
                f"Validation error in requirement definition at '{file_path}': {error}."
            )
            continue

        if requirement.key in requirement_key_to_id:
            response = requests.put(
                f"{host}/api/requirements/{requirement_key_to_id[requirement.key]}",
                json=requirement.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        else:
            response = requests.post(
                f"{host}/api/requirements",
                json=requirement.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        if response.status_code not in [200, 201]:
            print(
                f"Failed to create/update requirement '{requirement.key}:\n"
                f"{response.text}"
            )
        else:
            print(f"Successfully created requirement '{requirement.key}'.")

    return get_requirement_key_to_id(host=host, api_key=api_key)


def get_requirement_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/requirements", headers=headers, timeout=30)
    response.raise_for_status()
    requirements = Requirements.model_validate(response.json())
    return {
        requirement.key: requirement.id
        for requirement in requirements.requirements
        if requirement.key is not None
    }


def create_controls(*, host: str, api_key: str, controls_dir: Path) -> dict[str, str]:
    if not controls_dir.exists():
        print(f"Controls directory '{controls_dir}' does not exist.")
        return {}

    headers = get_headers(api_key)
    control_key_to_id = get_control_key_to_id(host=host, api_key=api_key)
    for file_path in controls_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            control_data = yaml.safe_load(file)
        try:
            control = Control.model_validate(control_data)
        except ValidationError as error:
            print(f"Validation error in control definition at '{file_path}': {error}.")
            continue

        if control.key in control_key_to_id:
            response = requests.put(
                f"{host}/api/controls/{control_key_to_id[control.key]}",
                json=control.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        else:
            response = requests.post(
                f"{host}/api/controls",
                json=control.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        if response.status_code not in [200, 201]:
            print(f"Failed to create/update control '{control.key}:\n{response.text}")
        else:
            print(f"Successfully created control '{control.key}'.")

    return get_control_key_to_id(host=host, api_key=api_key)


def get_control_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/controls", headers=headers, timeout=30)
    response.raise_for_status()
    controls = Controls.model_validate(response.json())
    return {
        control.key: control.id
        for control in controls.controls
        if control.key is not None
    }


def create_risks(*, host: str, api_key: str, risks_dir: Path) -> dict[str, str]:
    if not risks_dir.exists():
        print(f"Risks directory '{risks_dir}' does not exist.")
        return {}

    headers = get_headers(api_key)
    risk_key_to_id = get_risk_key_to_id(host=host, api_key=api_key)
    for file_path in sorted(risks_dir.glob("*.y*ml")):
        with open(file_path, "r") as file:
            risk_data = yaml.safe_load(file)
        try:
            risk = Risk.model_validate(risk_data)
        except ValidationError as error:
            print(f"Validation error in risk definition at '{file_path}': {error}.")
            continue

        if risk.key in risk_key_to_id:
            response = requests.put(
                f"{host}/api/risks/{risk_key_to_id[risk.key]}",
                json=risk.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        else:
            response = requests.post(
                f"{host}/api/risks",
                json=risk.model_dump(mode="json"),
                headers=headers,
                timeout=30,
            )
        if response.status_code not in [200, 201]:
            print(f"Failed to create/update risk '{risk.key}:\n{response.text}")
        else:
            print(f"Successfully created risk '{risk.key}'.")

    return get_risk_key_to_id(host=host, api_key=api_key)


def get_risk_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/risks", headers=headers, timeout=30)
    response.raise_for_status()
    risks = Risks.model_validate(response.json())
    return {risk.key: risk.id for risk in risks.risks if risk.key is not None}


def create_framework(
    *,
    host: str,
    api_key: str,
    framework_path: Path,
    risk_key_to_risk_id: dict[str, str],
    control_key_to_control_id: dict[str, str],
    requirement_key_to_requirement_id: dict[str, str],
) -> str | None:
    if not framework_path.exists():
        print(f"Framework definition file '{framework_path}' does not exist.")
        return None

    with open(framework_path, "r") as file:
        framework_data = yaml.safe_load(file)
    try:
        framework = Framework.model_validate(framework_data)
    except ValidationError as error:
        print(
            f"Validation error in framework definition at '{framework_path}': {error}."
        )
        return None

    headers = get_headers(api_key)

    framework_key_to_id = get_framework_key_to_id(host=host, api_key=api_key)
    if framework.key not in framework_key_to_id:
        response = requests.post(
            f"{host}/api/frameworks",
            json=framework.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
    else:
        response = requests.put(
            f"{host}/api/frameworks/{framework_key_to_id[framework.key]}",
            json=framework.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
    if response.status_code not in [200, 201]:
        print(f"Failed to create/update framework '{framework.key}:\n{response.text}")
        return None

    print(f"Successfully created framework '{framework.key}'.")
    stored_framework = TypeAdapter(StoredFramework).validate_json(response.text)

    framework_id = stored_framework.id
    risk_ids: list[str] = []
    for risk_key, control_keys in framework_data.get("risk_control_links", {}).items():
        if risk_key not in risk_key_to_risk_id:
            print(
                f"Unknown risk key '{risk_key}' linked in framework "
                f"'{stored_framework.key}'."
            )
            continue
        risk_id = risk_key_to_risk_id[risk_key]
        risk_ids.append(risk_id)

        control_ids: list[str] = []
        for control_key in control_keys:
            if control_key not in control_key_to_control_id:
                print(
                    f"Unknown control key '{control_key}' linked in framework "
                    f"'{stored_framework.key}'."
                )
                continue
            control_ids.append(control_key_to_control_id[control_key])

        requests.post(
            f"{host}/api/risks/{risk_id}/link",
            json={"framework_id": framework_id, "control_ids": control_ids},
            headers=headers,
            timeout=30,
        )

    for control_key, requirement_keys in framework_data.get(
        "control_requirement_links", {}
    ).items():
        if control_key not in control_key_to_control_id:
            print(
                f"Unknown control key '{control_key}' linked in framework "
                f"'{stored_framework.key}'."
            )
            continue
        control_id = control_key_to_control_id[control_key]

        requirement_ids: list[str] = []
        for requirement_key in requirement_keys:
            if requirement_key not in requirement_key_to_requirement_id:
                print(
                    f"Unknown requirement key '{requirement_key}' linked in framework "
                    f"'{stored_framework.key}'."
                )
                continue
            requirement_ids.append(requirement_key_to_requirement_id[requirement_key])

        requests.post(
            f"{host}/api/controls/{control_id}/link",
            json={
                "framework_id": str(framework_id),
                "requirement_ids": list(map(str, requirement_ids)),
            },
            headers=headers,
            timeout=30,
        )

    requests.post(
        f"{host}/api/frameworks/{framework_id}/link",
        json={"risk_ids": list(map(str, risk_ids))},
        headers=headers,
        timeout=30,
    )
    print(f"Successfully linked framework '{framework.key}' to risks.")
    return framework_id


def get_framework_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/frameworks", headers=headers, timeout=30)
    response.raise_for_status()
    frameworks = Frameworks.model_validate(response.json())
    return {
        framework.key: framework.id
        for framework in frameworks.frameworks
        if framework.key is not None
    }


def create_models(*, host: str, api_key: str, models_dir: Path) -> None:
    if not models_dir.exists():
        return

    model_display_name_to_model_id = get_model_display_name_to_id(
        host=host, api_key=api_key
    )
    model_adapter_key_to_id = get_model_adapter_key_to_id(host=host, api_key=api_key)

    headers = get_headers(api_key)
    for file_path in models_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            model_data = yaml.safe_load(file)

        model_adapter_key = model_data.pop("adapter_key", None)
        if model_adapter_key is not None:
            adapter_id = model_adapter_key_to_id[model_adapter_key]
            model_data["adapter_id"] = adapter_id

        try:
            model = Model.model_validate(model_data)
        except ValidationError as error:
            print(f"Validation error in model definition at '{file_path}': {error}.")
            continue

        if model.display_name in model_display_name_to_model_id:
            print(f"Model '{model.display_name}' already exists.")
            continue

        response = requests.post(
            f"{host}/api/models",
            json=model.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code != 201:
            print(f"Failed to create model '{model.key}':\n{response.text}")
        else:
            print(f"Successfully created model '{model.display_name}'.")


def get_model_display_name_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/models", headers=headers, timeout=30)
    response.raise_for_status()
    models = StoredModels.model_validate(response.json())
    return {model.display_name: model.id for model in models.models}


def create_model_adapters(*, host: str, api_key: str, model_adapters_dir: Path) -> None:
    if not model_adapters_dir.exists():
        return

    model_adapter_key_to_id = get_model_adapter_key_to_id(host=host, api_key=api_key)

    headers = get_headers(api_key)
    for file_path in model_adapters_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            adapter_data = yaml.safe_load(file)

        try:
            model_adapter = ModelAdapter.model_validate(adapter_data)
        except ValidationError as error:
            print(
                f"Validation error in model adapter definition at '{file_path}': "
                f"{error}."
            )
            continue

        if model_adapter.key in model_adapter_key_to_id:
            print(f"Model adapter '{model_adapter.key}' already exists.")
            continue

        response = requests.post(
            f"{host}/api/model-adapters",
            json=model_adapter.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code != 201:
            print(
                f"Failed to create model adapter '{model_adapter.key}':\n{response.text}"
            )
        else:
            print(
                f"Successfully created model adapter '{adapter_data['display_name']}'."
            )


def get_model_adapter_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/model-adapters", headers=headers, timeout=30)
    response.raise_for_status()
    model_adapters = StoredModelAdapters.model_validate(response.json())
    return {
        model_adapter.key: model_adapter.id
        for model_adapter in model_adapters.model_adapters
        if model_adapter.key is not None
    }


def create_datasets(*, host: str, api_key: str, datasets_dir: Path) -> None:
    if not datasets_dir.exists():
        return

    dataset_display_name_to_dataset_id = get_dataset_display_name_to_id(
        host=host, api_key=api_key
    )

    headers = get_headers(api_key)
    headers.pop("content-type")
    for file_path in datasets_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            dataset_data = yaml.safe_load(file)

        try:
            dataset = Dataset.model_validate(dataset_data)
        except ValidationError as error:
            print(f"Validation error in dataset definition at '{file_path}': {error}.")
            continue

        if dataset.display_name in dataset_display_name_to_dataset_id:
            # TODO: we are abusing the display name as key here.
            print(f"Dataset '{dataset.display_name}' already exists.")
            continue

        csv_path = datasets_dir / f"{file_path.stem}.csv"
        response = requests.post(
            f"{host}/api/datasets",
            files=[
                ("file", ("data.csv", open(str(csv_path), "rb"), "text/csv")),
                (
                    "request",
                    (
                        None,
                        json.dumps(dataset.model_dump(mode="json")),
                        "application/json",
                    ),
                ),
            ],
            headers=headers,
            timeout=30,
        )
        if response.status_code != 201:
            print(f"Failed to create dataset '{dataset.display_name}': {response.text}")
        else:
            print(f"Successfully created dataset '{dataset.display_name}'.")


def get_dataset_display_name_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/datasets", headers=headers, timeout=30)
    response.raise_for_status()
    datasets = StoredDatasets.model_validate(response.json())
    return {dataset.display_name: dataset.id for dataset in datasets.datasets}


def create_ai_systems(*, host: str, api_key: str, ai_systems_dir: Path) -> None:
    if not ai_systems_dir.exists():
        return

    model_display_name_to_id = get_model_display_name_to_id(host=host, api_key=api_key)
    dataset_display_name_to_id = get_dataset_display_name_to_id(
        host=host, api_key=api_key
    )
    ai_system_display_name_to_ai_system = get_ai_system_display_name_to_ai_system(
        host=host, api_key=api_key
    )

    headers = get_headers(api_key)
    for file_path in ai_systems_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            ai_system_data = yaml.safe_load(file)

        model_display_names = ai_system_data.pop("model_display_names", [])
        model_ids: list[str] = []
        for model_display_name in model_display_names:
            if model_display_name not in model_display_name_to_id:
                print(f"No model with display name '{model_display_name}' exists.")
                continue
            model_ids.append(model_display_name_to_id[model_display_name])
        ai_system_data["model_ids"] = model_ids

        dataset_display_names = ai_system_data.pop("dataset_display_names", [])
        dataset_ids: list[str] = []
        for dataset_display_name in dataset_display_names:
            if dataset_display_name not in dataset_display_name_to_id:
                print(f"No dataset with display name '{dataset_display_name}' exists.")
                continue
            dataset_ids.append(dataset_display_name_to_id[dataset_display_name])
        ai_system_data["dataset_ids"] = dataset_ids

        try:
            ai_system = AISystem.model_validate(ai_system_data)
        except ValidationError as error:
            print(
                f"Validation error in AI system definition at '{file_path}': {error}."
            )
            continue

        if ai_system.display_name in ai_system_display_name_to_ai_system:
            # TODO: we are abusing the display name as key here.
            print(f"AI system '{ai_system.display_name}' already exists.")
            continue

        response = requests.post(
            f"{host}/api/ai-systems",
            json=ai_system.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code != 201:
            print(f"Failed to create AI system '{ai_system.key}':\n{response.text}")
        else:
            print(f"Successfully created AI system '{ai_system_data['display_name']}'.")


def get_ai_system_display_name_to_ai_system(
    *, host: str, api_key: str
) -> dict[str, StoredAISystem]:
    headers = get_headers(api_key)
    response = requests.get(f"{host}/api/ai-systems", headers=headers, timeout=30)
    response.raise_for_status()
    ai_systems = AISystems.model_validate(response.json())

    return {ai_system.display_name: ai_system for ai_system in ai_systems.ai_systems}


def get_metric_evaluator_key_to_id(*, host: str, api_key: str) -> dict[str, str]:
    headers = get_headers(api_key)
    response = requests.get(
        f"{host}/api/metric-evaluators", headers=headers, timeout=30
    )
    response.raise_for_status()
    metric_evaluators = StoredMetricEvaluators.model_validate(response.json())
    return {
        stored_metric_evaluator.key: stored_metric_evaluator.id
        for stored_metric_evaluator in metric_evaluators.metric_evaluators
        if stored_metric_evaluator.key is not None
    }


def create_evaluators(*, host: str, api_key: str, evaluators_dir: Path) -> None:
    if not evaluators_dir.exists():
        return

    dataset_display_name_to_id = get_dataset_display_name_to_id(
        host=host, api_key=api_key
    )
    metric_evaluator_key_to_id = get_metric_evaluator_key_to_id(
        host=host, api_key=api_key
    )
    headers = get_headers(api_key)

    for file_path in evaluators_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            metric_evaluator_data = yaml.safe_load(file)

        dataset_display_name = metric_evaluator_data["definition"].pop(
            "dataset_display_name"
        )
        metric_evaluator_data["definition"]["dataset_id"] = dataset_display_name_to_id[
            dataset_display_name
        ]

        try:
            metric_evaluator = TypeAdapter(MetricEvaluator).validate_python(
                metric_evaluator_data
            )
        except ValidationError as error:
            print(
                f"Validation error in metric evaluator definition at '{file_path}': "
                f"{error}."
            )
            continue

        if metric_evaluator.key in metric_evaluator_key_to_id:
            print(f"Metric evaluator with key '{metric_evaluator.key}' already exists.")
            continue

        response = requests.post(
            f"{host}/api/metric-evaluators",
            json=metric_evaluator.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code not in [201, 409]:
            raise Exception(response.text)
        else:
            print(
                f"Successfully created metric evaluator "
                f"'{metric_evaluator_data['display_name']}'."
            )


def create_artifacts(
    *, host: str, api_key: str, ai_systems_dir: Path, artifacts_dir: Path
) -> None:
    if not ai_systems_dir.exists() or not artifacts_dir.exists():
        return

    headers = get_headers(api_key)
    # Drop content type and allow `requests` to create the files as
    # 'multipart/form-data' content type with correct multipart boundary.
    headers.pop("content-type")

    ai_system_display_name_to_ai_system = get_ai_system_display_name_to_ai_system(
        host=host, api_key=api_key
    )
    for file_path in ai_systems_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            ai_system_data = yaml.safe_load(file)
        ai_system = ai_system_display_name_to_ai_system.get(
            ai_system_data["display_name"], None
        )
        if ai_system is None:
            print(f"AI system '{ai_system_data['display_name']}' does not exist.")
            continue

        for artifact in ai_system_data.get("artifacts", []):
            artifact_path = artifacts_dir / artifact
            if not artifact_path.exists():
                print(f"No artifact found at '{artifact_path}'.")
                continue

            if artifact in {artifact.file_name for artifact in ai_system.artifacts}:
                print(
                    f"Artifact '{artifact}' already exists for AI system "
                    f"'{ai_system.display_name}'."
                )
                continue

            with open(artifact_path, "rb") as file:
                response = requests.post(
                    f"{host}/api/ai-systems/{ai_system.id}/artifacts",
                    files={"artifact": file},
                    headers=headers,
                    timeout=30,
                )
            if response.status_code != 201:
                print(f"Failed to create artifact '{artifact}'.")
            else:
                print(f"Successfully created artifact '{artifact}'.")


def create_assessments(*, host: str, api_key: str, assessments_dir: Path) -> None:
    if not assessments_dir.exists():
        return

    ai_system_display_name_to_ai_system = get_ai_system_display_name_to_ai_system(
        host=host, api_key=api_key
    )
    framework_key_to_id = get_framework_key_to_id(host=host, api_key=api_key)
    requirement_key_to_id = get_requirement_key_to_id(host=host, api_key=api_key)
    metric_evaluator_key_to_id = get_metric_evaluator_key_to_id(
        host=host, api_key=api_key
    )

    headers = get_headers(api_key)

    response = requests.get(f"{host}/api/assessments", headers=headers, timeout=30)
    response.raise_for_status()
    assessment_display_name_to_id = {
        stored_assessment.display_name: stored_assessment.id
        for stored_assessment in StoredAssessments.model_validate(
            response.json()
        ).assessments
    }

    for file_path in assessments_dir.glob("*.y*ml"):
        with open(file_path, "r") as file:
            assessment_data = yaml.safe_load(file)

        assessment_display_name = assessment_data["display_name"]
        if assessment_display_name in assessment_display_name_to_id:
            print(f"Assessment '{assessment_display_name}' already exists.")
            continue
        if assessment_data["assessment_type"] != "technical_risk_assessment":
            print(
                f"Assessment type '{assessment_data['assessment_type']}' is not "
                f"supported."
            )
            continue

        ai_system_display_name = assessment_data["ai_system_display_name"]
        ai_system = ai_system_display_name_to_ai_system[ai_system_display_name]

        framework_key = assessment_data["framework_key"]
        framework_id = framework_key_to_id[framework_key]

        requirement_assessments: list[RequirementEvaluation] = []
        for requirement_assessment in assessment_data.get(
            "requirement_evaluations", []
        ):
            metric_evaluations: list[MetricEvaluation] = []
            for metric_evaluation in requirement_assessment.pop(
                "metric_evaluations", []
            ):
                if metric_evaluation.get("metric_evaluator_provider", None) == "user":
                    metric_evaluation["metric_evaluator_id"] = (
                        metric_evaluator_key_to_id[
                            metric_evaluation["metric_evaluator_key"]
                        ]
                    )

                metric_evaluations.append(
                    MetricEvaluation(
                        evaluated_entity_type=EvaluatedEntityType.MODEL,
                        evaluated_entity_id=ai_system.model_ids[0],
                        display_name=metric_evaluation["display_name"],
                        metric_evaluator_id=metric_evaluation["metric_evaluator_id"],
                        metric_evaluator_config=metric_evaluation[
                            "metric_evaluator_config"
                        ],
                        metric_score=None,
                    )
                )
            requirement_assessments.append(
                RequirementEvaluation(
                    requirement_id=requirement_key_to_id[
                        requirement_assessment["requirement_key"]
                    ],
                    status=AssessmentStatus(status="pending", reason=""),
                    metric_evaluations=metric_evaluations,
                )
            )

        assessment = TechnicalRiskAssessment(
            display_name=assessment_display_name,
            assessment_type=assessment_data["assessment_type"],
            ai_system_id=ai_system.id,
            framework_id=framework_id,
            requirement_evaluations=requirement_assessments,
        )

        response = requests.post(
            f"{host}/api/assessments",
            json=assessment.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code not in [201, 409]:
            print(
                f"Failed to create assessment '{assessment.display_name}':"
                f"\n{response.text}"
            )
        else:
            print(f"Successfully created assessment '{assessment.display_name}'.")


def activate_integrations(*, host: str, api_key: str) -> None:
    headers = get_headers(api_key)

    _OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
    _OPENAI_ORG = os.environ.get("OPENAI_ORG", None)
    if _OPENAI_API_KEY is not None:
        integration: Integration = OpenAIIntegration(
            api_key=SecretStr(_OPENAI_API_KEY), org_id=_OPENAI_ORG
        )
        response = requests.put(
            f"{host}/api/integrations/openai",
            json=integration.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code != 200:
            print(f"Failed to activate 'openai' integration:\n{response.text}.")
        else:
            print("Successfully activated 'openai' integration.")

    for env_var, integration_key in [
        ("TOGETHER_API_KEY", "together"),
        ("HF_TOKEN", "huggingface"),
    ]:
        try:
            api_key = os.environ[env_var]
        except KeyError:
            continue

        integration = Integration(api_key=SecretStr(api_key))
        response = requests.put(
            f"{host}/api/integrations/{integration_key}",
            json=integration.model_dump(mode="json"),
            headers=headers,
            timeout=30,
        )
        if response.status_code != 200:
            print(
                f"Failed to activate '{integration_key}' integration:\n{response.text}."
            )
        else:
            print(f"Successfully activated '{integration_key}' integration.")


def main() -> None:
    # Parse arguments.
    parser = argparse.ArgumentParser(
        description="LatticeFlow util for populating an AI GO! deployment."
    )

    parser.add_argument("--host", help="The URL of the deployment.", required=True)
    parser.add_argument("--api_key", help="API key for the deployment.", required=False)
    parser.add_argument(
        "--requirements_dir",
        help="The path of the directory containing the requirement YAMLs.",
        required=False,
    )
    parser.add_argument(
        "--controls_dir",
        help="The path of the directory containing the control YAMLs.",
        required=False,
    )
    parser.add_argument(
        "--risks_dir",
        help="The path of the directory containing the risk YAMLs.",
        required=False,
    )
    parser.add_argument(
        "--frameworks_dir",
        help="The path of the directory containing the framework YAMLs.",
        required=False,
    )
    parser.add_argument(
        "--demo_dir",
        help="The path of the directory containing demo files.",
        required=False,
    )
    args = parser.parse_args()

    if args.demo_dir is not None:
        data_dir = Path(args.demo_dir)
    else:
        data_dir = (
            get_core_path() / "assessment" / "latticeflow" / "assessment" / "templates"
        )

    if args.requirements_dir is not None:
        requirements_dir = Path(args.requirements_dir)
    elif args.demo_dir is not None:
        requirements_dir = data_dir / "requirements"
    else:
        requirements_dir = None

    if args.controls_dir is not None:
        controls_dir = Path(args.controls_dir)
    elif args.demo_dir is not None:
        controls_dir = data_dir / "controls"
    else:
        controls_dir = None

    if args.risks_dir is not None:
        risks_dir = Path(args.risks_dir)
    elif args.demo_dir is not None:
        risks_dir = data_dir / "risks"
    else:
        risks_dir = None

    if args.frameworks_dir is not None:
        frameworks_dir = Path(args.frameworks_dir)
    elif args.demo_dir is not None:
        frameworks_dir = data_dir / "frameworks"
    else:
        frameworks_dir = None

    host_is_up = wait_for_host_up(args.host, args.api_key)
    if args.api_key is None:
        api_key = complete_initial_setup(args.host).get_secret_value()
        print(f"API key: {api_key}")
    else:
        api_key = args.api_key

    if host_is_up:
        if requirements_dir is not None:
            requirement_key_to_requirement_id = create_requirements(
                host=args.host, api_key=api_key, requirements_dir=requirements_dir
            )
        if controls_dir is not None:
            control_key_to_control_id = create_controls(
                host=args.host, api_key=api_key, controls_dir=controls_dir
            )
        if risks_dir is not None:
            risk_key_to_risk_id = create_risks(
                host=args.host, api_key=api_key, risks_dir=risks_dir
            )
        if frameworks_dir is not None:
            for framework_path in sorted(frameworks_dir.glob("*.y*ml")):
                create_framework(
                    host=args.host,
                    api_key=api_key,
                    framework_path=framework_path,
                    risk_key_to_risk_id=risk_key_to_risk_id,
                    control_key_to_control_id=control_key_to_control_id,
                    requirement_key_to_requirement_id=requirement_key_to_requirement_id,
                )

        create_model_adapters(
            host=args.host,
            api_key=api_key,
            model_adapters_dir=data_dir / "model_adapters",
        )
        create_models(host=args.host, api_key=api_key, models_dir=data_dir / "models")
        create_datasets(
            host=args.host, api_key=api_key, datasets_dir=data_dir / "datasets"
        )
        create_ai_systems(
            host=args.host, api_key=api_key, ai_systems_dir=data_dir / "ai_systems"
        )
        create_artifacts(
            host=args.host,
            api_key=api_key,
            ai_systems_dir=data_dir / "ai_systems",
            artifacts_dir=data_dir / "artifacts",
        )
        create_evaluators(
            host=args.host, api_key=api_key, evaluators_dir=data_dir / "evaluators"
        )

        activate_integrations(host=args.host, api_key=api_key)

        create_assessments(
            host=args.host, api_key=api_key, assessments_dir=data_dir / "assessments"
        )
    else:
        print("Cannot populate deployment since host is not up.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
    )
    main()
