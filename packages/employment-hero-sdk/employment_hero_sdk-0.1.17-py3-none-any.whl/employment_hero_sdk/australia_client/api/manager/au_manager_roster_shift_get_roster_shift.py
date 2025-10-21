from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_manager_roster_shift_model import AuManagerRosterShiftModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    roster_shift_id: int,
    *,
    include_costs: Union[Unset, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["includeCosts"] = include_costs

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/rostershift/{roster_shift_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuManagerRosterShiftModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuManagerRosterShiftModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuManagerRosterShiftModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    roster_shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_costs: Union[Unset, bool] = False,
) -> Response[AuManagerRosterShiftModel]:
    """Get Roster Shift by ID

     Gets the details for a roster shift with the specified ID.

    Args:
        business_id (str):
        roster_shift_id (int):
        include_costs (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuManagerRosterShiftModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        roster_shift_id=roster_shift_id,
        include_costs=include_costs,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    roster_shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_costs: Union[Unset, bool] = False,
) -> Optional[AuManagerRosterShiftModel]:
    """Get Roster Shift by ID

     Gets the details for a roster shift with the specified ID.

    Args:
        business_id (str):
        roster_shift_id (int):
        include_costs (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuManagerRosterShiftModel
    """

    return sync_detailed(
        business_id=business_id,
        roster_shift_id=roster_shift_id,
        client=client,
        include_costs=include_costs,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    roster_shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_costs: Union[Unset, bool] = False,
) -> Response[AuManagerRosterShiftModel]:
    """Get Roster Shift by ID

     Gets the details for a roster shift with the specified ID.

    Args:
        business_id (str):
        roster_shift_id (int):
        include_costs (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuManagerRosterShiftModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        roster_shift_id=roster_shift_id,
        include_costs=include_costs,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    roster_shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    include_costs: Union[Unset, bool] = False,
) -> Optional[AuManagerRosterShiftModel]:
    """Get Roster Shift by ID

     Gets the details for a roster shift with the specified ID.

    Args:
        business_id (str):
        roster_shift_id (int):
        include_costs (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuManagerRosterShiftModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            roster_shift_id=roster_shift_id,
            client=client,
            include_costs=include_costs,
        )
    ).parsed
