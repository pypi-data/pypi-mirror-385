from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.public_holiday_model import PublicHolidayModel
from ...types import UNSET, Response


def _get_kwargs(
    business_id: str,
    *,
    year: int,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["year"] = year

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/publicholiday",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["PublicHolidayModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = PublicHolidayModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["PublicHolidayModel"]]:
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
    year: int,
) -> Response[List["PublicHolidayModel"]]:
    """Get Public Holidays for Year

     Retrieves all the public holidays for a specific year.

    Args:
        business_id (str):
        year (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['PublicHolidayModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        year=year,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    year: int,
) -> Optional[List["PublicHolidayModel"]]:
    """Get Public Holidays for Year

     Retrieves all the public holidays for a specific year.

    Args:
        business_id (str):
        year (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['PublicHolidayModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        year=year,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    year: int,
) -> Response[List["PublicHolidayModel"]]:
    """Get Public Holidays for Year

     Retrieves all the public holidays for a specific year.

    Args:
        business_id (str):
        year (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['PublicHolidayModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        year=year,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    year: int,
) -> Optional[List["PublicHolidayModel"]]:
    """Get Public Holidays for Year

     Retrieves all the public holidays for a specific year.

    Args:
        business_id (str):
        year (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['PublicHolidayModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            year=year,
        )
    ).parsed
