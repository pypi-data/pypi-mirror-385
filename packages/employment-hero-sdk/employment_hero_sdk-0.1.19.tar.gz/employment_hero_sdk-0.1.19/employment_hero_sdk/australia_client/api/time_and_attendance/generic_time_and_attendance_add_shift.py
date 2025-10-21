from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_add_shift_model import AuAddShiftModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    kiosk_id: int,
    *,
    body: Union[
        AuAddShiftModel,
        AuAddShiftModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/kiosk/{kiosk_id}/addshift",
    }

    if isinstance(body, AuAddShiftModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, AuAddShiftModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuAddShiftModel,
        AuAddShiftModel,
    ],
) -> Response[Any]:
    """Add Complete Shift for Employee

     Clocks in / out an employee for a complete shift.

    Args:
        business_id (str):
        kiosk_id (int):
        body (AuAddShiftModel):
        body (AuAddShiftModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuAddShiftModel,
        AuAddShiftModel,
    ],
) -> Response[Any]:
    """Add Complete Shift for Employee

     Clocks in / out an employee for a complete shift.

    Args:
        business_id (str):
        kiosk_id (int):
        body (AuAddShiftModel):
        body (AuAddShiftModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
