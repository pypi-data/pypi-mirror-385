from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.attachment_model import AttachmentModel
from ...types import UNSET, Response


def _get_kwargs(
    business_id: str,
    employee_id: int,
    expense_request_id: int,
    *,
    file_name: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["fileName"] = file_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/business/{business_id}/manager/{employee_id}/expense/{expense_request_id}/attachment",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AttachmentModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AttachmentModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AttachmentModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: int,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[AttachmentModel]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        business_id (str):
        employee_id (int):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        file_name=file_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: int,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[AttachmentModel]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        business_id (str):
        employee_id (int):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        client=client,
        file_name=file_name,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: int,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[AttachmentModel]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        business_id (str):
        employee_id (int):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AttachmentModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        file_name=file_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: int,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[AttachmentModel]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        business_id (str):
        employee_id (int):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AttachmentModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            expense_request_id=expense_request_id,
            client=client,
            file_name=file_name,
        )
    ).parsed
