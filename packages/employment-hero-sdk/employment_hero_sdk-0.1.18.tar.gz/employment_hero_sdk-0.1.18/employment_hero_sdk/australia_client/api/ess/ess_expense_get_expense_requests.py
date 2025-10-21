from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ess_expense_request_response_model import EssExpenseRequestResponseModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    employee_id: str,
    *,
    current_page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 100,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["currentPage"] = current_page

    params["pageSize"] = page_size

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/ess/{employee_id}/expense",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["EssExpenseRequestResponseModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EssExpenseRequestResponseModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["EssExpenseRequestResponseModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    current_page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 100,
) -> Response[List["EssExpenseRequestResponseModel"]]:
    """Get Expense Requests

     Gets a paged view of expense requests for this employee.

    Args:
        employee_id (str):
        current_page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['EssExpenseRequestResponseModel']]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        current_page=current_page,
        page_size=page_size,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    current_page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 100,
) -> Optional[List["EssExpenseRequestResponseModel"]]:
    """Get Expense Requests

     Gets a paged view of expense requests for this employee.

    Args:
        employee_id (str):
        current_page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['EssExpenseRequestResponseModel']
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        current_page=current_page,
        page_size=page_size,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    current_page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 100,
) -> Response[List["EssExpenseRequestResponseModel"]]:
    """Get Expense Requests

     Gets a paged view of expense requests for this employee.

    Args:
        employee_id (str):
        current_page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['EssExpenseRequestResponseModel']]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        current_page=current_page,
        page_size=page_size,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    current_page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 100,
) -> Optional[List["EssExpenseRequestResponseModel"]]:
    """Get Expense Requests

     Gets a paged view of expense requests for this employee.

    Args:
        employee_id (str):
        current_page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['EssExpenseRequestResponseModel']
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            current_page=current_page,
            page_size=page_size,
        )
    ).parsed
