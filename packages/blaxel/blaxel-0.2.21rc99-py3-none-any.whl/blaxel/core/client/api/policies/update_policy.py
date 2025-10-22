from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...models.policy import Policy
from ...types import Response


def _get_kwargs(
    policy_name: str,
    *,
    body: Policy,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/policies/{policy_name}",
    }

    if type(body) is dict:
        _body = body
    else:
        _body = body.to_dict()


    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> Policy | None:
    if response.status_code == 200:
        response_200 = Policy.from_dict(response.json())



        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[Policy]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    policy_name: str,
    *,
    client: Union[Client],
    body: Policy,

) -> Response[Policy]:
    """ Update policy

     Updates a policy.

    Args:
        policy_name (str):
        body (Policy): Rule that controls how a deployment is made and served (e.g. location
            restrictions)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Policy]
     """


    kwargs = _get_kwargs(
        policy_name=policy_name,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    policy_name: str,
    *,
    client: Union[Client],
    body: Policy,

) -> Policy | None:
    """ Update policy

     Updates a policy.

    Args:
        policy_name (str):
        body (Policy): Rule that controls how a deployment is made and served (e.g. location
            restrictions)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Policy
     """


    return sync_detailed(
        policy_name=policy_name,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    policy_name: str,
    *,
    client: Union[Client],
    body: Policy,

) -> Response[Policy]:
    """ Update policy

     Updates a policy.

    Args:
        policy_name (str):
        body (Policy): Rule that controls how a deployment is made and served (e.g. location
            restrictions)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Policy]
     """


    kwargs = _get_kwargs(
        policy_name=policy_name,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    policy_name: str,
    *,
    client: Union[Client],
    body: Policy,

) -> Policy | None:
    """ Update policy

     Updates a policy.

    Args:
        policy_name (str):
        body (Policy): Rule that controls how a deployment is made and served (e.g. location
            restrictions)

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Policy
     """


    return (await asyncio_detailed(
        policy_name=policy_name,
client=client,
body=body,

    )).parsed
