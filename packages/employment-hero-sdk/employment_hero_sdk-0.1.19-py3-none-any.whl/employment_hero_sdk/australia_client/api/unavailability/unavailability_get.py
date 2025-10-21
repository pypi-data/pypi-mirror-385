import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unavailability_model import UnavailabilityModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_default_location_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_from_date: Union[Unset, str] = UNSET
    if not isinstance(filter_from_date, Unset):
        json_filter_from_date = filter_from_date.isoformat()
    params["filter.fromDate"] = json_filter_from_date

    json_filter_to_date: Union[Unset, str] = UNSET
    if not isinstance(filter_to_date, Unset):
        json_filter_to_date = filter_to_date.isoformat()
    params["filter.toDate"] = json_filter_to_date

    params["filter.employeeId"] = filter_employee_id

    params["filter.defaultLocationId"] = filter_default_location_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/unavailability",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["UnavailabilityModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = UnavailabilityModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["UnavailabilityModel"]]:
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
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_default_location_id: Union[Unset, int] = UNSET,
) -> Response[List["UnavailabilityModel"]]:
    """List Unavailabilities

     Lists all of the unavailabilities for this business, with optional filters.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_default_location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['UnavailabilityModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_default_location_id=filter_default_location_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_default_location_id: Union[Unset, int] = UNSET,
) -> Optional[List["UnavailabilityModel"]]:
    """List Unavailabilities

     Lists all of the unavailabilities for this business, with optional filters.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_default_location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['UnavailabilityModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_default_location_id=filter_default_location_id,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_default_location_id: Union[Unset, int] = UNSET,
) -> Response[List["UnavailabilityModel"]]:
    """List Unavailabilities

     Lists all of the unavailabilities for this business, with optional filters.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_default_location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['UnavailabilityModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_from_date=filter_from_date,
        filter_to_date=filter_to_date,
        filter_employee_id=filter_employee_id,
        filter_default_location_id=filter_default_location_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_from_date: Union[Unset, datetime.datetime] = UNSET,
    filter_to_date: Union[Unset, datetime.datetime] = UNSET,
    filter_employee_id: Union[Unset, int] = UNSET,
    filter_default_location_id: Union[Unset, int] = UNSET,
) -> Optional[List["UnavailabilityModel"]]:
    """List Unavailabilities

     Lists all of the unavailabilities for this business, with optional filters.

    Args:
        business_id (str):
        filter_from_date (Union[Unset, datetime.datetime]):
        filter_to_date (Union[Unset, datetime.datetime]):
        filter_employee_id (Union[Unset, int]):
        filter_default_location_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['UnavailabilityModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_from_date=filter_from_date,
            filter_to_date=filter_to_date,
            filter_employee_id=filter_employee_id,
            filter_default_location_id=filter_default_location_id,
        )
    ).parsed
