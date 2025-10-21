from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_leave_allowance_template_model import AuLeaveAllowanceTemplateModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/leaveallowancetemplate",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuLeaveAllowanceTemplateModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuLeaveAllowanceTemplateModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuLeaveAllowanceTemplateModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuLeaveAllowanceTemplateModel]:
    """Get Leave Allowance Template for Employee

     Gets the current leave allowance template for the specified employee

    Args:
        business_id (str):
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuLeaveAllowanceTemplateModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuLeaveAllowanceTemplateModel]:
    """Get Leave Allowance Template for Employee

     Gets the current leave allowance template for the specified employee

    Args:
        business_id (str):
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuLeaveAllowanceTemplateModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuLeaveAllowanceTemplateModel]:
    """Get Leave Allowance Template for Employee

     Gets the current leave allowance template for the specified employee

    Args:
        business_id (str):
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuLeaveAllowanceTemplateModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuLeaveAllowanceTemplateModel]:
    """Get Leave Allowance Template for Employee

     Gets the current leave allowance template for the specified employee

    Args:
        business_id (str):
        employee_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuLeaveAllowanceTemplateModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            client=client,
        )
    ).parsed
