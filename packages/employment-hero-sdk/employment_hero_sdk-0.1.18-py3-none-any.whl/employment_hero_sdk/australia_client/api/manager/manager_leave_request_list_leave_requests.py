import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.manager_leave_request_list_leave_requests_filter_group_by import (
    ManagerLeaveRequestListLeaveRequestsFilterGroupBy,
)
from ...models.manager_leave_request_list_leave_requests_filter_status import (
    ManagerLeaveRequestListLeaveRequestsFilterStatus,
)
from ...models.manager_leave_request_model import ManagerLeaveRequestModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_status: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_leave_category_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy] = UNSET,
    filter_restrict_overlapping_leave: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_status: Union[Unset, str] = UNSET
    if not isinstance(filter_status, Unset):
        json_filter_status = filter_status.value

    params["filter.status"] = json_filter_status

    json_filter_from_date: Union[Unset, str] = UNSET
    if not isinstance(filter_from_date, Unset):
        json_filter_from_date = filter_from_date.isoformat()
    params["filter.fromDate"] = json_filter_from_date

    json_filter_to_date: Union[Unset, str] = UNSET
    if not isinstance(filter_to_date, Unset):
        json_filter_to_date = filter_to_date.isoformat()
    params["filter.toDate"] = json_filter_to_date

    params["filter.leaveCategoryId"] = filter_leave_category_id

    params["filter.locationId"] = filter_location_id

    params["filter.employeeId"] = filter_employee_id

    json_filter_group_by: Union[Unset, str] = UNSET
    if not isinstance(filter_group_by, Unset):
        json_filter_group_by = filter_group_by.value

    params["filter.groupBy"] = json_filter_group_by

    params["filter.restrictOverlappingLeave"] = filter_restrict_overlapping_leave

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/leaverequest",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ManagerLeaveRequestModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ManagerLeaveRequestModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ManagerLeaveRequestModel"]]:
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
    filter_status: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_leave_category_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy] = UNSET,
    filter_restrict_overlapping_leave: Union[Unset, bool] = UNSET,
) -> Response[List["ManagerLeaveRequestModel"]]:
    """List Leave Requests

     Lists all the leave requests for this manager.

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_leave_category_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy]):
        filter_restrict_overlapping_leave (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ManagerLeaveRequestModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_leave_category_id=filter_leave_category_id,
        filter_location_id=filter_location_id,
        filter_employee_id=filter_employee_id,
        filter_group_by=filter_group_by,
        filter_restrict_overlapping_leave=filter_restrict_overlapping_leave,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_leave_category_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy] = UNSET,
    filter_restrict_overlapping_leave: Union[Unset, bool] = UNSET,
) -> Optional[List["ManagerLeaveRequestModel"]]:
    """List Leave Requests

     Lists all the leave requests for this manager.

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_leave_category_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy]):
        filter_restrict_overlapping_leave (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ManagerLeaveRequestModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_leave_category_id=filter_leave_category_id,
        filter_location_id=filter_location_id,
        filter_employee_id=filter_employee_id,
        filter_group_by=filter_group_by,
        filter_restrict_overlapping_leave=filter_restrict_overlapping_leave,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_leave_category_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy] = UNSET,
    filter_restrict_overlapping_leave: Union[Unset, bool] = UNSET,
) -> Response[List["ManagerLeaveRequestModel"]]:
    """List Leave Requests

     Lists all the leave requests for this manager.

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_leave_category_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy]):
        filter_restrict_overlapping_leave (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ManagerLeaveRequestModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_leave_category_id=filter_leave_category_id,
        filter_location_id=filter_location_id,
        filter_employee_id=filter_employee_id,
        filter_group_by=filter_group_by,
        filter_restrict_overlapping_leave=filter_restrict_overlapping_leave,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_leave_category_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy] = UNSET,
    filter_restrict_overlapping_leave: Union[Unset, bool] = UNSET,
) -> Optional[List["ManagerLeaveRequestModel"]]:
    """List Leave Requests

     Lists all the leave requests for this manager.

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_leave_category_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_employee_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerLeaveRequestListLeaveRequestsFilterGroupBy]):
        filter_restrict_overlapping_leave (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ManagerLeaveRequestModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_status=filter_status,
            filter_from_date=filter_from_date,
            filter_to_date=filter_to_date,
            filter_leave_category_id=filter_leave_category_id,
            filter_location_id=filter_location_id,
            filter_employee_id=filter_employee_id,
            filter_group_by=filter_group_by,
            filter_restrict_overlapping_leave=filter_restrict_overlapping_leave,
        )
    ).parsed
