from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...models.workspace import Workspace
from ...types import Response


def _get_kwargs(
    workspace_name: str,
    *,
    body: Workspace,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/workspaces/{workspace_name}",
    }

    if type(body) is dict:
        _body = body
    else:
        _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Workspace | None:
    if response.status_code == 200:
        response_200 = Workspace.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Workspace]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    workspace_name: str,
    *,
    client: Union[Client],
    body: Workspace,

) -> Response[Workspace]:
    """ Update workspace

     Updates a workspace by name.

    Args:
        workspace_name (str):
        body (Workspace): Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Workspace]
     """


    kwargs = _get_kwargs(
        workspace_name=workspace_name,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    workspace_name: str,
    *,
    client: Union[Client],
    body: Workspace,

) -> Workspace | None:
    """ Update workspace

     Updates a workspace by name.

    Args:
        workspace_name (str):
        body (Workspace): Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Workspace
     """


    return sync_detailed(
        workspace_name=workspace_name,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    workspace_name: str,
    *,
    client: Union[Client],
    body: Workspace,

) -> Response[Workspace]:
    """ Update workspace

     Updates a workspace by name.

    Args:
        workspace_name (str):
        body (Workspace): Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Workspace]
     """


    kwargs = _get_kwargs(
        workspace_name=workspace_name,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    workspace_name: str,
    *,
    client: Union[Client],
    body: Workspace,

) -> Workspace | None:
    """ Update workspace

     Updates a workspace by name.

    Args:
        workspace_name (str):
        body (Workspace): Workspace

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Workspace
     """


    return (await asyncio_detailed(
        workspace_name=workspace_name,
client=client,
body=body,

    )).parsed
