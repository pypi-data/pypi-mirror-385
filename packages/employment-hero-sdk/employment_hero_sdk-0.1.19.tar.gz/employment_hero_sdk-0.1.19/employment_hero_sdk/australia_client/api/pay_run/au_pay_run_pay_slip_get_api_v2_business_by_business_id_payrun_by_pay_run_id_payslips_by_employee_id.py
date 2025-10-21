from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_api_pay_slip_model import AuApiPaySlipModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    show_all_data: Union[Unset, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["showAllData"] = show_all_data

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/payrun/{pay_run_id}/payslips/{employee_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuApiPaySlipModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuApiPaySlipModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuApiPaySlipModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    show_all_data: Union[Unset, bool] = False,
) -> Response[AuApiPaySlipModel]:
    """Get Pay Slip Data by Employee ID

     Gets the pay slip data for an employee in a payrun.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        show_all_data (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuApiPaySlipModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        show_all_data=show_all_data,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    show_all_data: Union[Unset, bool] = False,
) -> Optional[AuApiPaySlipModel]:
    """Get Pay Slip Data by Employee ID

     Gets the pay slip data for an employee in a payrun.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        show_all_data (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuApiPaySlipModel
    """

    return sync_detailed(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        client=client,
        show_all_data=show_all_data,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    show_all_data: Union[Unset, bool] = False,
) -> Response[AuApiPaySlipModel]:
    """Get Pay Slip Data by Employee ID

     Gets the pay slip data for an employee in a payrun.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        show_all_data (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuApiPaySlipModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        show_all_data=show_all_data,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    show_all_data: Union[Unset, bool] = False,
) -> Optional[AuApiPaySlipModel]:
    """Get Pay Slip Data by Employee ID

     Gets the pay slip data for an employee in a payrun.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        show_all_data (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuApiPaySlipModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            pay_run_id=pay_run_id,
            employee_id=employee_id,
            client=client,
            show_all_data=show_all_data,
        )
    ).parsed
