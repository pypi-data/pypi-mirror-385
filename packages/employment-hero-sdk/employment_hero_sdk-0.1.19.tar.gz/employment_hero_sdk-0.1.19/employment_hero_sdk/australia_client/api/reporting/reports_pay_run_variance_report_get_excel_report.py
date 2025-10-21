import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.byte_array_content import ByteArrayContent
from ...models.reports_pay_run_variance_report_get_excel_report_request_comparison_type import (
    ReportsPayRunVarianceReportGetExcelReportRequestComparisonType,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_pay_run_id_1: Union[Unset, int] = UNSET,
    request_pay_run_id_2: Union[Unset, int] = UNSET,
    request_pay_period_from_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_from_2: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_2: Union[Unset, datetime.datetime] = UNSET,
    request_comparison_type: Union[Unset, ReportsPayRunVarianceReportGetExcelReportRequestComparisonType] = UNSET,
    request_highlight_variance_percentage: Union[Unset, float] = UNSET,
    request_only_show_variances: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.payRunId1"] = request_pay_run_id_1

    params["request.payRunId2"] = request_pay_run_id_2

    json_request_pay_period_from_1: Union[Unset, str] = UNSET
    if not isinstance(request_pay_period_from_1, Unset):
        json_request_pay_period_from_1 = request_pay_period_from_1.isoformat()
    params["request.payPeriodFrom1"] = json_request_pay_period_from_1

    json_request_pay_period_to_1: Union[Unset, str] = UNSET
    if not isinstance(request_pay_period_to_1, Unset):
        json_request_pay_period_to_1 = request_pay_period_to_1.isoformat()
    params["request.payPeriodTo1"] = json_request_pay_period_to_1

    json_request_pay_period_from_2: Union[Unset, str] = UNSET
    if not isinstance(request_pay_period_from_2, Unset):
        json_request_pay_period_from_2 = request_pay_period_from_2.isoformat()
    params["request.payPeriodFrom2"] = json_request_pay_period_from_2

    json_request_pay_period_to_2: Union[Unset, str] = UNSET
    if not isinstance(request_pay_period_to_2, Unset):
        json_request_pay_period_to_2 = request_pay_period_to_2.isoformat()
    params["request.payPeriodTo2"] = json_request_pay_period_to_2

    json_request_comparison_type: Union[Unset, str] = UNSET
    if not isinstance(request_comparison_type, Unset):
        json_request_comparison_type = request_comparison_type.value

    params["request.comparisonType"] = json_request_comparison_type

    params["request.highlightVariancePercentage"] = request_highlight_variance_percentage

    params["request.onlyShowVariances"] = request_only_show_variances

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/payrunvariance/xlxs",
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
    request_pay_run_id_1: Union[Unset, int] = UNSET,
    request_pay_run_id_2: Union[Unset, int] = UNSET,
    request_pay_period_from_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_from_2: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_2: Union[Unset, datetime.datetime] = UNSET,
    request_comparison_type: Union[Unset, ReportsPayRunVarianceReportGetExcelReportRequestComparisonType] = UNSET,
    request_highlight_variance_percentage: Union[Unset, float] = UNSET,
    request_only_show_variances: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Pay Run Variance Report

     Generates a pay run variance report as an Excel file.

    Args:
        business_id (str):
        request_pay_run_id_1 (Union[Unset, int]):
        request_pay_run_id_2 (Union[Unset, int]):
        request_pay_period_from_1 (Union[Unset, datetime.datetime]):
        request_pay_period_to_1 (Union[Unset, datetime.datetime]):
        request_pay_period_from_2 (Union[Unset, datetime.datetime]):
        request_pay_period_to_2 (Union[Unset, datetime.datetime]):
        request_comparison_type (Union[Unset,
            ReportsPayRunVarianceReportGetExcelReportRequestComparisonType]):
        request_highlight_variance_percentage (Union[Unset, float]):
        request_only_show_variances (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_pay_run_id_1=request_pay_run_id_1,
        request_pay_run_id_2=request_pay_run_id_2,
        request_pay_period_from_1=request_pay_period_from_1,
        request_pay_period_to_1=request_pay_period_to_1,
        request_pay_period_from_2=request_pay_period_from_2,
        request_pay_period_to_2=request_pay_period_to_2,
        request_comparison_type=request_comparison_type,
        request_highlight_variance_percentage=request_highlight_variance_percentage,
        request_only_show_variances=request_only_show_variances,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_run_id_1: Union[Unset, int] = UNSET,
    request_pay_run_id_2: Union[Unset, int] = UNSET,
    request_pay_period_from_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_from_2: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_2: Union[Unset, datetime.datetime] = UNSET,
    request_comparison_type: Union[Unset, ReportsPayRunVarianceReportGetExcelReportRequestComparisonType] = UNSET,
    request_highlight_variance_percentage: Union[Unset, float] = UNSET,
    request_only_show_variances: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Pay Run Variance Report

     Generates a pay run variance report as an Excel file.

    Args:
        business_id (str):
        request_pay_run_id_1 (Union[Unset, int]):
        request_pay_run_id_2 (Union[Unset, int]):
        request_pay_period_from_1 (Union[Unset, datetime.datetime]):
        request_pay_period_to_1 (Union[Unset, datetime.datetime]):
        request_pay_period_from_2 (Union[Unset, datetime.datetime]):
        request_pay_period_to_2 (Union[Unset, datetime.datetime]):
        request_comparison_type (Union[Unset,
            ReportsPayRunVarianceReportGetExcelReportRequestComparisonType]):
        request_highlight_variance_percentage (Union[Unset, float]):
        request_only_show_variances (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_pay_run_id_1=request_pay_run_id_1,
        request_pay_run_id_2=request_pay_run_id_2,
        request_pay_period_from_1=request_pay_period_from_1,
        request_pay_period_to_1=request_pay_period_to_1,
        request_pay_period_from_2=request_pay_period_from_2,
        request_pay_period_to_2=request_pay_period_to_2,
        request_comparison_type=request_comparison_type,
        request_highlight_variance_percentage=request_highlight_variance_percentage,
        request_only_show_variances=request_only_show_variances,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_run_id_1: Union[Unset, int] = UNSET,
    request_pay_run_id_2: Union[Unset, int] = UNSET,
    request_pay_period_from_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_from_2: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_2: Union[Unset, datetime.datetime] = UNSET,
    request_comparison_type: Union[Unset, ReportsPayRunVarianceReportGetExcelReportRequestComparisonType] = UNSET,
    request_highlight_variance_percentage: Union[Unset, float] = UNSET,
    request_only_show_variances: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Pay Run Variance Report

     Generates a pay run variance report as an Excel file.

    Args:
        business_id (str):
        request_pay_run_id_1 (Union[Unset, int]):
        request_pay_run_id_2 (Union[Unset, int]):
        request_pay_period_from_1 (Union[Unset, datetime.datetime]):
        request_pay_period_to_1 (Union[Unset, datetime.datetime]):
        request_pay_period_from_2 (Union[Unset, datetime.datetime]):
        request_pay_period_to_2 (Union[Unset, datetime.datetime]):
        request_comparison_type (Union[Unset,
            ReportsPayRunVarianceReportGetExcelReportRequestComparisonType]):
        request_highlight_variance_percentage (Union[Unset, float]):
        request_only_show_variances (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_pay_run_id_1=request_pay_run_id_1,
        request_pay_run_id_2=request_pay_run_id_2,
        request_pay_period_from_1=request_pay_period_from_1,
        request_pay_period_to_1=request_pay_period_to_1,
        request_pay_period_from_2=request_pay_period_from_2,
        request_pay_period_to_2=request_pay_period_to_2,
        request_comparison_type=request_comparison_type,
        request_highlight_variance_percentage=request_highlight_variance_percentage,
        request_only_show_variances=request_only_show_variances,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_run_id_1: Union[Unset, int] = UNSET,
    request_pay_run_id_2: Union[Unset, int] = UNSET,
    request_pay_period_from_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_1: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_from_2: Union[Unset, datetime.datetime] = UNSET,
    request_pay_period_to_2: Union[Unset, datetime.datetime] = UNSET,
    request_comparison_type: Union[Unset, ReportsPayRunVarianceReportGetExcelReportRequestComparisonType] = UNSET,
    request_highlight_variance_percentage: Union[Unset, float] = UNSET,
    request_only_show_variances: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Pay Run Variance Report

     Generates a pay run variance report as an Excel file.

    Args:
        business_id (str):
        request_pay_run_id_1 (Union[Unset, int]):
        request_pay_run_id_2 (Union[Unset, int]):
        request_pay_period_from_1 (Union[Unset, datetime.datetime]):
        request_pay_period_to_1 (Union[Unset, datetime.datetime]):
        request_pay_period_from_2 (Union[Unset, datetime.datetime]):
        request_pay_period_to_2 (Union[Unset, datetime.datetime]):
        request_comparison_type (Union[Unset,
            ReportsPayRunVarianceReportGetExcelReportRequestComparisonType]):
        request_highlight_variance_percentage (Union[Unset, float]):
        request_only_show_variances (Union[Unset, bool]):

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
            request_pay_run_id_1=request_pay_run_id_1,
            request_pay_run_id_2=request_pay_run_id_2,
            request_pay_period_from_1=request_pay_period_from_1,
            request_pay_period_to_1=request_pay_period_to_1,
            request_pay_period_from_2=request_pay_period_from_2,
            request_pay_period_to_2=request_pay_period_to_2,
            request_comparison_type=request_comparison_type,
            request_highlight_variance_percentage=request_highlight_variance_percentage,
            request_only_show_variances=request_only_show_variances,
        )
    ).parsed
