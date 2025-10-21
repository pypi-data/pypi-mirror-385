import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_leave_liability_export_model import AuLeaveLiabilityExportModel
from ...models.au_reports_leave_liability_get_request_filter_type import AuReportsLeaveLiabilityGetRequestFilterType
from ...models.au_reports_leave_liability_get_request_group_by import AuReportsLeaveLiabilityGetRequestGroupBy
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_job_id: Union[Unset, str] = UNSET,
    request_filter_type: Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_include_approved_leave: Union[Unset, bool] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.jobId"] = request_job_id

    json_request_filter_type: Union[Unset, str] = UNSET
    if not isinstance(request_filter_type, Unset):
        json_request_filter_type = request_filter_type.value

    params["request.filterType"] = json_request_filter_type

    params["request.locationId"] = request_location_id

    params["request.leaveTypeId"] = request_leave_type_id

    params["request.includeApprovedLeave"] = request_include_approved_leave

    json_request_as_at_date: Union[Unset, str] = UNSET
    if not isinstance(request_as_at_date, Unset):
        json_request_as_at_date = request_as_at_date.isoformat()
    params["request.asAtDate"] = json_request_as_at_date

    params["request.employingEntityId"] = request_employing_entity_id

    params["request.payRunId"] = request_pay_run_id

    json_request_leave_type_ids: Union[Unset, List[int]] = UNSET
    if not isinstance(request_leave_type_ids, Unset):
        json_request_leave_type_ids = request_leave_type_ids

    params["request.leaveTypeIds"] = json_request_leave_type_ids

    json_request_group_by: Union[Unset, str] = UNSET
    if not isinstance(request_group_by, Unset):
        json_request_group_by = request_group_by.value

    params["request.groupBy"] = json_request_group_by

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/leaveliability",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuLeaveLiabilityExportModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuLeaveLiabilityExportModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuLeaveLiabilityExportModel"]]:
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
    request_job_id: Union[Unset, str] = UNSET,
    request_filter_type: Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_include_approved_leave: Union[Unset, bool] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy] = UNSET,
) -> Response[List["AuLeaveLiabilityExportModel"]]:
    """Leave Liability Report

     Generates a leave liability report.

    Args:
        business_id (str):
        request_job_id (Union[Unset, str]):
        request_filter_type (Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType]):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_include_approved_leave (Union[Unset, bool]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_employing_entity_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_group_by (Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuLeaveLiabilityExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_job_id=request_job_id,
        request_filter_type=request_filter_type,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_include_approved_leave=request_include_approved_leave,
        request_as_at_date=request_as_at_date,
        request_employing_entity_id=request_employing_entity_id,
        request_pay_run_id=request_pay_run_id,
        request_leave_type_ids=request_leave_type_ids,
        request_group_by=request_group_by,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_job_id: Union[Unset, str] = UNSET,
    request_filter_type: Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_include_approved_leave: Union[Unset, bool] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy] = UNSET,
) -> Optional[List["AuLeaveLiabilityExportModel"]]:
    """Leave Liability Report

     Generates a leave liability report.

    Args:
        business_id (str):
        request_job_id (Union[Unset, str]):
        request_filter_type (Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType]):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_include_approved_leave (Union[Unset, bool]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_employing_entity_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_group_by (Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuLeaveLiabilityExportModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_job_id=request_job_id,
        request_filter_type=request_filter_type,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_include_approved_leave=request_include_approved_leave,
        request_as_at_date=request_as_at_date,
        request_employing_entity_id=request_employing_entity_id,
        request_pay_run_id=request_pay_run_id,
        request_leave_type_ids=request_leave_type_ids,
        request_group_by=request_group_by,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_job_id: Union[Unset, str] = UNSET,
    request_filter_type: Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_include_approved_leave: Union[Unset, bool] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy] = UNSET,
) -> Response[List["AuLeaveLiabilityExportModel"]]:
    """Leave Liability Report

     Generates a leave liability report.

    Args:
        business_id (str):
        request_job_id (Union[Unset, str]):
        request_filter_type (Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType]):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_include_approved_leave (Union[Unset, bool]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_employing_entity_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_group_by (Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuLeaveLiabilityExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_job_id=request_job_id,
        request_filter_type=request_filter_type,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_include_approved_leave=request_include_approved_leave,
        request_as_at_date=request_as_at_date,
        request_employing_entity_id=request_employing_entity_id,
        request_pay_run_id=request_pay_run_id,
        request_leave_type_ids=request_leave_type_ids,
        request_group_by=request_group_by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_job_id: Union[Unset, str] = UNSET,
    request_filter_type: Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType] = UNSET,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_include_approved_leave: Union[Unset, bool] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_leave_type_ids: Union[Unset, List[int]] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy] = UNSET,
) -> Optional[List["AuLeaveLiabilityExportModel"]]:
    """Leave Liability Report

     Generates a leave liability report.

    Args:
        business_id (str):
        request_job_id (Union[Unset, str]):
        request_filter_type (Union[Unset, AuReportsLeaveLiabilityGetRequestFilterType]):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_include_approved_leave (Union[Unset, bool]):
        request_as_at_date (Union[Unset, datetime.datetime]):
        request_employing_entity_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_leave_type_ids (Union[Unset, List[int]]):
        request_group_by (Union[Unset, AuReportsLeaveLiabilityGetRequestGroupBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuLeaveLiabilityExportModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_job_id=request_job_id,
            request_filter_type=request_filter_type,
            request_location_id=request_location_id,
            request_leave_type_id=request_leave_type_id,
            request_include_approved_leave=request_include_approved_leave,
            request_as_at_date=request_as_at_date,
            request_employing_entity_id=request_employing_entity_id,
            request_pay_run_id=request_pay_run_id,
            request_leave_type_ids=request_leave_type_ids,
            request_group_by=request_group_by,
        )
    ).parsed
