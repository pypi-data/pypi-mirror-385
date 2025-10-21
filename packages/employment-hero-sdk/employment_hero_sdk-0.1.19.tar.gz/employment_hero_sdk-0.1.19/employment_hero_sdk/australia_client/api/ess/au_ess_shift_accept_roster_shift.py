from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_accept_roster_shift_response_model import AuAcceptRosterShiftResponseModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
    shift_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/ess/{employee_id}/shift/{shift_id}/accept",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuAcceptRosterShiftResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuAcceptRosterShiftResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuAcceptRosterShiftResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuAcceptRosterShiftResponseModel]:
    """Accept Roster Shift

     Accepts the roster shift with the specified ID.

    Args:
        employee_id (str):
        shift_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuAcceptRosterShiftResponseModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        shift_id=shift_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuAcceptRosterShiftResponseModel]:
    """Accept Roster Shift

     Accepts the roster shift with the specified ID.

    Args:
        employee_id (str):
        shift_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuAcceptRosterShiftResponseModel
    """

    return sync_detailed(
        employee_id=employee_id,
        shift_id=shift_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuAcceptRosterShiftResponseModel]:
    """Accept Roster Shift

     Accepts the roster shift with the specified ID.

    Args:
        employee_id (str):
        shift_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuAcceptRosterShiftResponseModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        shift_id=shift_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    shift_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuAcceptRosterShiftResponseModel]:
    """Accept Roster Shift

     Accepts the roster shift with the specified ID.

    Args:
        employee_id (str):
        shift_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuAcceptRosterShiftResponseModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            shift_id=shift_id,
            client=client,
        )
    ).parsed
