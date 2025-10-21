from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.byte_array_content import ByteArrayContent
from ...types import Response


def _get_kwargs(
    brand_id: int,
    id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/brand/{brand_id}/Invoice/{id}/excel",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ByteArrayContent]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ByteArrayContent.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ByteArrayContent]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    brand_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ByteArrayContent]:
    """Get Brand Invoice Excel By ID

     Gets the Brand invoice Excel with the specified ID.

    Args:
        brand_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    brand_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ByteArrayContent]:
    """Get Brand Invoice Excel By ID

     Gets the Brand invoice Excel with the specified ID.

    Args:
        brand_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return sync_detailed(
        brand_id=brand_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    brand_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ByteArrayContent]:
    """Get Brand Invoice Excel By ID

     Gets the Brand invoice Excel with the specified ID.

    Args:
        brand_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    brand_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ByteArrayContent]:
    """Get Brand Invoice Excel By ID

     Gets the Brand invoice Excel with the specified ID.

    Args:
        brand_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return (
        await asyncio_detailed(
            brand_id=brand_id,
            id=id,
            client=client,
        )
    ).parsed
