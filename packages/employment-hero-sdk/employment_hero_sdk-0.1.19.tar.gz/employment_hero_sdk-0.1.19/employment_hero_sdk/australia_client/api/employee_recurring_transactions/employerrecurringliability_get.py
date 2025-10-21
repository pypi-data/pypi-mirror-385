from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employer_recurring_liability_model import EmployerRecurringLiabilityModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
    id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/employerliability/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EmployerRecurringLiabilityModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EmployerRecurringLiabilityModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EmployerRecurringLiabilityModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployerRecurringLiabilityModel]:
    """Get Employer liability by ID

     Gets the employee's recurring employer liabilities with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployerRecurringLiabilityModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployerRecurringLiabilityModel]:
    """Get Employer liability by ID

     Gets the employee's recurring employer liabilities with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployerRecurringLiabilityModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployerRecurringLiabilityModel]:
    """Get Employer liability by ID

     Gets the employee's recurring employer liabilities with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployerRecurringLiabilityModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployerRecurringLiabilityModel]:
    """Get Employer liability by ID

     Gets the employee's recurring employer liabilities with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployerRecurringLiabilityModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            id=id,
            client=client,
        )
    ).parsed
