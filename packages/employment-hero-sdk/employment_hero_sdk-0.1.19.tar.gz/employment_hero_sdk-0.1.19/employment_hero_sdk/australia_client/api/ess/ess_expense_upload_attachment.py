from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ess_expense_upload_attachment_i_http_action_result import EssExpenseUploadAttachmentIHttpActionResult
from ...types import UNSET, Response


def _get_kwargs(
    employee_id: str,
    expense_request_id: int,
    *,
    file_name: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["fileName"] = file_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/ess/{employee_id}/expense/{expense_request_id}/attachment",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EssExpenseUploadAttachmentIHttpActionResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EssExpenseUploadAttachmentIHttpActionResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EssExpenseUploadAttachmentIHttpActionResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[EssExpenseUploadAttachmentIHttpActionResult]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssExpenseUploadAttachmentIHttpActionResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        file_name=file_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[EssExpenseUploadAttachmentIHttpActionResult]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssExpenseUploadAttachmentIHttpActionResult
    """

    return sync_detailed(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        client=client,
        file_name=file_name,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[EssExpenseUploadAttachmentIHttpActionResult]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssExpenseUploadAttachmentIHttpActionResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        expense_request_id=expense_request_id,
        file_name=file_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    expense_request_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[EssExpenseUploadAttachmentIHttpActionResult]:
    """Upload Attachment to Expense Request

     Uploads an attachment to the expense request with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        expense_request_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssExpenseUploadAttachmentIHttpActionResult
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            expense_request_id=expense_request_id,
            client=client,
            file_name=file_name,
        )
    ).parsed
