from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.employee_qualification_document_model import EmployeeQualificationDocumentModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    *,
    visible: Union[Unset, bool] = False,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["visible"] = visible

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/qualification/{qualification_id}/document",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["EmployeeQualificationDocumentModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EmployeeQualificationDocumentModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["EmployeeQualificationDocumentModel"]]:
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
    *,
    client: Union[AuthenticatedClient, Client],
    visible: Union[Unset, bool] = False,
) -> Response[List["EmployeeQualificationDocumentModel"]]:
    """Create Employee Qualification Document

     Uploads an employee qualification document. Note: the request should be a MIME multipart file upload
    request.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        visible (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['EmployeeQualificationDocumentModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        visible=visible,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    visible: Union[Unset, bool] = False,
) -> Optional[List["EmployeeQualificationDocumentModel"]]:
    """Create Employee Qualification Document

     Uploads an employee qualification document. Note: the request should be a MIME multipart file upload
    request.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        visible (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['EmployeeQualificationDocumentModel']
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        client=client,
        visible=visible,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    visible: Union[Unset, bool] = False,
) -> Response[List["EmployeeQualificationDocumentModel"]]:
    """Create Employee Qualification Document

     Uploads an employee qualification document. Note: the request should be a MIME multipart file upload
    request.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        visible (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['EmployeeQualificationDocumentModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        qualification_id=qualification_id,
        visible=visible,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    visible: Union[Unset, bool] = False,
) -> Optional[List["EmployeeQualificationDocumentModel"]]:
    """Create Employee Qualification Document

     Uploads an employee qualification document. Note: the request should be a MIME multipart file upload
    request.

    Args:
        business_id (str):
        employee_id (str):
        qualification_id (int):
        visible (Union[Unset, bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['EmployeeQualificationDocumentModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            qualification_id=qualification_id,
            client=client,
            visible=visible,
        )
    ).parsed
