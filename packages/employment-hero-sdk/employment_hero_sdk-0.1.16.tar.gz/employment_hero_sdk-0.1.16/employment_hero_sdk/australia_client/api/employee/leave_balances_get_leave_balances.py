import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.leave_balance_model import LeaveBalanceModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    employee_id: str,
    *,
    as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_as_at_date: Union[Unset, str] = UNSET
    if not isinstance(as_at_date, Unset):
        json_as_at_date = as_at_date.isoformat()
    params["asAtDate"] = json_as_at_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/leavebalances",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["LeaveBalanceModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LeaveBalanceModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["LeaveBalanceModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["LeaveBalanceModel"]]:
    """Get Leave Balances

     Gets leave balances for this employee.

    Args:
        business_id (str):
        employee_id (str):
        as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LeaveBalanceModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        as_at_date=as_at_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["LeaveBalanceModel"]]:
    """Get Leave Balances

     Gets leave balances for this employee.

    Args:
        business_id (str):
        employee_id (str):
        as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LeaveBalanceModel']
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        client=client,
        as_at_date=as_at_date,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["LeaveBalanceModel"]]:
    """Get Leave Balances

     Gets leave balances for this employee.

    Args:
        business_id (str):
        employee_id (str):
        as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LeaveBalanceModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        as_at_date=as_at_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["LeaveBalanceModel"]]:
    """Get Leave Balances

     Gets leave balances for this employee.

    Args:
        business_id (str):
        employee_id (str):
        as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LeaveBalanceModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            client=client,
            as_at_date=as_at_date,
        )
    ).parsed
