# Based on our override (see README.md) of openapi-python-client's Jinja template
# (https://github.com/openapi-generators/openapi-python-client/blob/main/openapi_python_client/templates/endpoint_module.py.jinja)

from http import HTTPStatus
from typing import Any
from typing import Union

import httpx
from pydantic import ValidationError

from ... import errors
from ...client import AuthenticatedClient
from ...client import Client
from ...models.model import Error
from ...models.model import ExternalGuardrailsAssessmentConfig
from ...models.model import ExternalTechnicalRiskAssessmentConfig
from ...types import Response


def _get_kwargs(assessment_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/assessments/{assessment_id}/external_config",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[
    Error,
    Union[
        "ExternalGuardrailsAssessmentConfig", "ExternalTechnicalRiskAssessmentConfig"
    ],
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_external_assessment_config_type_0 = (
                    ExternalTechnicalRiskAssessmentConfig.model_validate(data)
                )

                return componentsschemas_external_assessment_config_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_external_assessment_config_type_1 = (
                ExternalGuardrailsAssessmentConfig.model_validate(data)
            )

            return componentsschemas_external_assessment_config_type_1

        response_200 = _parse_response_200(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.model_validate(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.model_validate(response.json())

        return response_404

    # NOTE: We always try to parse the response as an error if all previous parsing has failed,
    # because the client generator only adds handling for status codes defined in the OpenAPI spec,
    # which does not always cover all possible error codes. This code was added by the Jinja template
    # located at `templates/overrides/endpoint_module.py.jinja`.
    try:
        return Error.model_validate(response.json())
    except ValidationError as e:
        raise errors.ErrorParsingException(
            "Could not parse the API-returned object as `Error`", e
        )


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        Error,
        Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ],
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    assessment_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Response[
    Union[
        Error,
        Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ],
    ]
]:
    """Get the external configuration for an assessment.

    Args:
        assessment_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['ExternalGuardrailsAssessmentConfig', 'ExternalTechnicalRiskAssessmentConfig']]]
    """
    kwargs = _get_kwargs(assessment_id=assessment_id)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    assessment_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Union[
    Error,
    Union[
        "ExternalGuardrailsAssessmentConfig", "ExternalTechnicalRiskAssessmentConfig"
    ],
]:
    """Get the external configuration for an assessment.

    Args:
        assessment_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['ExternalGuardrailsAssessmentConfig', 'ExternalTechnicalRiskAssessmentConfig']]
    """
    return sync_detailed(assessment_id=assessment_id, client=client).parsed


async def asyncio_detailed(
    assessment_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Response[
    Union[
        Error,
        Union[
            "ExternalGuardrailsAssessmentConfig",
            "ExternalTechnicalRiskAssessmentConfig",
        ],
    ]
]:
    """Get the external configuration for an assessment.

    Args:
        assessment_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['ExternalGuardrailsAssessmentConfig', 'ExternalTechnicalRiskAssessmentConfig']]]
    """
    kwargs = _get_kwargs(assessment_id=assessment_id)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assessment_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Union[
    Error,
    Union[
        "ExternalGuardrailsAssessmentConfig", "ExternalTechnicalRiskAssessmentConfig"
    ],
]:
    """Get the external configuration for an assessment.

    Args:
        assessment_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['ExternalGuardrailsAssessmentConfig', 'ExternalTechnicalRiskAssessmentConfig']]
    """
    return (await asyncio_detailed(assessment_id=assessment_id, client=client)).parsed
