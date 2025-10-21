from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.journal_account_bulk_create_model import JournalAccountBulkCreateModel
from ...models.journal_account_model import JournalAccountModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    *,
    body: Union[
        List["JournalAccountModel"],
        List["JournalAccountModel"],
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/accounts/bulk",
    }

    if isinstance(body, List["JournalAccountModel"]):
        _json_body = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _json_body.append(body_item)

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, List["JournalAccountModel"]):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[JournalAccountBulkCreateModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = JournalAccountBulkCreateModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[JournalAccountBulkCreateModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        List["JournalAccountModel"],
        List["JournalAccountModel"],
    ],
) -> Response[JournalAccountBulkCreateModel]:
    """Bulk insert Journal Accounts

     Create new journal accounts for the Business. This will not replace any existing journal accounts.

    Args:
        business_id (str):
        body (List['JournalAccountModel']):
        body (List['JournalAccountModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JournalAccountBulkCreateModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        List["JournalAccountModel"],
        List["JournalAccountModel"],
    ],
) -> Optional[JournalAccountBulkCreateModel]:
    """Bulk insert Journal Accounts

     Create new journal accounts for the Business. This will not replace any existing journal accounts.

    Args:
        business_id (str):
        body (List['JournalAccountModel']):
        body (List['JournalAccountModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JournalAccountBulkCreateModel
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        List["JournalAccountModel"],
        List["JournalAccountModel"],
    ],
) -> Response[JournalAccountBulkCreateModel]:
    """Bulk insert Journal Accounts

     Create new journal accounts for the Business. This will not replace any existing journal accounts.

    Args:
        business_id (str):
        body (List['JournalAccountModel']):
        body (List['JournalAccountModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JournalAccountBulkCreateModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        List["JournalAccountModel"],
        List["JournalAccountModel"],
    ],
) -> Optional[JournalAccountBulkCreateModel]:
    """Bulk insert Journal Accounts

     Create new journal accounts for the Business. This will not replace any existing journal accounts.

    Args:
        business_id (str):
        body (List['JournalAccountModel']):
        body (List['JournalAccountModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JournalAccountBulkCreateModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            body=body,
        )
    ).parsed
