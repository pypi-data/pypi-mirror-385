from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.manager_leave_request_model import ManagerLeaveRequestModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: int,
    leave_request_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v2/business/{business_id}/manager/{employee_id}/leaverequest/{leave_request_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ManagerLeaveRequestModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ManagerLeaveRequestModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ManagerLeaveRequestModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: int,
    leave_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ManagerLeaveRequestModel]:
    """Delete Leave Request

     Deletes the leave request with the specified ID.

    Args:
        business_id (str):
        employee_id (int):
        leave_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagerLeaveRequestModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        leave_request_id=leave_request_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: int,
    leave_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ManagerLeaveRequestModel]:
    """Delete Leave Request

     Deletes the leave request with the specified ID.

    Args:
        business_id (str):
        employee_id (int):
        leave_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagerLeaveRequestModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        leave_request_id=leave_request_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: int,
    leave_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ManagerLeaveRequestModel]:
    """Delete Leave Request

     Deletes the leave request with the specified ID.

    Args:
        business_id (str):
        employee_id (int):
        leave_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagerLeaveRequestModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        leave_request_id=leave_request_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: int,
    leave_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ManagerLeaveRequestModel]:
    """Delete Leave Request

     Deletes the leave request with the specified ID.

    Args:
        business_id (str):
        employee_id (int):
        leave_request_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagerLeaveRequestModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            leave_request_id=leave_request_id,
            client=client,
        )
    ).parsed
