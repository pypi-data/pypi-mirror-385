from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.earnings_line_split_api_model import EarningsLineSplitApiModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
    location_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/earningslinesplit/{location_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EarningsLineSplitApiModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EarningsLineSplitApiModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EarningsLineSplitApiModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    location_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EarningsLineSplitApiModel]:
    """Get Earnings line split by location ID

     Gets the earnings line split for this employee with the specified location ID.

    Args:
        business_id (str):
        employee_id (str):
        location_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EarningsLineSplitApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        location_id=location_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    location_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EarningsLineSplitApiModel]:
    """Get Earnings line split by location ID

     Gets the earnings line split for this employee with the specified location ID.

    Args:
        business_id (str):
        employee_id (str):
        location_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EarningsLineSplitApiModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        location_id=location_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    location_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EarningsLineSplitApiModel]:
    """Get Earnings line split by location ID

     Gets the earnings line split for this employee with the specified location ID.

    Args:
        business_id (str):
        employee_id (str):
        location_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EarningsLineSplitApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        location_id=location_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    location_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EarningsLineSplitApiModel]:
    """Get Earnings line split by location ID

     Gets the earnings line split for this employee with the specified location ID.

    Args:
        business_id (str):
        employee_id (str):
        location_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EarningsLineSplitApiModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            location_id=location_id,
            client=client,
        )
    ).parsed
