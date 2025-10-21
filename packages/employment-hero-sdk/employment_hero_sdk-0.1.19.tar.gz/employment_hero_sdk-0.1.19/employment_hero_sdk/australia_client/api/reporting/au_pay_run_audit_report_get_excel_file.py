from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.byte_array_content import ByteArrayContent
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    pay_run_id: int,
    *,
    request_single_employee_worksheet: Union[Unset, bool] = UNSET,
    request_show_all_summary_details: Union[Unset, bool] = UNSET,
    request_show_all_employee_details: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.singleEmployeeWorksheet"] = request_single_employee_worksheet

    params["request.showAllSummaryDetails"] = request_show_all_summary_details

    params["request.showAllEmployeeDetails"] = request_show_all_employee_details

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/payrunaudit/{pay_run_id}/xlxs",
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
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    request_single_employee_worksheet: Union[Unset, bool] = UNSET,
    request_show_all_summary_details: Union[Unset, bool] = UNSET,
    request_show_all_employee_details: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Pay Run Audit Report

     Pay run audit report

    Args:
        business_id (str):
        pay_run_id (int):
        request_single_employee_worksheet (Union[Unset, bool]):
        request_show_all_summary_details (Union[Unset, bool]):
        request_show_all_employee_details (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        request_single_employee_worksheet=request_single_employee_worksheet,
        request_show_all_summary_details=request_show_all_summary_details,
        request_show_all_employee_details=request_show_all_employee_details,
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
    request_single_employee_worksheet: Union[Unset, bool] = UNSET,
    request_show_all_summary_details: Union[Unset, bool] = UNSET,
    request_show_all_employee_details: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Pay Run Audit Report

     Pay run audit report

    Args:
        business_id (str):
        pay_run_id (int):
        request_single_employee_worksheet (Union[Unset, bool]):
        request_show_all_summary_details (Union[Unset, bool]):
        request_show_all_employee_details (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return sync_detailed(
        business_id=business_id,
        pay_run_id=pay_run_id,
        client=client,
        request_single_employee_worksheet=request_single_employee_worksheet,
        request_show_all_summary_details=request_show_all_summary_details,
        request_show_all_employee_details=request_show_all_employee_details,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    request_single_employee_worksheet: Union[Unset, bool] = UNSET,
    request_show_all_summary_details: Union[Unset, bool] = UNSET,
    request_show_all_employee_details: Union[Unset, bool] = UNSET,
) -> Response[ByteArrayContent]:
    """Pay Run Audit Report

     Pay run audit report

    Args:
        business_id (str):
        pay_run_id (int):
        request_single_employee_worksheet (Union[Unset, bool]):
        request_show_all_summary_details (Union[Unset, bool]):
        request_show_all_employee_details (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ByteArrayContent]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        request_single_employee_worksheet=request_single_employee_worksheet,
        request_show_all_summary_details=request_show_all_summary_details,
        request_show_all_employee_details=request_show_all_employee_details,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    pay_run_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    request_single_employee_worksheet: Union[Unset, bool] = UNSET,
    request_show_all_summary_details: Union[Unset, bool] = UNSET,
    request_show_all_employee_details: Union[Unset, bool] = UNSET,
) -> Optional[ByteArrayContent]:
    """Pay Run Audit Report

     Pay run audit report

    Args:
        business_id (str):
        pay_run_id (int):
        request_single_employee_worksheet (Union[Unset, bool]):
        request_show_all_summary_details (Union[Unset, bool]):
        request_show_all_employee_details (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ByteArrayContent
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            pay_run_id=pay_run_id,
            client=client,
            request_single_employee_worksheet=request_single_employee_worksheet,
            request_show_all_summary_details=request_show_all_summary_details,
            request_show_all_employee_details=request_show_all_employee_details,
        )
    ).parsed
