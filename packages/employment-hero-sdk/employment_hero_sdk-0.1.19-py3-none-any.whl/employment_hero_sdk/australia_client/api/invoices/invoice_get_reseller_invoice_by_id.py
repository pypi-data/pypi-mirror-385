from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.invoice_model import InvoiceModel
from ...types import Response


def _get_kwargs(
    reseller_id: int,
    id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/reseller/{reseller_id}/Invoice/{id}",
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[InvoiceModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = InvoiceModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[InvoiceModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    reseller_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[InvoiceModel]:
    """Get Reseller Invoice By ID

     Gets the Reseller invoice with the specified ID.

    Args:
        reseller_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InvoiceModel]
    """

    kwargs = _get_kwargs(
        reseller_id=reseller_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    reseller_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[InvoiceModel]:
    """Get Reseller Invoice By ID

     Gets the Reseller invoice with the specified ID.

    Args:
        reseller_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InvoiceModel
    """

    return sync_detailed(
        reseller_id=reseller_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    reseller_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[InvoiceModel]:
    """Get Reseller Invoice By ID

     Gets the Reseller invoice with the specified ID.

    Args:
        reseller_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[InvoiceModel]
    """

    kwargs = _get_kwargs(
        reseller_id=reseller_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    reseller_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[InvoiceModel]:
    """Get Reseller Invoice By ID

     Gets the Reseller invoice with the specified ID.

    Args:
        reseller_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        InvoiceModel
    """

    return (
        await asyncio_detailed(
            reseller_id=reseller_id,
            id=id,
            client=client,
        )
    ).parsed
