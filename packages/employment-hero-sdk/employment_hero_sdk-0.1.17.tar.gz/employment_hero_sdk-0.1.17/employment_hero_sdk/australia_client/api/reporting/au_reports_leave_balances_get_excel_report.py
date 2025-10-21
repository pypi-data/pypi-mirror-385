import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_reports_leave_balances_get_excel_report_request_filter_type import (
    AuReportsLeaveBalancesGetExcelReportRequestFilterType,
)
from ...models.au_reports_leave_balances_get_excel_report_request_group_by import (
    AuReportsLeaveBalancesGetExcelReportRequestGroupBy,
)
from ...models.byte_array_content import ByteArrayContent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_filter_type: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_hide_leave_values: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_request_filter_type: Union[Unset, str] = UNSET
    if not isinstance(request_filter_type, Unset):
        json_request_filter_type = request_filter_type.value

    params["request.filterType"] = json_request_filter_type

    json_request_as_at_date: Union[Unset, str] = UNSET
    if not isinstance(request_as_at_date, Unset):
        json_request_as_at_date = request_as_at_date.isoformat()
    params["request.asAtDate"] = json_request_as_at_date

    params["request.payRunId"] = request_pay_run_id

    json_request_group_by: Union[Unset, str] = UNSET
    if not isinstance(request_group_by, Unset):
        json_request_group_by = request_group_by.value

    params["request.groupBy"] = json_request_group_by

    params["request.locationId"] = request_location_id

    json_request_leave_type_ids: Union[Unset, List[int]] = UNSET
    if not isinstance(request_leave_type_ids, Unset):
        json_request_leave_type_ids = request_leave_type_ids

    params["request.leaveTypeIds"] = json_request_leave_type_ids

    params["request.employingEntityId"] = request_employing_entity_id

    params["request.hideLeaveValues"] = request_hide_leave_values

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/leavebalances/xlsx",
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
    request_filter_type: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_hide_leave_values: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Leave Balances Report as Excel

     Generates a Leave Balances Report as an Excel file.

    Args:
        business_id (str):
        request_filter_type (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_pay_run_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy]):
        request_location_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_employing_entity_id (Union[Unset, int]):
        request_hide_leave_values (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_filter_type=request_filter_type,
        request_as_at_date=request_as_at_date,
        request_pay_run_id=request_pay_run_id,
        request_group_by=request_group_by,
        request_location_id=request_location_id,
        request_leave_type_ids=request_leave_type_ids,
        request_employing_entity_id=request_employing_entity_id,
        request_hide_leave_values=request_hide_leave_values,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_filter_type: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_hide_leave_values: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Leave Balances Report as Excel

     Generates a Leave Balances Report as an Excel file.

    Args:
        business_id (str):
        request_filter_type (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_pay_run_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy]):
        request_location_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_employing_entity_id (Union[Unset, int]):
        request_hide_leave_values (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_filter_type=request_filter_type,
        request_as_at_date=request_as_at_date,
        request_pay_run_id=request_pay_run_id,
        request_group_by=request_group_by,
        request_location_id=request_location_id,
        request_leave_type_ids=request_leave_type_ids,
        request_employing_entity_id=request_employing_entity_id,
        request_hide_leave_values=request_hide_leave_values,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_filter_type: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_hide_leave_values: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Leave Balances Report as Excel

     Generates a Leave Balances Report as an Excel file.

    Args:
        business_id (str):
        request_filter_type (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_pay_run_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy]):
        request_location_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_employing_entity_id (Union[Unset, int]):
        request_hide_leave_values (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_filter_type=request_filter_type,
        request_as_at_date=request_as_at_date,
        request_pay_run_id=request_pay_run_id,
        request_group_by=request_group_by,
        request_location_id=request_location_id,
        request_leave_type_ids=request_leave_type_ids,
        request_employing_entity_id=request_employing_entity_id,
        request_hide_leave_values=request_hide_leave_values,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_filter_type: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_hide_leave_values: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Leave Balances Report as Excel

     Generates a Leave Balances Report as an Excel file.

    Args:
        business_id (str):
        request_filter_type (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestFilterType]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_pay_run_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetExcelReportRequestGroupBy]):
        request_location_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_employing_entity_id (Union[Unset, int]):
        request_hide_leave_values (Union[Unset, bool]):

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
            request_filter_type=request_filter_type,
            request_as_at_date=request_as_at_date,
            request_pay_run_id=request_pay_run_id,
            request_group_by=request_group_by,
            request_location_id=request_location_id,
            request_leave_type_ids=request_leave_type_ids,
            request_employing_entity_id=request_employing_entity_id,
            request_hide_leave_values=request_hide_leave_values,
        )
    ).parsed
