from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...types import Response


def _get_kwargs(
    client_id: str,
    api_key_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/service_accounts/{client_id}/api_keys/{api_key_id}",
    }


    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Any | None:
    if response.status_code == 200:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    client_id: str,
    api_key_id: str,
    *,
    client: Union[Client],

) -> Response[Any]:
    """ Delete API key for service account

     Deletes an API key for a service account.

    Args:
        client_id (str):
        api_key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        client_id=client_id,
api_key_id=api_key_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    client_id: str,
    api_key_id: str,
    *,
    client: Union[Client],

) -> Response[Any]:
    """ Delete API key for service account

     Deletes an API key for a service account.

    Args:
        client_id (str):
        api_key_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        client_id=client_id,
api_key_id=api_key_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

