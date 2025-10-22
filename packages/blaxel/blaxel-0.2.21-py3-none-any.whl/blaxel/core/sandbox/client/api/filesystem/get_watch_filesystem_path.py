from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...models.error_response import ErrorResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    path: str,
    *,
    ignore: Union[Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["ignore"] = ignore

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/watch/filesystem/{path}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Union[ErrorResponse, str] | None:
    if response.status_code == 200:
        response_200 = response.text
        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.text)

        return response_400
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.text)

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[ErrorResponse, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    path: str,
    *,
    client: Union[Client],
    ignore: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, str]]:
    """Stream file modification events in a directory

     Streams the path of modified files (one per line) in the given directory. Closes when the client
    disconnects.

    Args:
        path (str):
        ignore (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, str]]
    """

    kwargs = _get_kwargs(
        path=path,
        ignore=ignore,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    path: str,
    *,
    client: Union[Client],
    ignore: Union[Unset, str] = UNSET,
) -> Union[ErrorResponse, str] | None:
    """Stream file modification events in a directory

     Streams the path of modified files (one per line) in the given directory. Closes when the client
    disconnects.

    Args:
        path (str):
        ignore (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, str]
    """

    return sync_detailed(
        path=path,
        client=client,
        ignore=ignore,
    ).parsed


async def asyncio_detailed(
    path: str,
    *,
    client: Union[Client],
    ignore: Union[Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, str]]:
    """Stream file modification events in a directory

     Streams the path of modified files (one per line) in the given directory. Closes when the client
    disconnects.

    Args:
        path (str):
        ignore (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, str]]
    """

    kwargs = _get_kwargs(
        path=path,
        ignore=ignore,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    path: str,
    *,
    client: Union[Client],
    ignore: Union[Unset, str] = UNSET,
) -> Union[ErrorResponse, str] | None:
    """Stream file modification events in a directory

     Streams the path of modified files (one per line) in the given directory. Closes when the client
    disconnects.

    Args:
        path (str):
        ignore (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, str]
    """

    return (
        await asyncio_detailed(
            path=path,
            client=client,
            ignore=ignore,
        )
    ).parsed
