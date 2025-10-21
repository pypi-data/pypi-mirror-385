from __future__ import annotations

from typing import Union

from pydantic import Field

from latticeflow.go._generated.models.base_model import LFBaseModel

from .. import types
from ..models.model import Dataset
from ..models.model import MetricEvaluation
from ..types import File
from ..types import UNSET
from ..types import Unset


# ---- from create_dataset_body.py ----
class CreateDatasetBody(LFBaseModel):
    request: Dataset = Field(
        ...,
        description="All properties required for the creation of a Dataset, except the binary file.",
    )
    " All properties required for the creation of a Dataset, except the binary file. "
    file: File = Field(..., description="The CSV file to upload.")
    " The CSV file to upload. "

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        request = self.request
        files.append(("request", (None, request.model_dump_json(), "application/json")))
        file = self.file
        if isinstance(file, File):
            files.append(
                (
                    "file",
                    (
                        file.file_name or "file",
                        file.payload,
                        file.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from create_metric_evaluation_body.py ----
class CreateMetricEvaluationBody(LFBaseModel):
    request: MetricEvaluation = Field(..., description="")
    files: list[File] = Field(..., description="")

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        request = self.request
        files.append(("request", (None, request.model_dump_json(), "application/json")))
        files_value = self.files
        for f in files_value:
            files.append(
                (
                    "files",
                    (
                        f.file_name or "file",
                        f.payload,
                        f.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from import_assessment_result_body.py ----
class ImportAssessmentResultBody(LFBaseModel):
    file: Union[Unset, File] = Field(default=UNSET, description="")

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        file = self.file
        if isinstance(file, File):
            files.append(
                (
                    "file",
                    (
                        file.file_name or "file",
                        file.payload,
                        file.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from import_framework_body.py ----
class ImportFrameworkBody(LFBaseModel):
    file: Union[Unset, File] = Field(default=UNSET, description="")

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        file = self.file
        if isinstance(file, File):
            files.append(
                (
                    "file",
                    (
                        file.file_name or "file",
                        file.payload,
                        file.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from replace_assessment_report_body.py ----
class ReplaceAssessmentReportBody(LFBaseModel):
    report: Union[Unset, File] = Field(default=UNSET, description="")

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        report = self.report
        if isinstance(report, File):
            files.append(
                (
                    "report",
                    (
                        report.file_name or "file",
                        report.payload,
                        report.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from update_dataset_data_body.py ----
class UpdateDatasetDataBody(LFBaseModel):
    file: File = Field(..., description="The updated CSV file.")
    " The updated CSV file. "

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        file = self.file
        if isinstance(file, File):
            files.append(
                (
                    "file",
                    (
                        file.file_name or "file",
                        file.payload,
                        file.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files


# ---- from upload_ai_system_artifact_body.py ----
class UploadAISystemArtifactBody(LFBaseModel):
    artifact: Union[Unset, File] = Field(default=UNSET, description="")

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []
        artifact = self.artifact
        if isinstance(artifact, File):
            files.append(
                (
                    "artifact",
                    (
                        artifact.file_name or "file",
                        artifact.payload,
                        artifact.mime_type or "application/octet-stream",
                    ),
                )
            )
        return files
