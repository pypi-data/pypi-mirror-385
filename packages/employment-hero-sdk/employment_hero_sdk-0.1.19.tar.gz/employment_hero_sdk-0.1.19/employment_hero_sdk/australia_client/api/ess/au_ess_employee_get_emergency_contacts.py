from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employee_emergency_contacts_edit_model import EmployeeEmergencyContactsEditModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/ess/{employee_id}/emergencycontacts",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EmployeeEmergencyContactsEditModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EmployeeEmergencyContactsEditModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EmployeeEmergencyContactsEditModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployeeEmergencyContactsEditModel]:
    """Get Emergency Contacts

     Gets emergency contacts for the specified employee.

    Args:
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeEmergencyContactsEditModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployeeEmergencyContactsEditModel]:
    """Get Emergency Contacts

     Gets emergency contacts for the specified employee.

    Args:
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeEmergencyContactsEditModel
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployeeEmergencyContactsEditModel]:
    """Get Emergency Contacts

     Gets emergency contacts for the specified employee.

    Args:
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeEmergencyContactsEditModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployeeEmergencyContactsEditModel]:
    """Get Emergency Contacts

     Gets emergency contacts for the specified employee.

    Args:
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeEmergencyContactsEditModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
        )
    ).parsed
