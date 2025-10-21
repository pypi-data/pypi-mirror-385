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
from ...models.model import Integration
from ...models.model import StoredIntegration
from ...types import Response


def _get_kwargs(integration_id: str, body: Integration) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/integrations/{integration_id}",
    }

    _kwargs["json"] = body.model_dump(mode="json")

    headers["Content-Type"] = "application/json"

    if headers:
        _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[Error, StoredIntegration]:
    if response.status_code == 200:
        response_200 = StoredIntegration.model_validate(response.json())

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
) -> Response[Union[Error, StoredIntegration]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    integration_id: str,
    body: Integration,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, StoredIntegration]]:
    """Update the integrations that have simple connection info(only api_key).

    Args:
        integration_id (str):
        body (Integration): Basic integration information shared between most integrations.

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, StoredIntegration]]
    """
    kwargs = _get_kwargs(integration_id=integration_id, body=body)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    integration_id: str,
    body: Integration,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Error, StoredIntegration]:
    """Update the integrations that have simple connection info(only api_key).

    Args:
        integration_id (str):
        body (Integration): Basic integration information shared between most integrations.

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, StoredIntegration]
    """
    return sync_detailed(integration_id=integration_id, client=client, body=body).parsed


async def asyncio_detailed(
    integration_id: str,
    body: Integration,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Error, StoredIntegration]]:
    """Update the integrations that have simple connection info(only api_key).

    Args:
        integration_id (str):
        body (Integration): Basic integration information shared between most integrations.

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Error, StoredIntegration]]
    """
    kwargs = _get_kwargs(integration_id=integration_id, body=body)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    integration_id: str,
    body: Integration,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Union[Error, StoredIntegration]:
    """Update the integrations that have simple connection info(only api_key).

    Args:
        integration_id (str):
        body (Integration): Basic integration information shared between most integrations.

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Error, StoredIntegration]
    """
    return (
        await asyncio_detailed(integration_id=integration_id, client=client, body=body)
    ).parsed
