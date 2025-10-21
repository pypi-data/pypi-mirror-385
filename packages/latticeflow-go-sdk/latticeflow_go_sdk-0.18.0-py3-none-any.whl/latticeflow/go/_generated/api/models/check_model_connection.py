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
from ...models.model import ConnectionCheckResult
from ...models.model import Error
from ...types import Response


def _get_kwargs(model_id: str) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/models/{model_id}/check-connection",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Union[ConnectionCheckResult, Error]:
    if response.status_code == 200:
        response_200 = ConnectionCheckResult.model_validate(response.json())

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
) -> Response[Union[ConnectionCheckResult, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    model_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Response[Union[ConnectionCheckResult, Error]]:
    """Check the connection to the model.

     Use this API to check the basic connectivity and authentication to the model.

    The API will make an empty, possibly malformed, request to the model. The check
    is considered successful if the model responds with any 2xx or 4xx HTTP response,
    except for 401 and 403 - these are considered as errors in the authenticaiton to the
    model (e.g. due to invalid API key, etc.).

    Args:
        model_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionCheckResult, Error]]
    """
    kwargs = _get_kwargs(model_id=model_id)

    response = client.get_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


def sync(
    model_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Union[ConnectionCheckResult, Error]:
    """Check the connection to the model.

     Use this API to check the basic connectivity and authentication to the model.

    The API will make an empty, possibly malformed, request to the model. The check
    is considered successful if the model responds with any 2xx or 4xx HTTP response,
    except for 401 and 403 - these are considered as errors in the authenticaiton to the
    model (e.g. due to invalid API key, etc.).

    Args:
        model_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionCheckResult, Error]
    """
    return sync_detailed(model_id=model_id, client=client).parsed


async def asyncio_detailed(
    model_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Response[Union[ConnectionCheckResult, Error]]:
    """Check the connection to the model.

     Use this API to check the basic connectivity and authentication to the model.

    The API will make an empty, possibly malformed, request to the model. The check
    is considered successful if the model responds with any 2xx or 4xx HTTP response,
    except for 401 and 403 - these are considered as errors in the authenticaiton to the
    model (e.g. due to invalid API key, etc.).

    Args:
        model_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ConnectionCheckResult, Error]]
    """
    kwargs = _get_kwargs(model_id=model_id)

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    model_id: str, *, client: Union[AuthenticatedClient, Client]
) -> Union[ConnectionCheckResult, Error]:
    """Check the connection to the model.

     Use this API to check the basic connectivity and authentication to the model.

    The API will make an empty, possibly malformed, request to the model. The check
    is considered successful if the model responds with any 2xx or 4xx HTTP response,
    except for 401 and 403 - these are considered as errors in the authenticaiton to the
    model (e.g. due to invalid API key, etc.).

    Args:
        model_id (str):

    Raises:
        errors.ErrorParsingException: If the server returns an unparseable entity instead of an ``Error``.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ConnectionCheckResult, Error]
    """
    return (await asyncio_detailed(model_id=model_id, client=client)).parsed
