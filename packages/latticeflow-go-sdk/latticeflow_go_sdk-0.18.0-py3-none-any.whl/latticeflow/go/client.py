from latticeflow.go._generated.resources.ai_systems import AiSystemsResource
from latticeflow.go._generated.resources.ai_systems import AsyncAiSystemsResource
from latticeflow.go._generated.resources.assessments import AssessmentsResource
from latticeflow.go._generated.resources.assessments import AsyncAssessmentsResource
from latticeflow.go._generated.resources.chat import AsyncChatResource
from latticeflow.go._generated.resources.chat import ChatResource
from latticeflow.go._generated.resources.controls import AsyncControlsResource
from latticeflow.go._generated.resources.controls import ControlsResource
from latticeflow.go._generated.resources.dataset_generators import (
    AsyncDatasetGeneratorsResource,
)
from latticeflow.go._generated.resources.dataset_generators import (
    DatasetGeneratorsResource,
)
from latticeflow.go._generated.resources.datasets import AsyncDatasetsResource
from latticeflow.go._generated.resources.datasets import DatasetsResource
from latticeflow.go._generated.resources.evaluations import AsyncEvaluationsResource
from latticeflow.go._generated.resources.evaluations import EvaluationsResource
from latticeflow.go._generated.resources.framework_templates import (
    AsyncFrameworkTemplatesResource,
)
from latticeflow.go._generated.resources.framework_templates import (
    FrameworkTemplatesResource,
)
from latticeflow.go._generated.resources.frameworks import AsyncFrameworksResource
from latticeflow.go._generated.resources.frameworks import FrameworksResource
from latticeflow.go._generated.resources.integrations import AsyncIntegrationsResource
from latticeflow.go._generated.resources.integrations import IntegrationsResource
from latticeflow.go._generated.resources.metric_evaluators import (
    AsyncMetricEvaluatorsResource,
)
from latticeflow.go._generated.resources.metric_evaluators import (
    MetricEvaluatorsResource,
)
from latticeflow.go._generated.resources.metrics import AsyncMetricsResource
from latticeflow.go._generated.resources.metrics import MetricsResource
from latticeflow.go._generated.resources.model_adapters import (
    AsyncModelAdaptersResource,
)
from latticeflow.go._generated.resources.model_adapters import ModelAdaptersResource
from latticeflow.go._generated.resources.model_providers import (
    AsyncModelProvidersResource,
)
from latticeflow.go._generated.resources.model_providers import ModelProvidersResource
from latticeflow.go._generated.resources.models import AsyncModelsResource
from latticeflow.go._generated.resources.models import ModelsResource
from latticeflow.go._generated.resources.requirements import AsyncRequirementsResource
from latticeflow.go._generated.resources.requirements import RequirementsResource
from latticeflow.go._generated.resources.risks import AsyncRisksResource
from latticeflow.go._generated.resources.risks import RisksResource
from latticeflow.go._generated.resources.tags import AsyncTagsResource
from latticeflow.go._generated.resources.tags import TagsResource
from latticeflow.go._generated.resources.tenants import AsyncTenantsResource
from latticeflow.go._generated.resources.tenants import TenantsResource
from latticeflow.go._generated.resources.users import AsyncUsersResource
from latticeflow.go._generated.resources.users import UsersResource
from latticeflow.go.base import BaseClient


