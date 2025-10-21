import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_roster_shift_generate_timesheet_model import AuRosterShiftGenerateTimesheetModel
from ...models.au_roster_shift_get_filter_shift_status import AuRosterShiftGetFilterShiftStatus
from ...models.au_roster_shift_get_roster_shift_status import AuRosterShiftGetRosterShiftStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_shift_status: Union[Unset, AuRosterShiftGetFilterShiftStatus] = UNSET,
    filter_shift_statuses: Union[Unset, List[AuRosterShiftGetRosterShiftStatus]] = UNSET,
    filter_selected_locations: Union[Unset, List[str]] = UNSET,
    filter_selected_employees: Union[Unset, List[str]] = UNSET,
    filter_selected_roles: Union[Unset, List[str]] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_unassigned_shifts_only: Union[Unset, bool] = UNSET,
    filter_select_all_roles: Union[Unset, bool] = UNSET,
    filter_exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_include_warnings: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_from_date: Union[Unset, str] = UNSET
    if not isinstance(filter_from_date, Unset):
        json_filter_from_date = filter_from_date.isoformat()
    params["filter.fromDate"] = json_filter_from_date

    json_filter_to_date: Union[Unset, str] = UNSET
    if not isinstance(filter_to_date, Unset):
        json_filter_to_date = filter_to_date.isoformat()
    params["filter.toDate"] = json_filter_to_date

    json_filter_shift_status: Union[Unset, str] = UNSET
    if not isinstance(filter_shift_status, Unset):
        json_filter_shift_status = filter_shift_status.value

    params["filter.shiftStatus"] = json_filter_shift_status

    json_filter_shift_statuses: Union[Unset, List[str]] = UNSET
    if not isinstance(filter_shift_statuses, Unset):
        json_filter_shift_statuses = []
        for filter_shift_statuses_item_data in filter_shift_statuses:
            filter_shift_statuses_item = filter_shift_statuses_item_data.value
            json_filter_shift_statuses.append(filter_shift_statuses_item)

    params["filter.shiftStatuses"] = json_filter_shift_statuses

    json_filter_selected_locations: Union[Unset, List[str]] = UNSET
    if not isinstance(filter_selected_locations, Unset):
        json_filter_selected_locations = filter_selected_locations

    params["filter.selectedLocations"] = json_filter_selected_locations

    json_filter_selected_employees: Union[Unset, List[str]] = UNSET
    if not isinstance(filter_selected_employees, Unset):
        json_filter_selected_employees = filter_selected_employees

    params["filter.selectedEmployees"] = json_filter_selected_employees

    json_filter_selected_roles: Union[Unset, List[str]] = UNSET
    if not isinstance(filter_selected_roles, Unset):
        json_filter_selected_roles = filter_selected_roles

    params["filter.selectedRoles"] = json_filter_selected_roles

    params["filter.employeeId"] = filter_employee_id

    params["filter.locationId"] = filter_location_id

    params["filter.employeeGroupId"] = filter_employee_group_id

    params["filter.unassignedShiftsOnly"] = filter_unassigned_shifts_only

    params["filter.selectAllRoles"] = filter_select_all_roles

    params["filter.excludeShiftsOverlappingFromDate"] = filter_exclude_shifts_overlapping_from_date

    params["filter.pageSize"] = filter_page_size

    params["filter.currentPage"] = filter_current_page

    params["filter.includeWarnings"] = filter_include_warnings

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/rostershift",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuRosterShiftGenerateTimesheetModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuRosterShiftGenerateTimesheetModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuRosterShiftGenerateTimesheetModel"]]:
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
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_shift_status: Union[Unset, AuRosterShiftGetFilterShiftStatus] = UNSET,
    filter_shift_statuses: Union[Unset, List[AuRosterShiftGetRosterShiftStatus]] = UNSET,
    filter_selected_locations: Union[Unset, List[str]] = UNSET,
    filter_selected_employees: Union[Unset, List[str]] = UNSET,
    filter_selected_roles: Union[Unset, List[str]] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_unassigned_shifts_only: Union[Unset, bool] = UNSET,
    filter_select_all_roles: Union[Unset, bool] = UNSET,
    filter_exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_include_warnings: Union[Unset, bool] = UNSET,
) -> Response[List["AuRosterShiftGenerateTimesheetModel"]]:
    """Get Roster Shifts

     Gets roster shifts, optionally filtered by a number of parameters. Query parameters 'fromDate' and
    'toDate' are required.
    NOTE: By default, only shifts with no role assigned are returned. To return shifts with roles,
    either specify some SelectedRoles,
    or specify SelectAllRoles = true.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_shift_status (Union[Unset, AuRosterShiftGetFilterShiftStatus]):
        filter_shift_statuses (Union[Unset, List[AuRosterShiftGetRosterShiftStatus]]):
        filter_selected_locations (Union[Unset, List[str]]):
        filter_selected_employees (Union[Unset, List[str]]):
        filter_selected_roles (Union[Unset, List[str]]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_unassigned_shifts_only (Union[Unset, bool]):
        filter_select_all_roles (Union[Unset, bool]):
        filter_exclude_shifts_overlapping_from_date (Union[Unset, bool]):
        filter_page_size (Union[Unset, int]):
        filter_current_page (Union[Unset, int]):
        filter_include_warnings (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuRosterShiftGenerateTimesheetModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_shift_status=filter_shift_status,
        filter_shift_statuses=filter_shift_statuses,
        filter_selected_locations=filter_selected_locations,
        filter_selected_employees=filter_selected_employees,
        filter_selected_roles=filter_selected_roles,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_unassigned_shifts_only=filter_unassigned_shifts_only,
        filter_select_all_roles=filter_select_all_roles,
        filter_exclude_shifts_overlapping_from_date=filter_exclude_shifts_overlapping_from_date,
        filter_page_size=filter_page_size,
        filter_current_page=filter_current_page,
        filter_include_warnings=filter_include_warnings,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_shift_status: Union[Unset, AuRosterShiftGetFilterShiftStatus] = UNSET,
    filter_shift_statuses: Union[Unset, List[AuRosterShiftGetRosterShiftStatus]] = UNSET,
    filter_selected_locations: Union[Unset, List[str]] = UNSET,
    filter_selected_employees: Union[Unset, List[str]] = UNSET,
    filter_selected_roles: Union[Unset, List[str]] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_unassigned_shifts_only: Union[Unset, bool] = UNSET,
    filter_select_all_roles: Union[Unset, bool] = UNSET,
    filter_exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_include_warnings: Union[Unset, bool] = UNSET,
) -> Optional[List["AuRosterShiftGenerateTimesheetModel"]]:
    """Get Roster Shifts

     Gets roster shifts, optionally filtered by a number of parameters. Query parameters 'fromDate' and
    'toDate' are required.
    NOTE: By default, only shifts with no role assigned are returned. To return shifts with roles,
    either specify some SelectedRoles,
    or specify SelectAllRoles = true.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_shift_status (Union[Unset, AuRosterShiftGetFilterShiftStatus]):
        filter_shift_statuses (Union[Unset, List[AuRosterShiftGetRosterShiftStatus]]):
        filter_selected_locations (Union[Unset, List[str]]):
        filter_selected_employees (Union[Unset, List[str]]):
        filter_selected_roles (Union[Unset, List[str]]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_unassigned_shifts_only (Union[Unset, bool]):
        filter_select_all_roles (Union[Unset, bool]):
        filter_exclude_shifts_overlapping_from_date (Union[Unset, bool]):
        filter_page_size (Union[Unset, int]):
        filter_current_page (Union[Unset, int]):
        filter_include_warnings (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuRosterShiftGenerateTimesheetModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_shift_status=filter_shift_status,
        filter_shift_statuses=filter_shift_statuses,
        filter_selected_locations=filter_selected_locations,
        filter_selected_employees=filter_selected_employees,
        filter_selected_roles=filter_selected_roles,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_unassigned_shifts_only=filter_unassigned_shifts_only,
        filter_select_all_roles=filter_select_all_roles,
        filter_exclude_shifts_overlapping_from_date=filter_exclude_shifts_overlapping_from_date,
        filter_page_size=filter_page_size,
        filter_current_page=filter_current_page,
        filter_include_warnings=filter_include_warnings,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_shift_status: Union[Unset, AuRosterShiftGetFilterShiftStatus] = UNSET,
    filter_shift_statuses: Union[Unset, List[AuRosterShiftGetRosterShiftStatus]] = UNSET,
    filter_selected_locations: Union[Unset, List[str]] = UNSET,
    filter_selected_employees: Union[Unset, List[str]] = UNSET,
    filter_selected_roles: Union[Unset, List[str]] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_unassigned_shifts_only: Union[Unset, bool] = UNSET,
    filter_select_all_roles: Union[Unset, bool] = UNSET,
    filter_exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_include_warnings: Union[Unset, bool] = UNSET,
) -> Response[List["AuRosterShiftGenerateTimesheetModel"]]:
    """Get Roster Shifts

     Gets roster shifts, optionally filtered by a number of parameters. Query parameters 'fromDate' and
    'toDate' are required.
    NOTE: By default, only shifts with no role assigned are returned. To return shifts with roles,
    either specify some SelectedRoles,
    or specify SelectAllRoles = true.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_shift_status (Union[Unset, AuRosterShiftGetFilterShiftStatus]):
        filter_shift_statuses (Union[Unset, List[AuRosterShiftGetRosterShiftStatus]]):
        filter_selected_locations (Union[Unset, List[str]]):
        filter_selected_employees (Union[Unset, List[str]]):
        filter_selected_roles (Union[Unset, List[str]]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_unassigned_shifts_only (Union[Unset, bool]):
        filter_select_all_roles (Union[Unset, bool]):
        filter_exclude_shifts_overlapping_from_date (Union[Unset, bool]):
        filter_page_size (Union[Unset, int]):
        filter_current_page (Union[Unset, int]):
        filter_include_warnings (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuRosterShiftGenerateTimesheetModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_shift_status=filter_shift_status,
        filter_shift_statuses=filter_shift_statuses,
        filter_selected_locations=filter_selected_locations,
        filter_selected_employees=filter_selected_employees,
        filter_selected_roles=filter_selected_roles,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_unassigned_shifts_only=filter_unassigned_shifts_only,
        filter_select_all_roles=filter_select_all_roles,
        filter_exclude_shifts_overlapping_from_date=filter_exclude_shifts_overlapping_from_date,
        filter_page_size=filter_page_size,
        filter_current_page=filter_current_page,
        filter_include_warnings=filter_include_warnings,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_shift_status: Union[Unset, AuRosterShiftGetFilterShiftStatus] = UNSET,
    filter_shift_statuses: Union[Unset, List[AuRosterShiftGetRosterShiftStatus]] = UNSET,
    filter_selected_locations: Union[Unset, List[str]] = UNSET,
    filter_selected_employees: Union[Unset, List[str]] = UNSET,
    filter_selected_roles: Union[Unset, List[str]] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_unassigned_shifts_only: Union[Unset, bool] = UNSET,
    filter_select_all_roles: Union[Unset, bool] = UNSET,
    filter_exclude_shifts_overlapping_from_date: Union[Unset, bool] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_include_warnings: Union[Unset, bool] = UNSET,
) -> Optional[List["AuRosterShiftGenerateTimesheetModel"]]:
    """Get Roster Shifts

     Gets roster shifts, optionally filtered by a number of parameters. Query parameters 'fromDate' and
    'toDate' are required.
    NOTE: By default, only shifts with no role assigned are returned. To return shifts with roles,
    either specify some SelectedRoles,
    or specify SelectAllRoles = true.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_shift_status (Union[Unset, AuRosterShiftGetFilterShiftStatus]):
        filter_shift_statuses (Union[Unset, List[AuRosterShiftGetRosterShiftStatus]]):
        filter_selected_locations (Union[Unset, List[str]]):
        filter_selected_employees (Union[Unset, List[str]]):
        filter_selected_roles (Union[Unset, List[str]]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_unassigned_shifts_only (Union[Unset, bool]):
        filter_select_all_roles (Union[Unset, bool]):
        filter_exclude_shifts_overlapping_from_date (Union[Unset, bool]):
        filter_page_size (Union[Unset, int]):
        filter_current_page (Union[Unset, int]):
        filter_include_warnings (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuRosterShiftGenerateTimesheetModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_from_date=filter_from_date,
            filter_to_date=filter_to_date,
            filter_shift_status=filter_shift_status,
            filter_shift_statuses=filter_shift_statuses,
            filter_selected_locations=filter_selected_locations,
            filter_selected_employees=filter_selected_employees,
            filter_selected_roles=filter_selected_roles,
            filter_employee_id=filter_employee_id,
            filter_location_id=filter_location_id,
            filter_employee_group_id=filter_employee_group_id,
            filter_unassigned_shifts_only=filter_unassigned_shifts_only,
            filter_select_all_roles=filter_select_all_roles,
            filter_exclude_shifts_overlapping_from_date=filter_exclude_shifts_overlapping_from_date,
            filter_page_size=filter_page_size,
            filter_current_page=filter_current_page,
            filter_include_warnings=filter_include_warnings,
        )
    ).parsed
