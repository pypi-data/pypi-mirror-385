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
from ...models.model import GuardrailsAssessment
from ...models.model import RiskScreeningAssessment
from ...models.model import StoredGuardrailsAssessment
from ...models.model import StoredRiskScreeningAssessment
from ...models.model import StoredTechnicalRiskAssessment
from ...models.model import TechnicalRiskAssessment
from ...types import Response


def _get_kwargs(
    assessment_id: str,
    body: Union[
        "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
    ],
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {"method": "put", "url": f"/assessments/{assessment_id}"}

    if isinstance(body, TechnicalRiskAssessment):
        _kwargs["json"] = body.model_dump(mode="json")
    elif isinstance(body, GuardrailsAssessment):
        _kwargs["json"] = body.model_dump(mode="json")
    else:
        _kwargs["json"] = body.model_dump(mode="json")

    headers["Content-Type"] = "application/json"

    if headers:
        _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[
    Error,
    Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ],
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> Union[
            "StoredGuardrailsAssessment",
            "StoredRiskScreeningAssessment",
            "StoredTechnicalRiskAssessment",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stored_assessment_type_0 = (
                    StoredTechnicalRiskAssessment.model_validate(data)
                )

                return componentsschemas_stored_assessment_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_stored_assessment_type_1 = (
                    StoredGuardrailsAssessment.model_validate(data)
                )

                return componentsschemas_stored_assessment_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_stored_assessment_type_2 = (
                StoredRiskScreeningAssessment.model_validate(data)
            )

            return componentsschemas_stored_assessment_type_2

        response_200 = _parse_response_200(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.model_validate(response.json())

        return response_400

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
            "StoredGuardrailsAssessment",
            "StoredRiskScreeningAssessment",
            "StoredTechnicalRiskAssessment",
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
    assessment_id: str,
    body: Union[
        "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
    ],
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        Error,
        Union[
            "StoredGuardrailsAssessment",
            "StoredRiskScreeningAssessment",
            "StoredTechnicalRiskAssessment",
        ],
    ]
]:
    """Update an assessment

    Args:
        assessment_id (str):
        body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
            'TechnicalRiskAssessment']):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['StoredGuardrailsAssessment', 'StoredRiskScreeningAssessment', 'StoredTechnicalRiskAssessment']]]
    """
    kwargs = _get_kwargs(assessment_id=assessment_id, body=body)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    assessment_id: str,
    body: Union[
        "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
    ],
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[
    Error,
    Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ],
]:
    """Update an assessment

    Args:
        assessment_id (str):
        body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
            'TechnicalRiskAssessment']):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['StoredGuardrailsAssessment', 'StoredRiskScreeningAssessment', 'StoredTechnicalRiskAssessment']]
    """
    return sync_detailed(assessment_id=assessment_id, client=client, body=body).parsed


async def asyncio_detailed(
    assessment_id: str,
    body: Union[
        "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
    ],
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        Error,
        Union[
            "StoredGuardrailsAssessment",
            "StoredRiskScreeningAssessment",
            "StoredTechnicalRiskAssessment",
        ],
    ]
]:
    """Update an assessment

    Args:
        assessment_id (str):
        body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
            'TechnicalRiskAssessment']):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Union['StoredGuardrailsAssessment', 'StoredRiskScreeningAssessment', 'StoredTechnicalRiskAssessment']]]
    """
    kwargs = _get_kwargs(assessment_id=assessment_id, body=body)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    assessment_id: str,
    body: Union[
        "GuardrailsAssessment", "RiskScreeningAssessment", "TechnicalRiskAssessment"
    ],
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[
    Error,
    Union[
        "StoredGuardrailsAssessment",
        "StoredRiskScreeningAssessment",
        "StoredTechnicalRiskAssessment",
    ],
]:
    """Update an assessment

    Args:
        assessment_id (str):
        body (Union['GuardrailsAssessment', 'RiskScreeningAssessment',
            'TechnicalRiskAssessment']):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Union['StoredGuardrailsAssessment', 'StoredRiskScreeningAssessment', 'StoredTechnicalRiskAssessment']]
    """
    return (
        await asyncio_detailed(assessment_id=assessment_id, client=client, body=body)
    ).parsed