class Client(BaseClient):
    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True) -> None:
        """Synchronous API Client.

        Args:
            base_url: The base URL for the API, all requests are made to a relative path to this URL
            api_key: The API key to use for authentication
            verify_ssl: Whether to verify the SSL certificate of the API server. This should be True in production, but can be set to False for testing purposes.
        """
        super().__init__(base_url=base_url, api_key=api_key, verify_ssl=verify_ssl)

    @property
    def tags(self) -> TagsResource:
        return TagsResource(self)

    @property
    def controls(self) -> ControlsResource:
        return ControlsResource(self)

    @property
    def dataset_generators(self) -> DatasetGeneratorsResource:
        return DatasetGeneratorsResource(self)

    @property
    def assessments(self) -> AssessmentsResource:
        return AssessmentsResource(self)

    @property
    def metric_evaluators(self) -> MetricEvaluatorsResource:
        return MetricEvaluatorsResource(self)

    @property
    def risks(self) -> RisksResource:
        return RisksResource(self)

    @property
    def frameworks(self) -> FrameworksResource:
        return FrameworksResource(self)

    @property
    def requirements(self) -> RequirementsResource:
        return RequirementsResource(self)

    @property
    def model_providers(self) -> ModelProvidersResource:
        return ModelProvidersResource(self)

    @property
    def model_adapters(self) -> ModelAdaptersResource:
        return ModelAdaptersResource(self)

    @property
    def tenants(self) -> TenantsResource:
        return TenantsResource(self)

    @property
    def users(self) -> UsersResource:
        return UsersResource(self)

    @property
    def framework_templates(self) -> FrameworkTemplatesResource:
        return FrameworkTemplatesResource(self)

    @property
    def metrics(self) -> MetricsResource:
        return MetricsResource(self)

    @property
    def evaluations(self) -> EvaluationsResource:
        return EvaluationsResource(self)

    @property
    def ai_systems(self) -> AiSystemsResource:
        return AiSystemsResource(self)

    @property
    def models(self) -> ModelsResource:
        return ModelsResource(self)

    @property
    def datasets(self) -> DatasetsResource:
        return DatasetsResource(self)

    @property
    def chat(self) -> ChatResource:
        return ChatResource(self)

    @property
    def integrations(self) -> IntegrationsResource:
        return IntegrationsResource(self)


class AsyncClient(BaseClient):
    def __init__(self, base_url: str, api_key: str, verify_ssl: bool = True) -> None:
        """Asynchronous API Client.

        Args:
            base_url: The base URL for the API, all requests are made to a relative path to this URL
            api_key: The API key to use for authentication
            verify_ssl: Whether to verify the SSL certificate of the API server. This should be True in production, but can be set to False for testing purposes.
        """
        super().__init__(base_url=base_url, api_key=api_key, verify_ssl=verify_ssl)

    @property
    def tags(self) -> AsyncTagsResource:
        return AsyncTagsResource(self)

    @property
    def controls(self) -> AsyncControlsResource:
        return AsyncControlsResource(self)

    @property
    def dataset_generators(self) -> AsyncDatasetGeneratorsResource:
        return AsyncDatasetGeneratorsResource(self)

    @property
    def assessments(self) -> AsyncAssessmentsResource:
        return AsyncAssessmentsResource(self)

    @property
    def metric_evaluators(self) -> AsyncMetricEvaluatorsResource:
        return AsyncMetricEvaluatorsResource(self)

    @property
    def risks(self) -> AsyncRisksResource:
        return AsyncRisksResource(self)

    @property
    def frameworks(self) -> AsyncFrameworksResource:
        return AsyncFrameworksResource(self)

    @property
    def requirements(self) -> AsyncRequirementsResource:
        return AsyncRequirementsResource(self)

    @property
    def model_providers(self) -> AsyncModelProvidersResource:
        return AsyncModelProvidersResource(self)

    @property
    def model_adapters(self) -> AsyncModelAdaptersResource:
        return AsyncModelAdaptersResource(self)

    @property
    def tenants(self) -> AsyncTenantsResource:
        return AsyncTenantsResource(self)

    @property
    def users(self) -> AsyncUsersResource:
        return AsyncUsersResource(self)

    @property
    def framework_templates(self) -> AsyncFrameworkTemplatesResource:
        return AsyncFrameworkTemplatesResource(self)

    @property
    def metrics(self) -> AsyncMetricsResource:
        return AsyncMetricsResource(self)

    @property
    def evaluations(self) -> AsyncEvaluationsResource:
        return AsyncEvaluationsResource(self)

    @property
    def ai_systems(self) -> AsyncAiSystemsResource:
        return AsyncAiSystemsResource(self)

    @property
    def models(self) -> AsyncModelsResource:
        return AsyncModelsResource(self)

    @property
    def datasets(self) -> AsyncDatasetsResource:
        return AsyncDatasetsResource(self)

    @property
    def chat(self) -> AsyncChatResource:
        return AsyncChatResource(self)

    @property
    def integrations(self) -> AsyncIntegrationsResource:
        return AsyncIntegrationsResource(self)
