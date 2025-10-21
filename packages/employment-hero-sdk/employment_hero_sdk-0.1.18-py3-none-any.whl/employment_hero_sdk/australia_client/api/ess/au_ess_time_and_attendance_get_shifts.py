from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_time_and_attendance_shift_model import AuTimeAndAttendanceShiftModel
from ...models.get_shifts_model import GetShiftsModel
from ...types import Response


def _get_kwargs(
    employee_id: int,
    *,
    body: Union[
        GetShiftsModel,
        GetShiftsModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/ess/{employee_id}/timeandattendance/shifts",
    }

    if isinstance(body, GetShiftsModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, GetShiftsModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuTimeAndAttendanceShiftModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuTimeAndAttendanceShiftModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuTimeAndAttendanceShiftModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftsModel,
        GetShiftsModel,
    ],
) -> Response[List["AuTimeAndAttendanceShiftModel"]]:
    """Shifts

     Gets shifts based on certain optional criteria.

    Args:
        employee_id (int):
        body (GetShiftsModel):
        body (GetShiftsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuTimeAndAttendanceShiftModel']]
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
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftsModel,
        GetShiftsModel,
    ],
) -> Optional[List["AuTimeAndAttendanceShiftModel"]]:
    """Shifts

     Gets shifts based on certain optional criteria.

    Args:
        employee_id (int):
        body (GetShiftsModel):
        body (GetShiftsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuTimeAndAttendanceShiftModel']
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftsModel,
        GetShiftsModel,
    ],
) -> Response[List["AuTimeAndAttendanceShiftModel"]]:
    """Shifts

     Gets shifts based on certain optional criteria.

    Args:
        employee_id (int):
        body (GetShiftsModel):
        body (GetShiftsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuTimeAndAttendanceShiftModel']]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftsModel,
        GetShiftsModel,
    ],
) -> Optional[List["AuTimeAndAttendanceShiftModel"]]:
    """Shifts

     Gets shifts based on certain optional criteria.

    Args:
        employee_id (int):
        body (GetShiftsModel):
        body (GetShiftsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuTimeAndAttendanceShiftModel']
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
