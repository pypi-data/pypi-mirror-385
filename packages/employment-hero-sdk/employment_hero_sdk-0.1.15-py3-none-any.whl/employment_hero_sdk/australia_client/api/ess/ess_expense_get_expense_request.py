from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ess_expense_request_response_model import EssExpenseRequestResponseModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
    expense_request_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/ess/{employee_id}/expense/{expense_request_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EssExpenseRequestResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EssExpenseRequestResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EssExpenseRequestResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EssExpenseRequestResponseModel]:
    """Get Expense Request by ID

     Gets the expense request with the specified ID.

    Args:
        employee_id (str):
        expense_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssExpenseRequestResponseModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EssExpenseRequestResponseModel]:
    """Get Expense Request by ID

     Gets the expense request with the specified ID.

    Args:
        employee_id (str):
        expense_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssExpenseRequestResponseModel
    """

    return sync_detailed(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EssExpenseRequestResponseModel]:
    """Get Expense Request by ID

     Gets the expense request with the specified ID.

    Args:
        employee_id (str):
        expense_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssExpenseRequestResponseModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EssExpenseRequestResponseModel]:
    """Get Expense Request by ID

     Gets the expense request with the specified ID.

    Args:
        employee_id (str):
        expense_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssExpenseRequestResponseModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            expense_request_id=expense_request_id,
            client=client,
        )
    ).parsed
