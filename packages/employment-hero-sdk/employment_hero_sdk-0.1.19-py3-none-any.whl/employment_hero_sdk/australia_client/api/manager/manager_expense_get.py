import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.manager_expense_get_filter_group_by import ManagerExpenseGetFilterGroupBy
from ...models.manager_expense_get_filter_status import ManagerExpenseGetFilterStatus
from ...models.paged_result_model_manager_expense_request_model import PagedResultModelManagerExpenseRequestModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_status: Union[Unset, ManagerExpenseGetFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_expense_category_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerExpenseGetFilterGroupBy] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
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

    params["filter.employeeId"] = filter_employee_id

    params["filter.locationId"] = filter_location_id

    params["filter.expenseCategoryId"] = filter_expense_category_id

    json_filter_group_by: Union[Unset, str] = UNSET
    if not isinstance(filter_group_by, Unset):
        json_filter_group_by = filter_group_by.value

    params["filter.groupBy"] = json_filter_group_by

    params["filter.currentPage"] = filter_current_page

    params["filter.pageSize"] = filter_page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/expense",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PagedResultModelManagerExpenseRequestModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PagedResultModelManagerExpenseRequestModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PagedResultModelManagerExpenseRequestModel]:
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
    filter_status: Union[Unset, ManagerExpenseGetFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_expense_category_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerExpenseGetFilterGroupBy] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
) -> Response[PagedResultModelManagerExpenseRequestModel]:
    """Get Business Expense Requests

     Retrieves expense request for the specified business which manager can access

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerExpenseGetFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_expense_category_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerExpenseGetFilterGroupBy]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelManagerExpenseRequestModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_expense_category_id=filter_expense_category_id,
        filter_group_by=filter_group_by,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerExpenseGetFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_expense_category_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerExpenseGetFilterGroupBy] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
) -> Optional[PagedResultModelManagerExpenseRequestModel]:
    """Get Business Expense Requests

     Retrieves expense request for the specified business which manager can access

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerExpenseGetFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_expense_category_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerExpenseGetFilterGroupBy]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelManagerExpenseRequestModel
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_expense_category_id=filter_expense_category_id,
        filter_group_by=filter_group_by,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerExpenseGetFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_expense_category_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerExpenseGetFilterGroupBy] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
) -> Response[PagedResultModelManagerExpenseRequestModel]:
    """Get Business Expense Requests

     Retrieves expense request for the specified business which manager can access

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerExpenseGetFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_expense_category_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerExpenseGetFilterGroupBy]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelManagerExpenseRequestModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_status=filter_status,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_location_id=filter_location_id,
        filter_expense_category_id=filter_expense_category_id,
        filter_group_by=filter_group_by,
        filter_current_page=filter_current_page,
        filter_page_size=filter_page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_status: Union[Unset, ManagerExpenseGetFilterStatus] = UNSET,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_location_id: Union[Unset, int] = UNSET,
    filter_expense_category_id: Union[Unset, int] = UNSET,
    filter_group_by: Union[Unset, ManagerExpenseGetFilterGroupBy] = UNSET,
    filter_current_page: Union[Unset, int] = UNSET,
    filter_page_size: Union[Unset, int] = UNSET,
) -> Optional[PagedResultModelManagerExpenseRequestModel]:
    """Get Business Expense Requests

     Retrieves expense request for the specified business which manager can access

    Args:
        business_id (str):
        filter_status (Union[Unset, ManagerExpenseGetFilterStatus]):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_location_id (Union[Unset, int]):
        filter_expense_category_id (Union[Unset, int]):
        filter_group_by (Union[Unset, ManagerExpenseGetFilterGroupBy]):
        filter_current_page (Union[Unset, int]):
        filter_page_size (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelManagerExpenseRequestModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_status=filter_status,
            filter_from_date=filter_from_date,
            filter_to_date=filter_to_date,
            filter_employee_id=filter_employee_id,
            filter_location_id=filter_location_id,
            filter_expense_category_id=filter_expense_category_id,
            filter_group_by=filter_group_by,
            filter_current_page=filter_current_page,
            filter_page_size=filter_page_size,
        )
    ).parsed
