import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.generic_manager_timesheet_get_filter_order_by import GenericManagerTimesheetGetFilterOrderBy
from ...models.generic_manager_timesheet_get_filter_status import GenericManagerTimesheetGetFilterStatus
from ...models.paged_result_model_manager_timesheet_line_model import PagedResultModelManagerTimesheetLineModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_status: Union[Unset, GenericManagerTimesheetGetFilterStatus] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_include_costs: Union[Unset, bool] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_order_by: Union[Unset, GenericManagerTimesheetGetFilterOrderBy] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_from_date: Union[Unset, str] = UNSET
    if not isinstance(filter_from_date, Unset):
        json_filter_from_date = filter_from_date.isoformat()
    params["filter.fromDate"] = json_filter_from_date

    json_filter_to_date: Union[Unset, str] = UNSET
    if not isinstance(filter_to_date, Unset):
        json_filter_to_date = filter_to_date.isoformat()
    params["filter.toDate"] = json_filter_to_date

    json_filter_status: Union[Unset, str] = UNSET
    if not isinstance(filter_status, Unset):
        json_filter_status = filter_status.value

    params["filter.status"] = json_filter_status

    params["filter.employeeId"] = filter_employee_id

    params["filter.employeeGroupId"] = filter_employee_group_id

    params["filter.locationId"] = filter_location_id

    params["filter.includeCosts"] = filter_include_costs

    params["filter.currentPage"] = filter_current_page

    params["filter.pageSize"] = filter_page_size

    json_filter_order_by: Union[Unset, str] = UNSET
    if not isinstance(filter_order_by, Unset):
        json_filter_order_by = filter_order_by.value

    params["filter.orderBy"] = json_filter_order_by

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/timesheet",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PagedResultModelManagerTimesheetLineModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PagedResultModelManagerTimesheetLineModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PagedResultModelManagerTimesheetLineModel]:
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
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_status: Union[Unset, GenericManagerTimesheetGetFilterStatus] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_include_costs: Union[Unset, bool] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_order_by: Union[Unset, GenericManagerTimesheetGetFilterOrderBy] = UNSET,
) -> Response[PagedResultModelManagerTimesheetLineModel]:
    """Get Business Timesheets

     Retrieves timesheets for the specified business which manager can access

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_status (Union[Unset, GenericManagerTimesheetGetFilterStatus]):
        filter_employee_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_include_costs (Union[Unset, bool]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):
        filter_order_by (Union[Unset, GenericManagerTimesheetGetFilterOrderBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelManagerTimesheetLineModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_status=filter_status,
        filter_employee_id=filter_employee_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_location_id=filter_location_id,
        filter_include_costs=filter_include_costs,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
        filter_order_by=filter_order_by,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_status: Union[Unset, GenericManagerTimesheetGetFilterStatus] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_include_costs: Union[Unset, bool] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_order_by: Union[Unset, GenericManagerTimesheetGetFilterOrderBy] = UNSET,
) -> Optional[PagedResultModelManagerTimesheetLineModel]:
    """Get Business Timesheets

     Retrieves timesheets for the specified business which manager can access

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_status (Union[Unset, GenericManagerTimesheetGetFilterStatus]):
        filter_employee_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_include_costs (Union[Unset, bool]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):
        filter_order_by (Union[Unset, GenericManagerTimesheetGetFilterOrderBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelManagerTimesheetLineModel
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_status=filter_status,
        filter_employee_id=filter_employee_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_location_id=filter_location_id,
        filter_include_costs=filter_include_costs,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
        filter_order_by=filter_order_by,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_status: Union[Unset, GenericManagerTimesheetGetFilterStatus] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_include_costs: Union[Unset, bool] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_order_by: Union[Unset, GenericManagerTimesheetGetFilterOrderBy] = UNSET,
) -> Response[PagedResultModelManagerTimesheetLineModel]:
    """Get Business Timesheets

     Retrieves timesheets for the specified business which manager can access

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_status (Union[Unset, GenericManagerTimesheetGetFilterStatus]):
        filter_employee_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_include_costs (Union[Unset, bool]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):
        filter_order_by (Union[Unset, GenericManagerTimesheetGetFilterOrderBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelManagerTimesheetLineModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_status=filter_status,
        filter_employee_id=filter_employee_id,
        filter_employee_group_id=filter_employee_group_id,
        filter_location_id=filter_location_id,
        filter_include_costs=filter_include_costs,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
        filter_order_by=filter_order_by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_status: Union[Unset, GenericManagerTimesheetGetFilterStatus] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_employee_group_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_include_costs: Union[Unset, bool] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
    filter_order_by: Union[Unset, GenericManagerTimesheetGetFilterOrderBy] = UNSET,
) -> Optional[PagedResultModelManagerTimesheetLineModel]:
    """Get Business Timesheets

     Retrieves timesheets for the specified business which manager can access

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_status (Union[Unset, GenericManagerTimesheetGetFilterStatus]):
        filter_employee_id (Union[Unset, int]):
        filter_employee_group_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_include_costs (Union[Unset, bool]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):
        filter_order_by (Union[Unset, GenericManagerTimesheetGetFilterOrderBy]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelManagerTimesheetLineModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_from_date=filter_from_date,
            filter_to_date=filter_to_date,
            filter_status=filter_status,
            filter_employee_id=filter_employee_id,
            filter_employee_group_id=filter_employee_group_id,
            filter_location_id=filter_location_id,
            filter_include_costs=filter_include_costs,
            filter_current_page=filter_current_page,
            filter_page_size=filter_page_size,
            filter_order_by=filter_order_by,
        )
    ).parsed
