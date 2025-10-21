import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_reports_roster_timesheet_comparison_get_roster_shift_status import (
    AuReportsRosterTimesheetComparisonGetRosterShiftStatus,
)
from ...models.au_reports_roster_timesheet_comparison_get_timesheet_line_status_type import (
    AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType,
)
from ...models.au_roster_timesheet_comparison_report_export_model import AuRosterTimesheetComparisonReportExportModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_employment_type_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_include_costs: Union[Unset, bool] = UNSET,
    request_timesheet_statuses: Union[
        Unset, List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]
    ] = UNSET,
    request_work_type_id: Union[Unset, int] = UNSET,
    request_roster_location_id: Union[Unset, int] = UNSET,
    request_timesheet_location_id: Union[Unset, int] = UNSET,
    request_roster_statuses: Union[Unset, List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.employmentTypeId"] = request_employment_type_id

    params["request.employeeId"] = request_employee_id

    params["request.includeCosts"] = request_include_costs

    json_request_timesheet_statuses: Union[Unset, List[str]] = UNSET
    if not isinstance(request_timesheet_statuses, Unset):
        json_request_timesheet_statuses = []
        for request_timesheet_statuses_item_data in request_timesheet_statuses:
            request_timesheet_statuses_item = request_timesheet_statuses_item_data.value
            json_request_timesheet_statuses.append(request_timesheet_statuses_item)

    params["request.timesheetStatuses"] = json_request_timesheet_statuses

    params["request.workTypeId"] = request_work_type_id

    params["request.rosterLocationId"] = request_roster_location_id

    params["request.timesheetLocationId"] = request_timesheet_location_id

    json_request_roster_statuses: Union[Unset, List[str]] = UNSET
    if not isinstance(request_roster_statuses, Unset):
        json_request_roster_statuses = []
        for request_roster_statuses_item_data in request_roster_statuses:
            request_roster_statuses_item = request_roster_statuses_item_data.value
            json_request_roster_statuses.append(request_roster_statuses_item)

    params["request.rosterStatuses"] = json_request_roster_statuses

    params["request.payScheduleId"] = request_pay_schedule_id

    params["request.includePostTaxDeductions"] = request_include_post_tax_deductions

    json_request_from_date: Union[Unset, str] = UNSET
    if not isinstance(request_from_date, Unset):
        json_request_from_date = request_from_date.isoformat()
    params["request.fromDate"] = json_request_from_date

    json_request_to_date: Union[Unset, str] = UNSET
    if not isinstance(request_to_date, Unset):
        json_request_to_date = request_to_date.isoformat()
    params["request.toDate"] = json_request_to_date

    params["request.locationId"] = request_location_id

    params["request.employingEntityId"] = request_employing_entity_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/rostertimesheetcomparison",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuRosterTimesheetComparisonReportExportModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuRosterTimesheetComparisonReportExportModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuRosterTimesheetComparisonReportExportModel"]]:
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
    request_employment_type_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_include_costs: Union[Unset, bool] = UNSET,
    request_timesheet_statuses: Union[
        Unset, List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]
    ] = UNSET,
    request_work_type_id: Union[Unset, int] = UNSET,
    request_roster_location_id: Union[Unset, int] = UNSET,
    request_timesheet_location_id: Union[Unset, int] = UNSET,
    request_roster_statuses: Union[Unset, List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["AuRosterTimesheetComparisonReportExportModel"]]:
    """Roster vs Timesheet Comparison Report

     Generates a roster vs timesheet comparison report.

    Args:
        business_id (str):
        request_employment_type_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_include_costs (Union[Unset, bool]):
        request_timesheet_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]]):
        request_work_type_id (Union[Unset, int]):
        request_roster_location_id (Union[Unset, int]):
        request_timesheet_location_id (Union[Unset, int]):
        request_roster_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]]):
        request_pay_schedule_id (Union[Unset, int]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_location_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuRosterTimesheetComparisonReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employment_type_id=request_employment_type_id,
        request_employee_id=request_employee_id,
        request_include_costs=request_include_costs,
        request_timesheet_statuses=request_timesheet_statuses,
        request_work_type_id=request_work_type_id,
        request_roster_location_id=request_roster_location_id,
        request_timesheet_location_id=request_timesheet_location_id,
        request_roster_statuses=request_roster_statuses,
        request_pay_schedule_id=request_pay_schedule_id,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_location_id=request_location_id,
        request_employing_entity_id=request_employing_entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_employment_type_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_include_costs: Union[Unset, bool] = UNSET,
    request_timesheet_statuses: Union[
        Unset, List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]
    ] = UNSET,
    request_work_type_id: Union[Unset, int] = UNSET,
    request_roster_location_id: Union[Unset, int] = UNSET,
    request_timesheet_location_id: Union[Unset, int] = UNSET,
    request_roster_statuses: Union[Unset, List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["AuRosterTimesheetComparisonReportExportModel"]]:
    """Roster vs Timesheet Comparison Report

     Generates a roster vs timesheet comparison report.

    Args:
        business_id (str):
        request_employment_type_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_include_costs (Union[Unset, bool]):
        request_timesheet_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]]):
        request_work_type_id (Union[Unset, int]):
        request_roster_location_id (Union[Unset, int]):
        request_timesheet_location_id (Union[Unset, int]):
        request_roster_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]]):
        request_pay_schedule_id (Union[Unset, int]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_location_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuRosterTimesheetComparisonReportExportModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_employment_type_id=request_employment_type_id,
        request_employee_id=request_employee_id,
        request_include_costs=request_include_costs,
        request_timesheet_statuses=request_timesheet_statuses,
        request_work_type_id=request_work_type_id,
        request_roster_location_id=request_roster_location_id,
        request_timesheet_location_id=request_timesheet_location_id,
        request_roster_statuses=request_roster_statuses,
        request_pay_schedule_id=request_pay_schedule_id,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_location_id=request_location_id,
        request_employing_entity_id=request_employing_entity_id,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_employment_type_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_include_costs: Union[Unset, bool] = UNSET,
    request_timesheet_statuses: Union[
        Unset, List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]
    ] = UNSET,
    request_work_type_id: Union[Unset, int] = UNSET,
    request_roster_location_id: Union[Unset, int] = UNSET,
    request_timesheet_location_id: Union[Unset, int] = UNSET,
    request_roster_statuses: Union[Unset, List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["AuRosterTimesheetComparisonReportExportModel"]]:
    """Roster vs Timesheet Comparison Report

     Generates a roster vs timesheet comparison report.

    Args:
        business_id (str):
        request_employment_type_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_include_costs (Union[Unset, bool]):
        request_timesheet_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]]):
        request_work_type_id (Union[Unset, int]):
        request_roster_location_id (Union[Unset, int]):
        request_timesheet_location_id (Union[Unset, int]):
        request_roster_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]]):
        request_pay_schedule_id (Union[Unset, int]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_location_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuRosterTimesheetComparisonReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employment_type_id=request_employment_type_id,
        request_employee_id=request_employee_id,
        request_include_costs=request_include_costs,
        request_timesheet_statuses=request_timesheet_statuses,
        request_work_type_id=request_work_type_id,
        request_roster_location_id=request_roster_location_id,
        request_timesheet_location_id=request_timesheet_location_id,
        request_roster_statuses=request_roster_statuses,
        request_pay_schedule_id=request_pay_schedule_id,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_location_id=request_location_id,
        request_employing_entity_id=request_employing_entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_employment_type_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_include_costs: Union[Unset, bool] = UNSET,
    request_timesheet_statuses: Union[
        Unset, List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]
    ] = UNSET,
    request_work_type_id: Union[Unset, int] = UNSET,
    request_roster_location_id: Union[Unset, int] = UNSET,
    request_timesheet_location_id: Union[Unset, int] = UNSET,
    request_roster_statuses: Union[Unset, List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["AuRosterTimesheetComparisonReportExportModel"]]:
    """Roster vs Timesheet Comparison Report

     Generates a roster vs timesheet comparison report.

    Args:
        business_id (str):
        request_employment_type_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_include_costs (Union[Unset, bool]):
        request_timesheet_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetTimesheetLineStatusType]]):
        request_work_type_id (Union[Unset, int]):
        request_roster_location_id (Union[Unset, int]):
        request_timesheet_location_id (Union[Unset, int]):
        request_roster_statuses (Union[Unset,
            List[AuReportsRosterTimesheetComparisonGetRosterShiftStatus]]):
        request_pay_schedule_id (Union[Unset, int]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_location_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuRosterTimesheetComparisonReportExportModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_employment_type_id=request_employment_type_id,
            request_employee_id=request_employee_id,
            request_include_costs=request_include_costs,
            request_timesheet_statuses=request_timesheet_statuses,
            request_work_type_id=request_work_type_id,
            request_roster_location_id=request_roster_location_id,
            request_timesheet_location_id=request_timesheet_location_id,
            request_roster_statuses=request_roster_statuses,
            request_pay_schedule_id=request_pay_schedule_id,
            request_include_post_tax_deductions=request_include_post_tax_deductions,
            request_from_date=request_from_date,
            request_to_date=request_to_date,
            request_location_id=request_location_id,
            request_employing_entity_id=request_employing_entity_id,
        )
    ).parsed
