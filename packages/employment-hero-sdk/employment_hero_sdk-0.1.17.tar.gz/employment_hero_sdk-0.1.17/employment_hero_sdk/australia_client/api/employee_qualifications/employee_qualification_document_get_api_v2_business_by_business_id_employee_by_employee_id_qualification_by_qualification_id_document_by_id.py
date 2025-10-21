from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employee_qualification_document_model import EmployeeQualificationDocumentModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/qualification/{qualification_id}/document/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EmployeeQualificationDocumentModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EmployeeQualificationDocumentModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EmployeeQualificationDocumentModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployeeQualificationDocumentModel]:
    """Get Qualification Document by ID

     Gets the details for a qualification document by ID.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeQualificationDocumentModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployeeQualificationDocumentModel]:
    """Get Qualification Document by ID

     Gets the details for a qualification document by ID.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeQualificationDocumentModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[EmployeeQualificationDocumentModel]:
    """Get Qualification Document by ID

     Gets the details for a qualification document by ID.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeQualificationDocumentModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[EmployeeQualificationDocumentModel]:
    """Get Qualification Document by ID

     Gets the details for a qualification document by ID.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeQualificationDocumentModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            qualification_id=qualification_id,
            id=id,
            client=client,
        )
    ).parsed
