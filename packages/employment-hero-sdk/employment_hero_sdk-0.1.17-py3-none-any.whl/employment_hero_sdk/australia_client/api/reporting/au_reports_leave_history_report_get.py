import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.leave_history_report_group_model import LeaveHistoryReportGroupModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    model_from_date: Union[Unset, datetime.datetime] = UNSET,
    model_to_date: Union[Unset, datetime.datetime] = UNSET,
    model_pay_schedule_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, List[str]] = UNSET,
    model_leave_category_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_model_from_date: Union[Unset, str] = UNSET
    if not isinstance(model_from_date, Unset):
        json_model_from_date = model_from_date.isoformat()
    params["model.fromDate"] = json_model_from_date

    json_model_to_date: Union[Unset, str] = UNSET
    if not isinstance(model_to_date, Unset):
        json_model_to_date = model_to_date.isoformat()
    params["model.toDate"] = json_model_to_date

    params["model.payScheduleId"] = model_pay_schedule_id

    params["model.locationId"] = model_location_id

    json_model_employee_id: Union[Unset, List[str]] = UNSET
    if not isinstance(model_employee_id, Unset):
        json_model_employee_id = model_employee_id

    params["model.employeeId"] = json_model_employee_id

    params["model.leaveCategoryId"] = model_leave_category_id

    params["model.employingEntityId"] = model_employing_entity_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/leavehistory",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["LeaveHistoryReportGroupModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LeaveHistoryReportGroupModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["LeaveHistoryReportGroupModel"]]:
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
    model_from_date: Union[Unset, datetime.datetime] = UNSET,
    model_to_date: Union[Unset, datetime.datetime] = UNSET,
    model_pay_schedule_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, List[str]] = UNSET,
    model_leave_category_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["LeaveHistoryReportGroupModel"]]:
    """Leave History Report

     Generates a leave history report.

    Args:
        business_id (str):
        model_from_date (Union[Unset, datetime.datetime]):
        model_to_date (Union[Unset, datetime.datetime]):
        model_pay_schedule_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employee_id (Union[Unset, List[str]]):
        model_leave_category_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LeaveHistoryReportGroupModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        model_from_date=model_from_date,
        model_to_date=model_to_date,
        model_pay_schedule_id=model_pay_schedule_id,
        model_location_id=model_location_id,
        model_employee_id=model_employee_id,
        model_leave_category_id=model_leave_category_id,
        model_employing_entity_id=model_employing_entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    model_from_date: Union[Unset, datetime.datetime] = UNSET,
    model_to_date: Union[Unset, datetime.datetime] = UNSET,
    model_pay_schedule_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, List[str]] = UNSET,
    model_leave_category_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["LeaveHistoryReportGroupModel"]]:
    """Leave History Report

     Generates a leave history report.

    Args:
        business_id (str):
        model_from_date (Union[Unset, datetime.datetime]):
        model_to_date (Union[Unset, datetime.datetime]):
        model_pay_schedule_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employee_id (Union[Unset, List[str]]):
        model_leave_category_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LeaveHistoryReportGroupModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        model_from_date=model_from_date,
        model_to_date=model_to_date,
        model_pay_schedule_id=model_pay_schedule_id,
        model_location_id=model_location_id,
        model_employee_id=model_employee_id,
        model_leave_category_id=model_leave_category_id,
        model_employing_entity_id=model_employing_entity_id,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    model_from_date: Union[Unset, datetime.datetime] = UNSET,
    model_to_date: Union[Unset, datetime.datetime] = UNSET,
    model_pay_schedule_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, List[str]] = UNSET,
    model_leave_category_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[List["LeaveHistoryReportGroupModel"]]:
    """Leave History Report

     Generates a leave history report.

    Args:
        business_id (str):
        model_from_date (Union[Unset, datetime.datetime]):
        model_to_date (Union[Unset, datetime.datetime]):
        model_pay_schedule_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employee_id (Union[Unset, List[str]]):
        model_leave_category_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['LeaveHistoryReportGroupModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        model_from_date=model_from_date,
        model_to_date=model_to_date,
        model_pay_schedule_id=model_pay_schedule_id,
        model_location_id=model_location_id,
        model_employee_id=model_employee_id,
        model_leave_category_id=model_leave_category_id,
        model_employing_entity_id=model_employing_entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    model_from_date: Union[Unset, datetime.datetime] = UNSET,
    model_to_date: Union[Unset, datetime.datetime] = UNSET,
    model_pay_schedule_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, List[str]] = UNSET,
    model_leave_category_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Optional[List["LeaveHistoryReportGroupModel"]]:
    """Leave History Report

     Generates a leave history report.

    Args:
        business_id (str):
        model_from_date (Union[Unset, datetime.datetime]):
        model_to_date (Union[Unset, datetime.datetime]):
        model_pay_schedule_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employee_id (Union[Unset, List[str]]):
        model_leave_category_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['LeaveHistoryReportGroupModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            model_from_date=model_from_date,
            model_to_date=model_to_date,
            model_pay_schedule_id=model_pay_schedule_id,
            model_location_id=model_location_id,
            model_employee_id=model_employee_id,
            model_leave_category_id=model_leave_category_id,
            model_employing_entity_id=model_employing_entity_id,
        )
    ).parsed
