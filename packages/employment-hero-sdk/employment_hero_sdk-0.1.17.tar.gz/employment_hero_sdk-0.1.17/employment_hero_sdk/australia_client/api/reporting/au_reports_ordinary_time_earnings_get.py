from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_ordinary_time_earnings_api_model import AuOrdinaryTimeEarningsApiModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_financial_year_ending: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.payScheduleId"] = request_pay_schedule_id

    params["request.employingEntityId"] = request_employing_entity_id

    params["request.financialYearEnding"] = request_financial_year_ending

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/ordinarytimeearnings",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuOrdinaryTimeEarningsApiModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuOrdinaryTimeEarningsApiModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuOrdinaryTimeEarningsApiModel"]]:
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
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_financial_year_ending: Union[Unset, int] = UNSET,
) -> Response[List["AuOrdinaryTimeEarningsApiModel"]]:
    """Ordinary Time Earnings Report

     Generates an ordinary time earnings report.

    Args:
        business_id (str):
        request_pay_schedule_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):
        request_financial_year_ending (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuOrdinaryTimeEarningsApiModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_pay_schedule_id=request_pay_schedule_id,
        request_employing_entity_id=request_employing_entity_id,
        request_financial_year_ending=request_financial_year_ending,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_financial_year_ending: Union[Unset, int] = UNSET,
) -> Optional[List["AuOrdinaryTimeEarningsApiModel"]]:
    """Ordinary Time Earnings Report

     Generates an ordinary time earnings report.

    Args:
        business_id (str):
        request_pay_schedule_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):
        request_financial_year_ending (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuOrdinaryTimeEarningsApiModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_pay_schedule_id=request_pay_schedule_id,
        request_employing_entity_id=request_employing_entity_id,
        request_financial_year_ending=request_financial_year_ending,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_financial_year_ending: Union[Unset, int] = UNSET,
) -> Response[List["AuOrdinaryTimeEarningsApiModel"]]:
    """Ordinary Time Earnings Report

     Generates an ordinary time earnings report.

    Args:
        business_id (str):
        request_pay_schedule_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):
        request_financial_year_ending (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuOrdinaryTimeEarningsApiModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_pay_schedule_id=request_pay_schedule_id,
        request_employing_entity_id=request_employing_entity_id,
        request_financial_year_ending=request_financial_year_ending,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_pay_schedule_id: Union[Unset, int] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_financial_year_ending: Union[Unset, int] = UNSET,
) -> Optional[List["AuOrdinaryTimeEarningsApiModel"]]:
    """Ordinary Time Earnings Report

     Generates an ordinary time earnings report.

    Args:
        business_id (str):
        request_pay_schedule_id (Union[Unset, int]):
        request_employing_entity_id (Union[Unset, int]):
        request_financial_year_ending (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuOrdinaryTimeEarningsApiModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_pay_schedule_id=request_pay_schedule_id,
            request_employing_entity_id=request_employing_entity_id,
            request_financial_year_ending=request_financial_year_ending,
        )
    ).parsed
