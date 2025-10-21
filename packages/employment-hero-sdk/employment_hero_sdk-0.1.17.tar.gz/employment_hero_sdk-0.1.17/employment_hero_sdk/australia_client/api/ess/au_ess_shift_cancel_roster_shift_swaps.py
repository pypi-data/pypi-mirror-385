from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_ess_bulk_roster_shift_action_response import AuEssBulkRosterShiftActionResponse
from ...models.ess_bulk_roster_shift_swap_model import EssBulkRosterShiftSwapModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
    *,
    body: Union[
        EssBulkRosterShiftSwapModel,
        EssBulkRosterShiftSwapModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/ess/{employee_id}/shift/swap/cancel",
    }

    if isinstance(body, EssBulkRosterShiftSwapModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, EssBulkRosterShiftSwapModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuEssBulkRosterShiftActionResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuEssBulkRosterShiftActionResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuEssBulkRosterShiftActionResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EssBulkRosterShiftSwapModel,
        EssBulkRosterShiftSwapModel,
    ],
) -> Response[AuEssBulkRosterShiftActionResponse]:
    """Bulk Cancel Roster Shift Swaps

     Cancels a number of roster shift swaps by shift ID.

    Args:
        employee_id (str):
        body (EssBulkRosterShiftSwapModel):
        body (EssBulkRosterShiftSwapModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuEssBulkRosterShiftActionResponse]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EssBulkRosterShiftSwapModel,
        EssBulkRosterShiftSwapModel,
    ],
) -> Optional[AuEssBulkRosterShiftActionResponse]:
    """Bulk Cancel Roster Shift Swaps

     Cancels a number of roster shift swaps by shift ID.

    Args:
        employee_id (str):
        body (EssBulkRosterShiftSwapModel):
        body (EssBulkRosterShiftSwapModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuEssBulkRosterShiftActionResponse
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EssBulkRosterShiftSwapModel,
        EssBulkRosterShiftSwapModel,
    ],
) -> Response[AuEssBulkRosterShiftActionResponse]:
    """Bulk Cancel Roster Shift Swaps

     Cancels a number of roster shift swaps by shift ID.

    Args:
        employee_id (str):
        body (EssBulkRosterShiftSwapModel):
        body (EssBulkRosterShiftSwapModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuEssBulkRosterShiftActionResponse]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EssBulkRosterShiftSwapModel,
        EssBulkRosterShiftSwapModel,
    ],
) -> Optional[AuEssBulkRosterShiftActionResponse]:
    """Bulk Cancel Roster Shift Swaps

     Cancels a number of roster shift swaps by shift ID.

    Args:
        employee_id (str):
        body (EssBulkRosterShiftSwapModel):
        body (EssBulkRosterShiftSwapModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuEssBulkRosterShiftActionResponse
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
