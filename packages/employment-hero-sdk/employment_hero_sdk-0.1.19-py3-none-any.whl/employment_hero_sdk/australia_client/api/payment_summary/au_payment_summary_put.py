from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    financial_year_ending: int,
    *,
    employee_id: Union[Unset, int] = UNSET,
    employing_entity_id: Union[Unset, int] = UNSET,
    location_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["employeeId"] = employee_id

    params["employingEntityId"] = employing_entity_id

    params["locationId"] = location_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/business/{business_id}/paymentsummary/{financial_year_ending}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    financial_year_ending: int,
    *,
    client: Union[AuthenticatedClient, Client],
    employee_id: Union[Unset, int] = UNSET,
    employing_entity_id: Union[Unset, int] = UNSET,
    location_id: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Generate Payment Summaries

     Generates (or regenerates) payment summaries for the specified financial year/business. Only
    unpublished payment summaries will be regenerated.

    Args:
        business_id (str):
        financial_year_ending (int):
        employee_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
        location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        financial_year_ending=financial_year_ending,
        employee_id=employee_id,
        employing_entity_id=employing_entity_id,
        location_id=location_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    business_id: str,
    financial_year_ending: int,
    *,
    client: Union[AuthenticatedClient, Client],
    employee_id: Union[Unset, int] = UNSET,
    employing_entity_id: Union[Unset, int] = UNSET,
    location_id: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Generate Payment Summaries

     Generates (or regenerates) payment summaries for the specified financial year/business. Only
    unpublished payment summaries will be regenerated.

    Args:
        business_id (str):
        financial_year_ending (int):
        employee_id (Union[Unset, int]):
        employing_entity_id (Union[Unset, int]):
        location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        financial_year_ending=financial_year_ending,
        employee_id=employee_id,
        employing_entity_id=employing_entity_id,
        location_id=location_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
