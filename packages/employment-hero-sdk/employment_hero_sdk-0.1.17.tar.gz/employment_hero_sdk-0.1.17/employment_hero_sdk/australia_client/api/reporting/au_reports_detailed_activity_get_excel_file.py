import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_reports_detailed_activity_get_excel_file_request_filter_type import (
    AuReportsDetailedActivityGetExcelFileRequestFilterType,
)
from ...models.au_reports_detailed_activity_get_excel_file_request_group_by import (
    AuReportsDetailedActivityGetExcelFileRequestGroupBy,
)
from ...models.byte_array_content import ByteArrayContent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_group_by: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy] = UNSET,
    request_filter_type: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestFilterType] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_locations_ids: Union[Unset, List[int]] = UNSET,
    request_employee_ids: Union[Unset, List[int]] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_show_location_totals_only: Union[Unset, bool] = UNSET,
    request_include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_request_from_date: Union[Unset, str] = UNSET
    if not isinstance(request_from_date, Unset):
        json_request_from_date = request_from_date.isoformat()
    params["request.fromDate"] = json_request_from_date

    json_request_to_date: Union[Unset, str] = UNSET
    if not isinstance(request_to_date, Unset):
        json_request_to_date = request_to_date.isoformat()
    params["request.toDate"] = json_request_to_date

    json_request_group_by: Union[Unset, str] = UNSET
    if not isinstance(request_group_by, Unset):
        json_request_group_by = request_group_by.value

    params["request.groupBy"] = json_request_group_by

    json_request_filter_type: Union[Unset, str] = UNSET
    if not isinstance(request_filter_type, Unset):
        json_request_filter_type = request_filter_type.value

    params["request.filterType"] = json_request_filter_type

    params["request.payRunId"] = request_pay_run_id

    params["request.payScheduleId"] = request_pay_schedule_id

    json_request_locations_ids: Union[Unset, List[int]] = UNSET
    if not isinstance(request_locations_ids, Unset):
        json_request_locations_ids = request_locations_ids

    params["request.locationsIds"] = json_request_locations_ids

    json_request_employee_ids: Union[Unset, List[int]] = UNSET
    if not isinstance(request_employee_ids, Unset):
        json_request_employee_ids = request_employee_ids

    params["request.employeeIds"] = json_request_employee_ids

    params["request.includePostTaxDeductions"] = request_include_post_tax_deductions

    params["request.showLocationTotalsOnly"] = request_show_location_totals_only

    params["request.includeEmployeePayRunBreakdown"] = request_include_employee_pay_run_breakdown

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/detailedactivity/xlsx",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ByteArrayContent]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ByteArrayContent.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ByteArrayContent]:
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
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_group_by: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy] = UNSET,
    request_filter_type: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestFilterType] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_locations_ids: Union[Unset, List[int]] = UNSET,
    request_employee_ids: Union[Unset, List[int]] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_show_location_totals_only: Union[Unset, bool] = UNSET,
    request_include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Detailed Activity Report

     Generates a xlsx file fordetailed activity report.

    Args:
        business_id (str):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_group_by (Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy]):
        request_filter_type (Union[Unset,
            AuReportsDetailedActivityGetExcelFileRequestFilterType]):
        request_pay_run_id (Union[Unset, int]):
        request_pay_schedule_id (Union[Unset, int]):
        request_locations_ids (Union[Unset, List[int]]):
        request_employee_ids (Union[Unset, List[int]]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_show_location_totals_only (Union[Unset, bool]):
        request_include_employee_pay_run_breakdown (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_group_by=request_group_by,
        request_filter_type=request_filter_type,
        request_pay_run_id=request_pay_run_id,
        request_pay_schedule_id=request_pay_schedule_id,
        request_locations_ids=request_locations_ids,
        request_employee_ids=request_employee_ids,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_show_location_totals_only=request_show_location_totals_only,
        request_include_employee_pay_run_breakdown=request_include_employee_pay_run_breakdown,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_group_by: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy] = UNSET,
    request_filter_type: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestFilterType] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_locations_ids: Union[Unset, List[int]] = UNSET,
    request_employee_ids: Union[Unset, List[int]] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_show_location_totals_only: Union[Unset, bool] = UNSET,
    request_include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Detailed Activity Report

     Generates a xlsx file fordetailed activity report.

    Args:
        business_id (str):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_group_by (Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy]):
        request_filter_type (Union[Unset,
            AuReportsDetailedActivityGetExcelFileRequestFilterType]):
        request_pay_run_id (Union[Unset, int]):
        request_pay_schedule_id (Union[Unset, int]):
        request_locations_ids (Union[Unset, List[int]]):
        request_employee_ids (Union[Unset, List[int]]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_show_location_totals_only (Union[Unset, bool]):
        request_include_employee_pay_run_breakdown (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_group_by=request_group_by,
        request_filter_type=request_filter_type,
        request_pay_run_id=request_pay_run_id,
        request_pay_schedule_id=request_pay_schedule_id,
        request_locations_ids=request_locations_ids,
        request_employee_ids=request_employee_ids,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_show_location_totals_only=request_show_location_totals_only,
        request_include_employee_pay_run_breakdown=request_include_employee_pay_run_breakdown,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_group_by: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy] = UNSET,
    request_filter_type: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestFilterType] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_locations_ids: Union[Unset, List[int]] = UNSET,
    request_employee_ids: Union[Unset, List[int]] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_show_location_totals_only: Union[Unset, bool] = UNSET,
    request_include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Detailed Activity Report

     Generates a xlsx file fordetailed activity report.

    Args:
        business_id (str):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_group_by (Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy]):
        request_filter_type (Union[Unset,
            AuReportsDetailedActivityGetExcelFileRequestFilterType]):
        request_pay_run_id (Union[Unset, int]):
        request_pay_schedule_id (Union[Unset, int]):
        request_locations_ids (Union[Unset, List[int]]):
        request_employee_ids (Union[Unset, List[int]]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_show_location_totals_only (Union[Unset, bool]):
        request_include_employee_pay_run_breakdown (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_group_by=request_group_by,
        request_filter_type=request_filter_type,
        request_pay_run_id=request_pay_run_id,
        request_pay_schedule_id=request_pay_schedule_id,
        request_locations_ids=request_locations_ids,
        request_employee_ids=request_employee_ids,
        request_include_post_tax_deductions=request_include_post_tax_deductions,
        request_show_location_totals_only=request_show_location_totals_only,
        request_include_employee_pay_run_breakdown=request_include_employee_pay_run_breakdown,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_group_by: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy] = UNSET,
    request_filter_type: Union[Unset, AuReportsDetailedActivityGetExcelFileRequestFilterType] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_locations_ids: Union[Unset, List[int]] = UNSET,
    request_employee_ids: Union[Unset, List[int]] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_show_location_totals_only: Union[Unset, bool] = UNSET,
    request_include_employee_pay_run_breakdown: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Detailed Activity Report

     Generates a xlsx file fordetailed activity report.

    Args:
        business_id (str):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_group_by (Union[Unset, AuReportsDetailedActivityGetExcelFileRequestGroupBy]):
        request_filter_type (Union[Unset,
            AuReportsDetailedActivityGetExcelFileRequestFilterType]):
        request_pay_run_id (Union[Unset, int]):
        request_pay_schedule_id (Union[Unset, int]):
        request_locations_ids (Union[Unset, List[int]]):
        request_employee_ids (Union[Unset, List[int]]):
        request_include_post_tax_deductions (Union[Unset, bool]):
        request_show_location_totals_only (Union[Unset, bool]):
        request_include_employee_pay_run_breakdown (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_from_date=request_from_date,
            request_to_date=request_to_date,
            request_group_by=request_group_by,
            request_filter_type=request_filter_type,
            request_pay_run_id=request_pay_run_id,
            request_pay_schedule_id=request_pay_schedule_id,
            request_locations_ids=request_locations_ids,
            request_employee_ids=request_employee_ids,
            request_include_post_tax_deductions=request_include_post_tax_deductions,
            request_show_location_totals_only=request_show_location_totals_only,
            request_include_employee_pay_run_breakdown=request_include_employee_pay_run_breakdown,
        )
    ).parsed
