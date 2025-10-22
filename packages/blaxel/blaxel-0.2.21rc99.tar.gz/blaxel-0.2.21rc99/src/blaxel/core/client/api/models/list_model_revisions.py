from http import HTTPStatus
from typing import Any, Union

import httpx

from ... import errors
from ...client import Client
from ...models.revision_metadata import RevisionMetadata
from ...types import Response


def _get_kwargs(
    model_name: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/models/{model_name}/revisions",
    }


    return _kwargs


def _parse_response(*, client: Client, response: httpx.Response) -> list['RevisionMetadata'] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in (_response_200):
            response_200_item = RevisionMetadata.from_dict(response_200_item_data)



            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Client, response: httpx.Response) -> Response[list['RevisionMetadata']]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    model_name: str,
    *,
    client: Union[Client],

) -> Response[list['RevisionMetadata']]:
    """ List model revisions

     Returns revisions for a model by name.

    Args:
        model_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RevisionMetadata']]
     """


    kwargs = _get_kwargs(
        model_name=model_name,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    model_name: str,
    *,
    client: Union[Client],

) -> list['RevisionMetadata'] | None:
    """ List model revisions

     Returns revisions for a model by name.

    Args:
        model_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RevisionMetadata']
     """


    return sync_detailed(
        model_name=model_name,
client=client,

    ).parsed

async def asyncio_detailed(
    model_name: str,
    *,
    client: Union[Client],

) -> Response[list['RevisionMetadata']]:
    """ List model revisions

     Returns revisions for a model by name.

    Args:
        model_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list['RevisionMetadata']]
     """


    kwargs = _get_kwargs(
        model_name=model_name,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    model_name: str,
    *,
    client: Union[Client],

) -> list['RevisionMetadata'] | None:
    """ List model revisions

     Returns revisions for a model by name.

    Args:
        model_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list['RevisionMetadata']
     """


    return (await asyncio_detailed(
        model_name=model_name,
client=client,

    )).parsed
