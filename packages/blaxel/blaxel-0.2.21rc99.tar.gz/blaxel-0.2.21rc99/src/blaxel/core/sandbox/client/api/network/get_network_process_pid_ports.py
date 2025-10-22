from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...models.error_response import ErrorResponse
from ...models.get_network_process_pid_ports_response_200 import (
    GetNetworkProcessPidPortsResponse200,
)
from ...types import Response


def _get_kwargs(
    pid: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/network/process/{pid}/ports",
    }

    return _kwargs


def _parse_response(
    *, client: Client, response: httpx.Response
) -> Union[ErrorResponse, GetNetworkProcessPidPortsResponse200] | None:
    if response.status_code == 200:
        response_200 = GetNetworkProcessPidPortsResponse200.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 422:
        response_422 = ErrorResponse.from_dict(response.json())

        return response_422
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Client, response: httpx.Response
) -> Response[Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pid: int,
    *,
    client: Union[Client],
) -> Response[Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]]:
    """Get open ports for a process

     Get a list of all open ports for a process

    Args:
        pid (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]]
    """

    kwargs = _get_kwargs(
        pid=pid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pid: int,
    *,
    client: Union[Client],
) -> Union[ErrorResponse, GetNetworkProcessPidPortsResponse200] | None:
    """Get open ports for a process

     Get a list of all open ports for a process

    Args:
        pid (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]
    """

    return sync_detailed(
        pid=pid,
        client=client,
    ).parsed


async def asyncio_detailed(
    pid: int,
    *,
    client: Union[Client],
) -> Response[Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]]:
    """Get open ports for a process

     Get a list of all open ports for a process

    Args:
        pid (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]]
    """

    kwargs = _get_kwargs(
        pid=pid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pid: int,
    *,
    client: Union[Client],
) -> Union[ErrorResponse, GetNetworkProcessPidPortsResponse200] | None:
    """Get open ports for a process

     Get a list of all open ports for a process

    Args:
        pid (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, GetNetworkProcessPidPortsResponse200]
    """

    return (
        await asyncio_detailed(
            pid=pid,
            client=client,
        )
    ).parsed
