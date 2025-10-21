import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reports_tasks_report_get_request_status import ReportsTasksReportGetRequestStatus
from ...models.tasks_report_export_model import TasksReportExportModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_employee_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_status: Union[Unset, ReportsTasksReportGetRequestStatus] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.employeeId"] = request_employee_id

    params["request.payRunId"] = request_pay_run_id

    json_request_from_date: Union[Unset, str] = UNSET
    if not isinstance(request_from_date, Unset):
        json_request_from_date = request_from_date.isoformat()
    params["request.fromDate"] = json_request_from_date

    json_request_to_date: Union[Unset, str] = UNSET
    if not isinstance(request_to_date, Unset):
        json_request_to_date = request_to_date.isoformat()
    params["request.toDate"] = json_request_to_date

    params["request.payScheduleId"] = request_pay_schedule_id

    json_request_status: Union[Unset, str] = UNSET
    if not isinstance(request_status, Unset):
        json_request_status = request_status.value

    params["request.status"] = json_request_status

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/tasks",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["TasksReportExportModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = TasksReportExportModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["TasksReportExportModel"]]:
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
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_status: Union[Unset, ReportsTasksReportGetRequestStatus] = UNSET,
) -> Response[List["TasksReportExportModel"]]:
    """Get tasks by business id

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_pay_schedule_id (Union[Unset, int]):
        request_status (Union[Unset, ReportsTasksReportGetRequestStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['TasksReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employee_id=request_employee_id,
        request_pay_run_id=request_pay_run_id,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_pay_schedule_id=request_pay_schedule_id,
        request_status=request_status,
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
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_status: Union[Unset, ReportsTasksReportGetRequestStatus] = UNSET,
) -> Optional[List["TasksReportExportModel"]]:
    """Get tasks by business id

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_pay_schedule_id (Union[Unset, int]):
        request_status (Union[Unset, ReportsTasksReportGetRequestStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['TasksReportExportModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_employee_id=request_employee_id,
        request_pay_run_id=request_pay_run_id,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_pay_schedule_id=request_pay_schedule_id,
        request_status=request_status,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_employee_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_status: Union[Unset, ReportsTasksReportGetRequestStatus] = UNSET,
) -> Response[List["TasksReportExportModel"]]:
    """Get tasks by business id

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_pay_schedule_id (Union[Unset, int]):
        request_status (Union[Unset, ReportsTasksReportGetRequestStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['TasksReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_employee_id=request_employee_id,
        request_pay_run_id=request_pay_run_id,
        request_from_date=request_from_date,
        request_to_date=request_to_date,
        request_pay_schedule_id=request_pay_schedule_id,
        request_status=request_status,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_employee_id: Union[Unset, int] = UNSET,
    request_pay_run_id: Union[Unset, int] = UNSET,
    request_from_date: Union[Unset, datetime.datetime] = UNSET,
    request_to_date: Union[Unset, datetime.datetime] = UNSET,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_status: Union[Unset, ReportsTasksReportGetRequestStatus] = UNSET,
) -> Optional[List["TasksReportExportModel"]]:
    """Get tasks by business id

    Args:
        business_id (str):
        request_employee_id (Union[Unset, int]):
        request_pay_run_id (Union[Unset, int]):
        request_from_date (Union[Unset, datetime.datetime]):
        request_to_date (Union[Unset, datetime.datetime]):
        request_pay_schedule_id (Union[Unset, int]):
        request_status (Union[Unset, ReportsTasksReportGetRequestStatus]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['TasksReportExportModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_employee_id=request_employee_id,
            request_pay_run_id=request_pay_run_id,
            request_from_date=request_from_date,
            request_to_date=request_to_date,
            request_pay_schedule_id=request_pay_schedule_id,
            request_status=request_status,
        )
    ).parsed
