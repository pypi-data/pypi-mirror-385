import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_leave_balances_export_model import AuLeaveBalancesExportModel
from ...models.au_reports_leave_balances_get_request_group_by import AuReportsLeaveBalancesGetRequestGroupBy
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["request.locationId"] = request_location_id

    params["request.leaveTypeId"] = request_leave_type_id

    json_request_group_by: Union[Unset, str] = UNSET
    if not isinstance(request_group_by, Unset):
        json_request_group_by = request_group_by.value

    params["request.groupBy"] = json_request_group_by

    params["request.employingEntityId"] = request_employing_entity_id

    json_request_as_at_date: Union[Unset, str] = UNSET
    if not isinstance(request_as_at_date, Unset):
        json_request_as_at_date = request_as_at_date.isoformat()
    params["request.asAtDate"] = json_request_as_at_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/leavebalances",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["AuLeaveBalancesExportModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AuLeaveBalancesExportModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["AuLeaveBalancesExportModel"]]:
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
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["AuLeaveBalancesExportModel"]]:
    """Leave Balances Report

     Generates a leave balances report.

    Args:
        business_id (str):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy]):
        request_employing_entity_id (Union[Unset, int]):
        request_as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuLeaveBalancesExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_group_by=request_group_by,
        request_employing_entity_id=request_employing_entity_id,
        request_as_at_date=request_as_at_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["AuLeaveBalancesExportModel"]]:
    """Leave Balances Report

     Generates a leave balances report.

    Args:
        business_id (str):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy]):
        request_employing_entity_id (Union[Unset, int]):
        request_as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuLeaveBalancesExportModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_group_by=request_group_by,
        request_employing_entity_id=request_employing_entity_id,
        request_as_at_date=request_as_at_date,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Response[List["AuLeaveBalancesExportModel"]]:
    """Leave Balances Report

     Generates a leave balances report.

    Args:
        business_id (str):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy]):
        request_employing_entity_id (Union[Unset, int]):
        request_as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['AuLeaveBalancesExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        request_location_id=request_location_id,
        request_leave_type_id=request_leave_type_id,
        request_group_by=request_group_by,
        request_employing_entity_id=request_employing_entity_id,
        request_as_at_date=request_as_at_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    request_location_id: Union[Unset, int] = UNSET,
    request_leave_type_id: Union[Unset, int] = UNSET,
    request_group_by: Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy] = UNSET,
    request_employing_entity_id: Union[Unset, int] = UNSET,
    request_as_at_date: Union[Unset, datetime.datetime] = UNSET,
) -> Optional[List["AuLeaveBalancesExportModel"]]:
    """Leave Balances Report

     Generates a leave balances report.

    Args:
        business_id (str):
        request_location_id (Union[Unset, int]):
        request_leave_type_id (Union[Unset, int]):
        request_group_by (Union[Unset, AuReportsLeaveBalancesGetRequestGroupBy]):
        request_employing_entity_id (Union[Unset, int]):
        request_as_at_date (Union[Unset, datetime.datetime]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['AuLeaveBalancesExportModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            request_location_id=request_location_id,
            request_leave_type_id=request_leave_type_id,
            request_group_by=request_group_by,
            request_employing_entity_id=request_employing_entity_id,
            request_as_at_date=request_as_at_date,
        )
    ).parsed
