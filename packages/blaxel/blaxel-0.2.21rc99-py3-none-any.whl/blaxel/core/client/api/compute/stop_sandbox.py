from http import HTTPStatus
from typing import Any, Union, cast

import httpx

from ... import errors
from ...client import Client
from ...models.stop_sandbox import StopSandbox
from ...types import Response


def _get_kwargs(
    sandbox_name: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/sandboxes/{sandbox_name}/stop",
    }


    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Union[Any, StopSandbox] | None:
    if response.status_code == 200:
        response_200 = StopSandbox.from_dict(response.json())



        return response_200
    if response.status_code == 409:
        response_409 = cast(Any, None)
        return response_409
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Union[Any, StopSandbox]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sandbox_name: str,
    *,
    client: Union[Client],

) -> Response[Union[Any, StopSandbox]]:
    """ Stop Sandbox

     Stops a Sandbox by name.

    Args:
        sandbox_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, StopSandbox]]
     """


    kwargs = _get_kwargs(
        sandbox_name=sandbox_name,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    sandbox_name: str,
    *,
    client: Union[Client],

) -> Union[Any, StopSandbox] | None:
    """ Stop Sandbox

     Stops a Sandbox by name.

    Args:
        sandbox_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, StopSandbox]
     """


    return sync_detailed(
        sandbox_name=sandbox_name,
client=client,

    ).parsed

async def asyncio_detailed(
    sandbox_name: str,
    *,
    client: Union[Client],

) -> Response[Union[Any, StopSandbox]]:
    """ Stop Sandbox

     Stops a Sandbox by name.

    Args:
        sandbox_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, StopSandbox]]
     """


    kwargs = _get_kwargs(
        sandbox_name=sandbox_name,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    sandbox_name: str,
    *,
    client: Union[Client],

) -> Union[Any, StopSandbox] | None:
    """ Stop Sandbox

     Stops a Sandbox by name.

    Args:
        sandbox_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, StopSandbox]
     """


    return (await asyncio_detailed(
        sandbox_name=sandbox_name,
client=client,

    )).parsed
