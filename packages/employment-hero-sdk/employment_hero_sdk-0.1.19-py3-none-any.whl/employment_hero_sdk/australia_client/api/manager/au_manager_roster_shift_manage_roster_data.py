import datetime
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_manager_roster_data_model import AuManagerRosterDataModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    filter_model_date: Union[Unset, datetime.datetime] = UNSET,
    filter_model_employee_id: Union[Unset, int] = UNSET,
    filter_model_location_id: Union[Unset, int] = UNSET,
    filter_model_role_id: Union[Unset, int] = UNSET,
    filter_model_include_costs: Union[Unset, bool] = UNSET,
    filter_model_include_sub_locations: Union[Unset, bool] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    json_filter_model_date: Union[Unset, str] = UNSET
    if not isinstance(filter_model_date, Unset):
        json_filter_model_date = filter_model_date.isoformat()
    params["filterModel.date"] = json_filter_model_date

    params["filterModel.employeeId"] = filter_model_employee_id

    params["filterModel.locationId"] = filter_model_location_id

    params["filterModel.roleId"] = filter_model_role_id

    params["filterModel.includeCosts"] = filter_model_include_costs

    params["filterModel.includeSubLocations"] = filter_model_include_sub_locations

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/manager/rostershift/manage",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuManagerRosterDataModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuManagerRosterDataModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuManagerRosterDataModel]:
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
    filter_model_date: Union[Unset, datetime.datetime] = UNSET,
    filter_model_employee_id: Union[Unset, int] = UNSET,
    filter_model_location_id: Union[Unset, int] = UNSET,
    filter_model_role_id: Union[Unset, int] = UNSET,
    filter_model_include_costs: Union[Unset, bool] = UNSET,
    filter_model_include_sub_locations: Union[Unset, bool] = UNSET,
) -> Response[AuManagerRosterDataModel]:
    """Manage Roster Data

     For the single date selected returns data about all published rostered shifts, published unassigned
    shifts,
    employee unavailablity, and leave requests.

    Args:
        business_id (str):
        filter_model_date (Union[Unset, datetime.datetime]):
        filter_model_employee_id (Union[Unset, int]):
        filter_model_location_id (Union[Unset, int]):
        filter_model_role_id (Union[Unset, int]):
        filter_model_include_costs (Union[Unset, bool]):
        filter_model_include_sub_locations (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuManagerRosterDataModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_model_date=filter_model_date,
        filter_model_employee_id=filter_model_employee_id,
        filter_model_location_id=filter_model_location_id,
        filter_model_role_id=filter_model_role_id,
        filter_model_include_costs=filter_model_include_costs,
        filter_model_include_sub_locations=filter_model_include_sub_locations,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_model_date: Union[Unset, datetime.datetime] = UNSET,
    filter_model_employee_id: Union[Unset, int] = UNSET,
    filter_model_location_id: Union[Unset, int] = UNSET,
    filter_model_role_id: Union[Unset, int] = UNSET,
    filter_model_include_costs: Union[Unset, bool] = UNSET,
    filter_model_include_sub_locations: Union[Unset, bool] = UNSET,
) -> Optional[AuManagerRosterDataModel]:
    """Manage Roster Data

     For the single date selected returns data about all published rostered shifts, published unassigned
    shifts,
    employee unavailablity, and leave requests.

    Args:
        business_id (str):
        filter_model_date (Union[Unset, datetime.datetime]):
        filter_model_employee_id (Union[Unset, int]):
        filter_model_location_id (Union[Unset, int]):
        filter_model_role_id (Union[Unset, int]):
        filter_model_include_costs (Union[Unset, bool]):
        filter_model_include_sub_locations (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuManagerRosterDataModel
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        filter_model_date=filter_model_date,
        filter_model_employee_id=filter_model_employee_id,
        filter_model_location_id=filter_model_location_id,
        filter_model_role_id=filter_model_role_id,
        filter_model_include_costs=filter_model_include_costs,
        filter_model_include_sub_locations=filter_model_include_sub_locations,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_model_date: Union[Unset, datetime.datetime] = UNSET,
    filter_model_employee_id: Union[Unset, int] = UNSET,
    filter_model_location_id: Union[Unset, int] = UNSET,
    filter_model_role_id: Union[Unset, int] = UNSET,
    filter_model_include_costs: Union[Unset, bool] = UNSET,
    filter_model_include_sub_locations: Union[Unset, bool] = UNSET,
) -> Response[AuManagerRosterDataModel]:
    """Manage Roster Data

     For the single date selected returns data about all published rostered shifts, published unassigned
    shifts,
    employee unavailablity, and leave requests.

    Args:
        business_id (str):
        filter_model_date (Union[Unset, datetime.datetime]):
        filter_model_employee_id (Union[Unset, int]):
        filter_model_location_id (Union[Unset, int]):
        filter_model_role_id (Union[Unset, int]):
        filter_model_include_costs (Union[Unset, bool]):
        filter_model_include_sub_locations (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuManagerRosterDataModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        filter_model_date=filter_model_date,
        filter_model_employee_id=filter_model_employee_id,
        filter_model_location_id=filter_model_location_id,
        filter_model_role_id=filter_model_role_id,
        filter_model_include_costs=filter_model_include_costs,
        filter_model_include_sub_locations=filter_model_include_sub_locations,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_model_date: Union[Unset, datetime.datetime] = UNSET,
    filter_model_employee_id: Union[Unset, int] = UNSET,
    filter_model_location_id: Union[Unset, int] = UNSET,
    filter_model_role_id: Union[Unset, int] = UNSET,
    filter_model_include_costs: Union[Unset, bool] = UNSET,
    filter_model_include_sub_locations: Union[Unset, bool] = UNSET,
) -> Optional[AuManagerRosterDataModel]:
    """Manage Roster Data

     For the single date selected returns data about all published rostered shifts, published unassigned
    shifts,
    employee unavailablity, and leave requests.

    Args:
        business_id (str):
        filter_model_date (Union[Unset, datetime.datetime]):
        filter_model_employee_id (Union[Unset, int]):
        filter_model_location_id (Union[Unset, int]):
        filter_model_role_id (Union[Unset, int]):
        filter_model_include_costs (Union[Unset, bool]):
        filter_model_include_sub_locations (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuManagerRosterDataModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            filter_model_date=filter_model_date,
            filter_model_employee_id=filter_model_employee_id,
            filter_model_location_id=filter_model_location_id,
            filter_model_role_id=filter_model_role_id,
            filter_model_include_costs=filter_model_include_costs,
            filter_model_include_sub_locations=filter_model_include_sub_locations,
        )
    ).parsed
