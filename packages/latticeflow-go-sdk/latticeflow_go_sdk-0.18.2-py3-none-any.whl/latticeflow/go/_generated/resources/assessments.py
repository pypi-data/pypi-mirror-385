from typing import Union

from latticeflow.go._generated.api.assessments.cancel_assessment import (
    asyncio as cancel_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.cancel_assessment import (
    sync as cancel_assessment_sync,
)
from latticeflow.go._generated.api.assessments.convert_assessment_config import (
    asyncio as convert_assessment_config_asyncio,
)
from latticeflow.go._generated.api.assessments.convert_assessment_config import (
    sync as convert_assessment_config_sync,
)
from latticeflow.go._generated.api.assessments.create_assessment import (
    asyncio as create_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.create_assessment import (
    sync as create_assessment_sync,
)
from latticeflow.go._generated.api.assessments.create_assessment_report import (
    asyncio as create_assessment_report_asyncio,
)
from latticeflow.go._generated.api.assessments.create_assessment_report import (
    sync as create_assessment_report_sync,
)
from latticeflow.go._generated.api.assessments.delete_assessment import (
    asyncio as delete_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.delete_assessment import (
    sync as delete_assessment_sync,
)
from latticeflow.go._generated.api.assessments.download_assessment_result import (
    asyncio as download_assessment_result_asyncio,
)
from latticeflow.go._generated.api.assessments.download_assessment_result import (
    sync as download_assessment_result_sync,
)
from latticeflow.go._generated.api.assessments.get_assessment import (
    asyncio as get_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.get_assessment import (
    sync as get_assessment_sync,
)
from latticeflow.go._generated.api.assessments.get_assessment_config import (
    asyncio as get_assessment_config_asyncio,
)
from latticeflow.go._generated.api.assessments.get_assessment_config import (
    sync as get_assessment_config_sync,
)
from latticeflow.go._generated.api.assessments.get_assessment_configuration_templates import (
    asyncio as get_assessment_configuration_templates_asyncio,
)
from latticeflow.go._generated.api.assessments.get_assessment_configuration_templates import (
    sync as get_assessment_configuration_templates_sync,
)
from latticeflow.go._generated.api.assessments.get_assessment_report import (
    asyncio as get_assessment_report_asyncio,
)
from latticeflow.go._generated.api.assessments.get_assessment_report import (
    sync as get_assessment_report_sync,
)
from latticeflow.go._generated.api.assessments.get_assessments import (
    asyncio as get_assessments_asyncio,
)
from latticeflow.go._generated.api.assessments.get_assessments import (
    sync as get_assessments_sync,
)
from latticeflow.go._generated.api.assessments.get_technical_risk_assessments_for_risk_screening import (
    asyncio as get_technical_risk_assessments_for_risk_screening_asyncio,
)
from latticeflow.go._generated.api.assessments.get_technical_risk_assessments_for_risk_screening import (
    sync as get_technical_risk_assessments_for_risk_screening_sync,
)
from latticeflow.go._generated.api.assessments.import_assessment_result import (
    asyncio as import_assessment_result_asyncio,
)
from latticeflow.go._generated.api.assessments.import_assessment_result import (
    sync as import_assessment_result_sync,
)
from latticeflow.go._generated.api.assessments.replace_assessment_report import (
    asyncio as replace_assessment_report_asyncio,
)
from latticeflow.go._generated.api.assessments.replace_assessment_report import (
    sync as replace_assessment_report_sync,
)
from latticeflow.go._generated.api.assessments.run_assessment import (
    asyncio as run_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.run_assessment import (
    sync as run_assessment_sync,
)
from latticeflow.go._generated.api.assessments.update_assessment import (
    asyncio as update_assessment_asyncio,
)
from latticeflow.go._generated.api.assessments.update_assessment import (
    sync as update_assessment_sync,
)
from latticeflow.go._generated.api.assessments.update_risk_screening import (
    asyncio as update_risk_screening_asyncio,
)
from latticeflow.go._generated.api.assessments.update_risk_screening import (
    sync as update_risk_screening_sync,
)
from latticeflow.go._generated.models.body import ImportAssessmentResultBody
from latticeflow.go._generated.models.body import ReplaceAssessmentReportBody
from latticeflow.go._generated.models.model import AssessmentConfigs
from latticeflow.go._generated.models.model import Error
from latticeflow.go._generated.models.model import ExternalGuardrailsAssessmentConfig
from latticeflow.go._generated.models.model import ExternalTechnicalRiskAssessmentConfig
from latticeflow.go._generated.models.model import GuardrailsAssessment
from latticeflow.go._generated.models.model import GuardrailsAssessmentConfig
from latticeflow.go._generated.models.model import Pending
from latticeflow.go._generated.models.model import Report
from latticeflow.go._generated.models.model import RiskScreening
from latticeflow.go._generated.models.model import RiskScreeningAssessment
from latticeflow.go._generated.models.model import StoredAssessments
from latticeflow.go._generated.models.model import (
    StoredEligibleTechnicalRiskAssessments,
)
from latticeflow.go._generated.models.model import StoredGuardrailsAssessment
from latticeflow.go._generated.models.model import StoredRiskScreening
from latticeflow.go._generated.models.model import StoredRiskScreeningAssessment
from latticeflow.go._generated.models.model import StoredTechnicalRiskAssessment
from latticeflow.go._generated.models.model import Success
from latticeflow.go._generated.models.model import TechnicalRiskAssessment
from latticeflow.go._generated.models.model import TechnicalRiskAssessmentConfig
from latticeflow.go._generated.types import File
from latticeflow.go._generated.types import UNSET
from latticeflow.go._generated.types import Unset
from latticeflow.go.base import BaseClient
from latticeflow.go.types import ApiError


class AssessmentsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    def import_assessment_result(
        self, assessment_id: str, body: ImportAssessmentResultBody
    ) -> Success:
        """Import the result for a given assessment in a ZIP format.

         Imports the result for a given assessment.

        Args:
            assessment_id (str):
            body (ImportAssessmentResultBody):
        """
        with self._base.get_client() as client:
            response = import_assessment_result_sync(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def convert_assessment_config(
        self,
        body: Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ],
    ) -> Union["GuardrailsAssessmentConfig", "TechnicalRiskAssessmentConfig"]:
        """Convert an external assessment config to an internal one.

        Args:
            body (Union['ExternalGuardrailsAssessmentConfig',
                'ExternalTechnicalRiskAssessmentConfig']):
        """
        with self._base.get_client() as client:
            response = convert_assessment_config_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_assessment_configuration_templates(self) -> AssessmentConfigs:
        """Get all assessments configuration templates."""
        with self._base.get_client() as client:
            response = get_assessment_configuration_templates_sync(client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def replace_assessment_report(
        self, assessment_id: str, body: ReplaceAssessmentReportBody
    ) -> Report:
        """Updates report for the assessment with attached file (MD).

        Args:
            assessment_id (str):
            body (ReplaceAssessmentReportBody):
        """
        with self._base.get_client() as client:
            response = replace_assessment_report_sync(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_risk_screening(
        self, risk_screening_id: str, body: RiskScreening
    ) -> StoredRiskScreening:
        """Update a risk screening

        Args:
            risk_screening_id (str):
            body (RiskScreening):
        """
        with self._base.get_client() as client:
            response = update_risk_screening_sync(
                risk_screening_id=risk_screening_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_assessment_report(self, assessment_id: str) -> Union[Pending, Report]:
        """Get the report URI for an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = get_assessment_report_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def update_assessment(
        self,
        assessment_id: str,
        body: Union[
            "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
        ],
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Update an assessment

        Args:
            assessment_id (str):
            body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
                'TechnicalRiskAssessment']):
        """
        with self._base.get_client() as client:
            response = update_assessment_sync(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_assessment(
        self,
        body: Union[
            "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
        ],
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Create an assessment

        Args:
            body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
                'TechnicalRiskAssessment']):
        """
        with self._base.get_client() as client:
            response = create_assessment_sync(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_assessment(
        self, assessment_id: str
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Get an assessment.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = get_assessment_sync(assessment_id=assessment_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def cancel_assessment(self, assessment_id: str) -> Success:
        """Cancel the running assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = cancel_assessment_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def download_assessment_result(self, assessment_id: str) -> File:
        """Download the result for a given assessment in a ZIP format.

         Download the result for a given assessment in a ZIP format. This contains the artifacts for all
        metric evaluations and some metadata about the assessment itself.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = download_assessment_result_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_assessment_config(
        self, assessment_id: str
    ) -> Union[
        "ExternalGuardrailsAssessmentConfig", "ExternalTechnicalRiskAssessmentConfig"
    ]:
        """Get the external configuration for an assessment.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = get_assessment_config_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def run_assessment(self, assessment_id: str) -> Success:
        """Run an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = run_assessment_sync(assessment_id=assessment_id, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_assessments(
        self, *, key: Union[Unset, str] = UNSET, ai_system_id: Union[Unset, str] = UNSET
    ) -> StoredAssessments:
        """Get all assessments.

        Args:
            key (Union[Unset, str]):
            ai_system_id (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = get_assessments_sync(
                client=client, key=key, ai_system_id=ai_system_id
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def create_assessment_report(self, assessment_id: str) -> Pending:
        """Creates a new report for an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = create_assessment_report_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def get_technical_risk_assessments_for_risk_screening(
        self, risk_screening_id: str
    ) -> StoredEligibleTechnicalRiskAssessments:
        """Get a list of technical risk assessments that are eligible to be linked to the risk screening to
        determine likelihood.

        Args:
            risk_screening_id (str):
        """
        with self._base.get_client() as client:
            response = get_technical_risk_assessments_for_risk_screening_sync(
                risk_screening_id=risk_screening_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    def delete_assessment(self, assessment_id: str) -> Success:
        """Delete an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = delete_assessment_sync(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response


class AsyncAssessmentsResource:
    def __init__(self, base_client: BaseClient) -> None:
        self._base = base_client

    async def import_assessment_result(
        self, assessment_id: str, body: ImportAssessmentResultBody
    ) -> Success:
        """Import the result for a given assessment in a ZIP format.

         Imports the result for a given assessment.

        Args:
            assessment_id (str):
            body (ImportAssessmentResultBody):
        """
        with self._base.get_client() as client:
            response = await import_assessment_result_asyncio(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def convert_assessment_config(
        self,
        body: Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ],
    ) -> Union["GuardrailsAssessmentConfig", "TechnicalRiskAssessmentConfig"]:
        """Convert an external assessment config to an internal one.

        Args:
            body (Union['ExternalGuardrailsAssessmentConfig',
                'ExternalTechnicalRiskAssessmentConfig']):
        """
        with self._base.get_client() as client:
            response = await convert_assessment_config_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_assessment_configuration_templates(self) -> AssessmentConfigs:
        """Get all assessments configuration templates."""
        with self._base.get_client() as client:
            response = await get_assessment_configuration_templates_asyncio(
                client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def replace_assessment_report(
        self, assessment_id: str, body: ReplaceAssessmentReportBody
    ) -> Report:
        """Updates report for the assessment with attached file (MD).

        Args:
            assessment_id (str):
            body (ReplaceAssessmentReportBody):
        """
        with self._base.get_client() as client:
            response = await replace_assessment_report_asyncio(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_risk_screening(
        self, risk_screening_id: str, body: RiskScreening
    ) -> StoredRiskScreening:
        """Update a risk screening

        Args:
            risk_screening_id (str):
            body (RiskScreening):
        """
        with self._base.get_client() as client:
            response = await update_risk_screening_asyncio(
                risk_screening_id=risk_screening_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_assessment_report(self, assessment_id: str) -> Union[Pending, Report]:
        """Get the report URI for an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await get_assessment_report_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def update_assessment(
        self,
        assessment_id: str,
        body: Union[
            "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
        ],
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Update an assessment

        Args:
            assessment_id (str):
            body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
                'TechnicalRiskAssessment']):
        """
        with self._base.get_client() as client:
            response = await update_assessment_asyncio(
                assessment_id=assessment_id, body=body, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_assessment(
        self,
        body: Union[
            "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
        ],
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Create an assessment

        Args:
            body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
                'TechnicalRiskAssessment']):
        """
        with self._base.get_client() as client:
            response = await create_assessment_asyncio(body=body, client=client)
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_assessment(
        self, assessment_id: str
    ) -> Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ]:
        """Get an assessment.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await get_assessment_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def cancel_assessment(self, assessment_id: str) -> Success:
        """Cancel the running assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await cancel_assessment_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def download_assessment_result(self, assessment_id: str) -> File:
        """Download the result for a given assessment in a ZIP format.

         Download the result for a given assessment in a ZIP format. This contains the artifacts for all
        metric evaluations and some metadata about the assessment itself.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await download_assessment_result_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_assessment_config(
        self, assessment_id: str
    ) -> Union[
        "ExternalGuardrailsAssessmentConfig", "ExternalTechnicalRiskAssessmentConfig"
    ]:
        """Get the external configuration for an assessment.

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await get_assessment_config_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def run_assessment(self, assessment_id: str) -> Success:
        """Run an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await run_assessment_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_assessments(
        self, *, key: Union[Unset, str] = UNSET, ai_system_id: Union[Unset, str] = UNSET
    ) -> StoredAssessments:
        """Get all assessments.

        Args:
            key (Union[Unset, str]):
            ai_system_id (Union[Unset, str]):
        """
        with self._base.get_client() as client:
            response = await get_assessments_asyncio(
                client=client, key=key, ai_system_id=ai_system_id
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def create_assessment_report(self, assessment_id: str) -> Pending:
        """Creates a new report for an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await create_assessment_report_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def get_technical_risk_assessments_for_risk_screening(
        self, risk_screening_id: str
    ) -> StoredEligibleTechnicalRiskAssessments:
        """Get a list of technical risk assessments that are eligible to be linked to the risk screening to
        determine likelihood.

        Args:
            risk_screening_id (str):
        """
        with self._base.get_client() as client:
            response = await get_technical_risk_assessments_for_risk_screening_asyncio(
                risk_screening_id=risk_screening_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response

    async def delete_assessment(self, assessment_id: str) -> Success:
        """Delete an assessment

        Args:
            assessment_id (str):
        """
        with self._base.get_client() as client:
            response = await delete_assessment_asyncio(
                assessment_id=assessment_id, client=client
            )
            if isinstance(response, Error):
                raise ApiError(response)
            return response
