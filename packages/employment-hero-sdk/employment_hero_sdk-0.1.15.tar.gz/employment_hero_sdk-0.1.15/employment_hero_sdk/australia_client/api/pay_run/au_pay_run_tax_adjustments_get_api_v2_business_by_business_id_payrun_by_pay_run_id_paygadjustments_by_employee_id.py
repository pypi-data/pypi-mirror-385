from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pay_run_payg_adjustment_response import PayRunPaygAdjustmentResponse
from ...types import Response


def _get_kwargs(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/payrun/{pay_run_id}/paygadjustments/{employee_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PayRunPaygAdjustmentResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PayRunPaygAdjustmentResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PayRunPaygAdjustmentResponse]:
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
) -> Response[PayRunPaygAdjustmentResponse]:
    """Get PAYG Adjustments by Employee ID

     Gets all the PAYG adjustments for a specific employee in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PayRunPaygAdjustmentResponse]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
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
) -> Optional[PayRunPaygAdjustmentResponse]:
    """Get PAYG Adjustments by Employee ID

     Gets all the PAYG adjustments for a specific employee in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PayRunPaygAdjustmentResponse
    """

    return sync_detailed(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[PayRunPaygAdjustmentResponse]:
    """Get PAYG Adjustments by Employee ID

     Gets all the PAYG adjustments for a specific employee in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PayRunPaygAdjustmentResponse]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[PayRunPaygAdjustmentResponse]:
    """Get PAYG Adjustments by Employee ID

     Gets all the PAYG adjustments for a specific employee in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PayRunPaygAdjustmentResponse
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            pay_run_id=pay_run_id,
            employee_id=employee_id,
            client=client,
        )
    ).parsed
