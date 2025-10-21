from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generic_time_and_attendance_get_shift_notes_model_type import (
    GenericTimeAndAttendanceGetShiftNotesModelType,
)
from ...models.generic_time_and_attendance_get_shift_notes_model_visibility import (
    GenericTimeAndAttendanceGetShiftNotesModelVisibility,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    kiosk_id: int,
    shift_id: int,
    *,
    model_employee_id: Union[Unset, int] = UNSET,
    model_is_admin_initiated: Union[Unset, bool] = UNSET,
    model_type: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelType] = UNSET,
    model_visibility: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelVisibility] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["model.employeeId"] = model_employee_id

    params["model.isAdminInitiated"] = model_is_admin_initiated

    json_model_type: Union[Unset, str] = UNSET
    if not isinstance(model_type, Unset):
        json_model_type = model_type.value

    params["model.type"] = json_model_type

    json_model_visibility: Union[Unset, str] = UNSET
    if not isinstance(model_visibility, Unset):
        json_model_visibility = model_visibility.value

    params["model.visibility"] = json_model_visibility

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/kiosk/{kiosk_id}/shift/{shift_id}/notes",
        "params": params,
    }

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
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    model_employee_id: Union[Unset, int] = UNSET,
    model_is_admin_initiated: Union[Unset, bool] = UNSET,
    model_type: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelType] = UNSET,
    model_visibility: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelVisibility] = UNSET,
) -> Response[Any]:
    """Get Shift Notes

     Gets all the notes for a specific shift.

    Args:
        business_id (str):
        kiosk_id (int):
        shift_id (int):
        model_employee_id (Union[Unset, int]):
        model_is_admin_initiated (Union[Unset, bool]):
        model_type (Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelType]):
        model_visibility (Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelVisibility]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        shift_id=shift_id,
        model_employee_id=model_employee_id,
        model_is_admin_initiated=model_is_admin_initiated,
        model_type=model_type,
        model_visibility=model_visibility,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    business_id: str,
    kiosk_id: int,
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    model_employee_id: Union[Unset, int] = UNSET,
    model_is_admin_initiated: Union[Unset, bool] = UNSET,
    model_type: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelType] = UNSET,
    model_visibility: Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelVisibility] = UNSET,
) -> Response[Any]:
    """Get Shift Notes

     Gets all the notes for a specific shift.

    Args:
        business_id (str):
        kiosk_id (int):
        shift_id (int):
        model_employee_id (Union[Unset, int]):
        model_is_admin_initiated (Union[Unset, bool]):
        model_type (Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelType]):
        model_visibility (Union[Unset, GenericTimeAndAttendanceGetShiftNotesModelVisibility]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        shift_id=shift_id,
        model_employee_id=model_employee_id,
        model_is_admin_initiated=model_is_admin_initiated,
        model_type=model_type,
        model_visibility=model_visibility,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
