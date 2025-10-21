from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.basic_kiosk_employee_model import BasicKioskEmployeeModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    kiosk_id: int,
    *,
    restrict_current_shifts_to_current_kiosk_location: Union[Unset, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["restrictCurrentShiftsToCurrentKioskLocation"] = restrict_current_shifts_to_current_kiosk_location

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/kiosk/{kiosk_id}/staff",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["BasicKioskEmployeeModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = BasicKioskEmployeeModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["BasicKioskEmployeeModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    restrict_current_shifts_to_current_kiosk_location: Union[Unset, bool] = False,
) -> Response[List["BasicKioskEmployeeModel"]]:
    """List Kiosk Staff

     Lists all the staff associated with a kiosk and their current shifts.

    Args:
        business_id (str):
        kiosk_id (int):
        restrict_current_shifts_to_current_kiosk_location (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['BasicKioskEmployeeModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        restrict_current_shifts_to_current_kiosk_location=restrict_current_shifts_to_current_kiosk_location,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    restrict_current_shifts_to_current_kiosk_location: Union[Unset, bool] = False,
) -> Optional[List["BasicKioskEmployeeModel"]]:
    """List Kiosk Staff

     Lists all the staff associated with a kiosk and their current shifts.

    Args:
        business_id (str):
        kiosk_id (int):
        restrict_current_shifts_to_current_kiosk_location (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['BasicKioskEmployeeModel']
    """

    return sync_detailed(
        business_id=business_id,
        kiosk_id=kiosk_id,
        client=client,
        restrict_current_shifts_to_current_kiosk_location=restrict_current_shifts_to_current_kiosk_location,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    restrict_current_shifts_to_current_kiosk_location: Union[Unset, bool] = False,
) -> Response[List["BasicKioskEmployeeModel"]]:
    """List Kiosk Staff

     Lists all the staff associated with a kiosk and their current shifts.

    Args:
        business_id (str):
        kiosk_id (int):
        restrict_current_shifts_to_current_kiosk_location (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['BasicKioskEmployeeModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        restrict_current_shifts_to_current_kiosk_location=restrict_current_shifts_to_current_kiosk_location,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    kiosk_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    restrict_current_shifts_to_current_kiosk_location: Union[Unset, bool] = False,
) -> Optional[List["BasicKioskEmployeeModel"]]:
    """List Kiosk Staff

     Lists all the staff associated with a kiosk and their current shifts.

    Args:
        business_id (str):
        kiosk_id (int):
        restrict_current_shifts_to_current_kiosk_location (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['BasicKioskEmployeeModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            kiosk_id=kiosk_id,
            client=client,
            restrict_current_shifts_to_current_kiosk_location=restrict_current_shifts_to_current_kiosk_location,
        )
    ).parsed
