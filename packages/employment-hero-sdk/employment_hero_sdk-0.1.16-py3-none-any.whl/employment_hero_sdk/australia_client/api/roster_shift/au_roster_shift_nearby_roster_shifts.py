import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_ess_roster_shift_model import AuEssRosterShiftModel
from ...types import UNSET, Response


def _get_kwargs(
    business_id: str,
    employee_id: int,
    *,
    local_time: datetime.datetime,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_local_time = local_time.isoformat()
    params["localTime"] = json_local_time

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/rostershift/{employee_id}/nearby",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuEssRosterShiftModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuEssRosterShiftModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuEssRosterShiftModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    local_time: datetime.datetime,
) -> Response[List["AuEssRosterShiftModel"]]:
    """Find Nearby Roster Shifts

     Finds any of the employee's roster shifts that are nearby to the specified local time.

    Args:
        business_id (str):
        employee_id (int):
        local_time (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuEssRosterShiftModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        local_time=local_time,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    local_time: datetime.datetime,
) -> Optional[List["AuEssRosterShiftModel"]]:
    """Find Nearby Roster Shifts

     Finds any of the employee's roster shifts that are nearby to the specified local time.

    Args:
        business_id (str):
        employee_id (int):
        local_time (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuEssRosterShiftModel']
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        client=client,
        local_time=local_time,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    local_time: datetime.datetime,
) -> Response[List["AuEssRosterShiftModel"]]:
    """Find Nearby Roster Shifts

     Finds any of the employee's roster shifts that are nearby to the specified local time.

    Args:
        business_id (str):
        employee_id (int):
        local_time (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuEssRosterShiftModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        local_time=local_time,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    local_time: datetime.datetime,
) -> Optional[List["AuEssRosterShiftModel"]]:
    """Find Nearby Roster Shifts

     Finds any of the employee's roster shifts that are nearby to the specified local time.

    Args:
        business_id (str):
        employee_id (int):
        local_time (datetime.datetime):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuEssRosterShiftModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            client=client,
            local_time=local_time,
        )
    ).parsed
