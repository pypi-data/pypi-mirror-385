import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_reports_super_contributions_get_excel_report_request_contribution_type import (
    AuReportsSuperContributionsGetExcelReportRequestContributionType,
)
from ...models.au_reports_super_contributions_get_excel_report_request_filter_type import (
    AuReportsSuperContributionsGetExcelReportRequestFilterType,
)
from ...models.au_reports_super_contributions_get_excel_report_request_group_by import (
    AuReportsSuperContributionsGetExcelReportRequestGroupBy,
)
from ...models.au_reports_super_contributions_get_excel_report_request_super_contributions_report_export_type import (
    AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType,
)
from ...models.byte_array_content import ByteArrayContent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_super_contributions_report_export_type: Union[
        Unset, AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType
    ] = UNSET,
    request_filter_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestFilterType] = UNSET,
    request_super_batch_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_contribution_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestContributionType] = UNSET,
    request_group_by: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy] = UNSET,
    request_fund_per_page: Union[Unset, bool] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_request_super_contributions_report_export_type: Union[Unset, str] = UNSET
    if not isinstance(request_super_contributions_report_export_type, Unset):
        json_request_super_contributions_report_export_type = request_super_contributions_report_export_type.value

    params["request.superContributionsReportExportType"] = json_request_super_contributions_report_export_type

    json_request_filter_type: Union[Unset, str] = UNSET
    if not isinstance(request_filter_type, Unset):
        json_request_filter_type = request_filter_type.value

    params["request.filterType"] = json_request_filter_type

    params["request.superBatchId"] = request_super_batch_id

    params["request.employeeId"] = request_employee_id

    json_request_contribution_type: Union[Unset, str] = UNSET
    if not isinstance(request_contribution_type, Unset):
        json_request_contribution_type = request_contribution_type.value

    params["request.contributionType"] = json_request_contribution_type

    json_request_group_by: Union[Unset, str] = UNSET
    if not isinstance(request_group_by, Unset):
        json_request_group_by = request_group_by.value

    params["request.groupBy"] = json_request_group_by

    params["request.fundPerPage"] = request_fund_per_page

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
        "url": f"/api/v2/business/{business_id}/report/supercontributions/xlsx",
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
    request_super_contributions_report_export_type: Union[
        Unset, AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType
    ] = UNSET,
    request_filter_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestFilterType] = UNSET,
    request_super_batch_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_contribution_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestContributionType] = UNSET,
    request_group_by: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy] = UNSET,
    request_fund_per_page: Union[Unset, bool] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[ByteArrayContent]:
    """Super Contribution Report as Excel

     Generates a Super Contribution Report as an Excel file.

    Args:
        business_id (str):
        request_super_contributions_report_export_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType]):
        request_filter_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestFilterType]):
        request_super_batch_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_contribution_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestContributionType]):
        request_group_by (Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy]):
        request_fund_per_page (Union[Unset, bool]):
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
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_super_contributions_report_export_type=request_super_contributions_report_export_type,
        request_filter_type=request_filter_type,
        request_super_batch_id=request_super_batch_id,
        request_employee_id=request_employee_id,
        request_contribution_type=request_contribution_type,
        request_group_by=request_group_by,
        request_fund_per_page=request_fund_per_page,
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
    request_super_contributions_report_export_type: Union[
        Unset, AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType
    ] = UNSET,
    request_filter_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestFilterType] = UNSET,
    request_super_batch_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_contribution_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestContributionType] = UNSET,
    request_group_by: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy] = UNSET,
    request_fund_per_page: Union[Unset, bool] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[ByteArrayContent]:
    """Super Contribution Report as Excel

     Generates a Super Contribution Report as an Excel file.

    Args:
        business_id (str):
        request_super_contributions_report_export_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType]):
        request_filter_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestFilterType]):
        request_super_batch_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_contribution_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestContributionType]):
        request_group_by (Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy]):
        request_fund_per_page (Union[Unset, bool]):
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
        ByteArrayContent
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_super_contributions_report_export_type=request_super_contributions_report_export_type,
        request_filter_type=request_filter_type,
        request_super_batch_id=request_super_batch_id,
        request_employee_id=request_employee_id,
        request_contribution_type=request_contribution_type,
        request_group_by=request_group_by,
        request_fund_per_page=request_fund_per_page,
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
    request_super_contributions_report_export_type: Union[
        Unset, AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType
    ] = UNSET,
    request_filter_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestFilterType] = UNSET,
    request_super_batch_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_contribution_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestContributionType] = UNSET,
    request_group_by: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy] = UNSET,
    request_fund_per_page: Union[Unset, bool] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[ByteArrayContent]:
    """Super Contribution Report as Excel

     Generates a Super Contribution Report as an Excel file.

    Args:
        business_id (str):
        request_super_contributions_report_export_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType]):
        request_filter_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestFilterType]):
        request_super_batch_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_contribution_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestContributionType]):
        request_group_by (Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy]):
        request_fund_per_page (Union[Unset, bool]):
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
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_super_contributions_report_export_type=request_super_contributions_report_export_type,
        request_filter_type=request_filter_type,
        request_super_batch_id=request_super_batch_id,
        request_employee_id=request_employee_id,
        request_contribution_type=request_contribution_type,
        request_group_by=request_group_by,
        request_fund_per_page=request_fund_per_page,
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
    request_super_contributions_report_export_type: Union[
        Unset, AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType
    ] = UNSET,
    request_filter_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestFilterType] = UNSET,
    request_super_batch_id: Union[Unset, int] = UNSET,
    request_employee_id: Union[Unset, int] = UNSET,
    request_contribution_type: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestContributionType] = UNSET,
    request_group_by: Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy] = UNSET,
    request_fund_per_page: Union[Unset, bool] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[ByteArrayContent]:
    """Super Contribution Report as Excel

     Generates a Super Contribution Report as an Excel file.

    Args:
        business_id (str):
        request_super_contributions_report_export_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestSuperContributionsReportExportType]):
        request_filter_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestFilterType]):
        request_super_batch_id (Union[Unset, int]):
        request_employee_id (Union[Unset, int]):
        request_contribution_type (Union[Unset,
            AuReportsSuperContributionsGetExcelReportRequestContributionType]):
        request_group_by (Union[Unset, AuReportsSuperContributionsGetExcelReportRequestGroupBy]):
        request_fund_per_page (Union[Unset, bool]):
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
        ByteArrayContent
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_super_contributions_report_export_type=request_super_contributions_report_export_type,
            request_filter_type=request_filter_type,
            request_super_batch_id=request_super_batch_id,
            request_employee_id=request_employee_id,
            request_contribution_type=request_contribution_type,
            request_group_by=request_group_by,
            request_fund_per_page=request_fund_per_page,
            request_pay_schedule_id=request_pay_schedule_id,
            request_include_post_tax_deductions=request_include_post_tax_deductions,
            request_from_date=request_from_date,
            request_to_date=request_to_date,
            request_location_id=request_location_id,
            request_employing_entity_id=request_employing_entity_id,
        )
    ).parsed
