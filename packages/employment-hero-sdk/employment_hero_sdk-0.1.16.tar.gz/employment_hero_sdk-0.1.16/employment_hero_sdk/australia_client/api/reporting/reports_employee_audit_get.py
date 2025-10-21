import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employee_details_audit_report_api_model import EmployeeDetailsAuditReportApiModel
from ...models.reports_employee_audit_get_request_section import ReportsEmployeeAuditGetRequestSection
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_employee_id: Union[Unset, int] = UNSET,
    request_section: Union[Unset, ReportsEmployeeAuditGetRequestSection] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.employeeId"] = request_employee_id

    json_request_section: Union[Unset, str] = UNSET
    if not isinstance(request_section, Unset):
        json_request_section = request_section.value

    params["request.section"] = json_request_section

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
        "url": f"/api/v2/business/{business_id}/report/employeeaudit",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["EmployeeDetailsAuditReportApiModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EmployeeDetailsAuditReportApiModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["EmployeeDetailsAuditReportApiModel"]]:
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
    request_employee_id: Union[Unset, int] = UNSET,
    request_section: Union[Unset, ReportsEmployeeAuditGetRequestSection] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["EmployeeDetailsAuditReportApiModel"]]:
    """Employee Audit Report

     Generates an Employee Audit Report.

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_section (Union[Unset, ReportsEmployeeAuditGetRequestSection]):
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
        Response[List['EmployeeDetailsAuditReportApiModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employee_id=request_employee_id,
        request_section=request_section,
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
    request_employee_id: Union[Unset, int] = UNSET,
    request_section: Union[Unset, ReportsEmployeeAuditGetRequestSection] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["EmployeeDetailsAuditReportApiModel"]]:
    """Employee Audit Report

     Generates an Employee Audit Report.

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_section (Union[Unset, ReportsEmployeeAuditGetRequestSection]):
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
        List['EmployeeDetailsAuditReportApiModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_employee_id=request_employee_id,
        request_section=request_section,
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
    request_employee_id: Union[Unset, int] = UNSET,
    request_section: Union[Unset, ReportsEmployeeAuditGetRequestSection] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["EmployeeDetailsAuditReportApiModel"]]:
    """Employee Audit Report

     Generates an Employee Audit Report.

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_section (Union[Unset, ReportsEmployeeAuditGetRequestSection]):
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
        Response[List['EmployeeDetailsAuditReportApiModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employee_id=request_employee_id,
        request_section=request_section,
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
    request_employee_id: Union[Unset, int] = UNSET,
    request_section: Union[Unset, ReportsEmployeeAuditGetRequestSection] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_include_post_tax_deductions: Union[Unset, bool] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["EmployeeDetailsAuditReportApiModel"]]:
    """Employee Audit Report

     Generates an Employee Audit Report.

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_section (Union[Unset, ReportsEmployeeAuditGetRequestSection]):
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
        List['EmployeeDetailsAuditReportApiModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_employee_id=request_employee_id,
            request_section=request_section,
            request_pay_schedule_id=request_pay_schedule_id,
            request_include_post_tax_deductions=request_include_post_tax_deductions,
            request_from_date=request_from_date,
            request_to_date=request_to_date,
            request_location_id=request_location_id,
            request_employing_entity_id=request_employing_entity_id,
        )
    ).parsed
