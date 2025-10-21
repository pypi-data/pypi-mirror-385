from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reports_employee_details_get_j_object import ReportsEmployeeDetailsGetJObject
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    selected_columns: Union[Unset, List[str]] = UNSET,
    location_id: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = UNSET,
    include_active: Union[Unset, bool] = True,
    include_inactive: Union[Unset, bool] = True,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_selected_columns: Union[Unset, List[str]] = UNSET
    if not isinstance(selected_columns, Unset):
        json_selected_columns = selected_columns

    params["selectedColumns"] = json_selected_columns

    params["locationId"] = location_id

    params["employingEntityId"] = employing_entity_id

    params["includeActive"] = include_active

    params["includeInactive"] = include_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/employeedetails",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ReportsEmployeeDetailsGetJObject"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ReportsEmployeeDetailsGetJObject.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ReportsEmployeeDetailsGetJObject"]]:
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
    selected_columns: Union[Unset, List[str]] = UNSET,
    location_id: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = UNSET,
    include_active: Union[Unset, bool] = True,
    include_inactive: Union[Unset, bool] = True,
) -> Response[List["ReportsEmployeeDetailsGetJObject"]]:
    """Employee Details Report

     Generates an employee details report.

    Args:
        business_id (str):
        selected_columns (Union[Unset, List[str]]):
        location_id (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):
        include_active (Union[Unset, bool]):  Default: True.
        include_inactive (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ReportsEmployeeDetailsGetJObject']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        selected_columns=selected_columns,
        location_id=location_id,
        employing_entity_id=employing_entity_id,
        include_active=include_active,
        include_inactive=include_inactive,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    selected_columns: Union[Unset, List[str]] = UNSET,
    location_id: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = UNSET,
    include_active: Union[Unset, bool] = True,
    include_inactive: Union[Unset, bool] = True,
) -> Optional[List["ReportsEmployeeDetailsGetJObject"]]:
    """Employee Details Report

     Generates an employee details report.

    Args:
        business_id (str):
        selected_columns (Union[Unset, List[str]]):
        location_id (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):
        include_active (Union[Unset, bool]):  Default: True.
        include_inactive (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ReportsEmployeeDetailsGetJObject']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        selected_columns=selected_columns,
        location_id=location_id,
        employing_entity_id=employing_entity_id,
        include_active=include_active,
        include_inactive=include_inactive,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    selected_columns: Union[Unset, List[str]] = UNSET,
    location_id: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = UNSET,
    include_active: Union[Unset, bool] = True,
    include_inactive: Union[Unset, bool] = True,
) -> Response[List["ReportsEmployeeDetailsGetJObject"]]:
    """Employee Details Report

     Generates an employee details report.

    Args:
        business_id (str):
        selected_columns (Union[Unset, List[str]]):
        location_id (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):
        include_active (Union[Unset, bool]):  Default: True.
        include_inactive (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ReportsEmployeeDetailsGetJObject']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        selected_columns=selected_columns,
        location_id=location_id,
        employing_entity_id=employing_entity_id,
        include_active=include_active,
        include_inactive=include_inactive,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    selected_columns: Union[Unset, List[str]] = UNSET,
    location_id: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = UNSET,
    include_active: Union[Unset, bool] = True,
    include_inactive: Union[Unset, bool] = True,
) -> Optional[List["ReportsEmployeeDetailsGetJObject"]]:
    """Employee Details Report

     Generates an employee details report.

    Args:
        business_id (str):
        selected_columns (Union[Unset, List[str]]):
        location_id (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):
        include_active (Union[Unset, bool]):  Default: True.
        include_inactive (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ReportsEmployeeDetailsGetJObject']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            selected_columns=selected_columns,
            location_id=location_id,
            employing_entity_id=employing_entity_id,
            include_active=include_active,
            include_inactive=include_inactive,
        )
    ).parsed
