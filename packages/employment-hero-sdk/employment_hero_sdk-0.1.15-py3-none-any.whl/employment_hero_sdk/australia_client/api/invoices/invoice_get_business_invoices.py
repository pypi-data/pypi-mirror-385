import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.invoice_model import InvoiceModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: int,
    *,
    options_from_date: Union[Unset, datetime.datetime] = UNSET,
    options_to_date: Union[Unset, datetime.datetime] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_options_from_date: Union[Unset, str] = UNSET
    if not isinstance(options_from_date, Unset):
        json_options_from_date = options_from_date.isoformat()
    params["options.fromDate"] = json_options_from_date

    json_options_to_date: Union[Unset, str] = UNSET
    if not isinstance(options_to_date, Unset):
        json_options_to_date = options_to_date.isoformat()
    params["options.toDate"] = json_options_to_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/Invoice",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["InvoiceModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = InvoiceModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["InvoiceModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    options_from_date: Union[Unset, datetime.datetime] = UNSET,
    options_to_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["InvoiceModel"]]:
    """Get Business Invoices

     Get invoices for the specified Business.

    Args:
        business_id (int):
        options_from_date (Union[Unset, datetime.datetime]):
        options_to_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['InvoiceModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        options_from_date=options_from_date,
        options_to_date=options_to_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    options_from_date: Union[Unset, datetime.datetime] = UNSET,
    options_to_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["InvoiceModel"]]:
    """Get Business Invoices

     Get invoices for the specified Business.

    Args:
        business_id (int):
        options_from_date (Union[Unset, datetime.datetime]):
        options_to_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['InvoiceModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        options_from_date=options_from_date,
        options_to_date=options_to_date,
    ).parsed


async def asyncio_detailed(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    options_from_date: Union[Unset, datetime.datetime] = UNSET,
    options_to_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["InvoiceModel"]]:
    """Get Business Invoices

     Get invoices for the specified Business.

    Args:
        business_id (int):
        options_from_date (Union[Unset, datetime.datetime]):
        options_to_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['InvoiceModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        options_from_date=options_from_date,
        options_to_date=options_to_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    options_from_date: Union[Unset, datetime.datetime] = UNSET,
    options_to_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["InvoiceModel"]]:
    """Get Business Invoices

     Get invoices for the specified Business.

    Args:
        business_id (int):
        options_from_date (Union[Unset, datetime.datetime]):
        options_to_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['InvoiceModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            options_from_date=options_from_date,
            options_to_date=options_to_date,
        )
    ).parsed
