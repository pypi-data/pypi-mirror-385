from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.leave_accrual_response import LeaveAccrualResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    pay_run_id: int,
    *,
    include_leave_taken: Union[Unset, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["includeLeaveTaken"] = include_leave_taken

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/payrun/{pay_run_id}/leaveaccrued",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[LeaveAccrualResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = LeaveAccrualResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[LeaveAccrualResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_leave_taken: Union[Unset, bool] = False,
) -> Response[LeaveAccrualResponse]:
    """Get Leave Accruals

     Lists all the leave accruals for the pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        include_leave_taken (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LeaveAccrualResponse]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        include_leave_taken=include_leave_taken,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_leave_taken: Union[Unset, bool] = False,
) -> Optional[LeaveAccrualResponse]:
    """Get Leave Accruals

     Lists all the leave accruals for the pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        include_leave_taken (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LeaveAccrualResponse
    """

    return sync_detailed(
        business_id=business_id,
        pay_run_id=pay_run_id,
        client=client,
        include_leave_taken=include_leave_taken,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_leave_taken: Union[Unset, bool] = False,
) -> Response[LeaveAccrualResponse]:
    """Get Leave Accruals

     Lists all the leave accruals for the pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        include_leave_taken (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[LeaveAccrualResponse]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        include_leave_taken=include_leave_taken,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_leave_taken: Union[Unset, bool] = False,
) -> Optional[LeaveAccrualResponse]:
    """Get Leave Accruals

     Lists all the leave accruals for the pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        include_leave_taken (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        LeaveAccrualResponse
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            pay_run_id=pay_run_id,
            client=client,
            include_leave_taken=include_leave_taken,
        )
    ).parsed
