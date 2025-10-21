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
from ...models.body import UploadAISystemArtifactBody
from ...models.model import Error
from ...models.model import Success
from ...types import Response


def _get_kwargs(ai_system_id: str, body: UploadAISystemArtifactBody) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/ai-systems/{ai_system_id}/artifacts",
    }

    _kwargs["files"] = body.to_multipart()

    if headers:
        _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Error, Success]:
    if response.status_code == 201:
        response_201 = Success.model_validate(response.json())

        return response_201

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
) -> Response[Union[Error, Success]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    ai_system_id: str,
    body: UploadAISystemArtifactBody,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, Success]]:
    """Uploads an artifact, associated with an AI system.

    Args:
        ai_system_id (str):
        body (UploadAISystemArtifactBody):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Success]]
    """
    kwargs = _get_kwargs(ai_system_id=ai_system_id, body=body)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    ai_system_id: str,
    body: UploadAISystemArtifactBody,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Error, Success]:
    """Uploads an artifact, associated with an AI system.

    Args:
        ai_system_id (str):
        body (UploadAISystemArtifactBody):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Success]
    """
    return sync_detailed(ai_system_id=ai_system_id, client=client, body=body).parsed


async def asyncio_detailed(
    ai_system_id: str,
    body: UploadAISystemArtifactBody,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, Success]]:
    """Uploads an artifact, associated with an AI system.

    Args:
        ai_system_id (str):
        body (UploadAISystemArtifactBody):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, Success]]
    """
    kwargs = _get_kwargs(ai_system_id=ai_system_id, body=body)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    ai_system_id: str,
    body: UploadAISystemArtifactBody,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Error, Success]:
    """Uploads an artifact, associated with an AI system.

    Args:
        ai_system_id (str):
        body (UploadAISystemArtifactBody):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, Success]
    """
    return (
        await asyncio_detailed(ai_system_id=ai_system_id, client=client, body=body)
    ).parsed
