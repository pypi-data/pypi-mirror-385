from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.ess_qualification_upload_attachment_i_http_action_result import (
    EssQualificationUploadAttachmentIHttpActionResult,
)
from ...types import UNSET, Response


def _get_kwargs(
    employee_id: str,
    employee_qualification_id: int,
    *,
    file_name: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["fileName"] = file_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/ess/{employee_id}/qualification/{employee_qualification_id}/attachment",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EssQualificationUploadAttachmentIHttpActionResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EssQualificationUploadAttachmentIHttpActionResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EssQualificationUploadAttachmentIHttpActionResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    employee_qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[EssQualificationUploadAttachmentIHttpActionResult]:
    """Upload attachment to qualification

     Uploads an attachment to the qualification with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        employee_qualification_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssQualificationUploadAttachmentIHttpActionResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        employee_qualification_id=employee_qualification_id,
        file_name=file_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    employee_qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[EssQualificationUploadAttachmentIHttpActionResult]:
    """Upload attachment to qualification

     Uploads an attachment to the qualification with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        employee_qualification_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssQualificationUploadAttachmentIHttpActionResult
    """

    return sync_detailed(
        employee_id=employee_id,
        employee_qualification_id=employee_qualification_id,
        client=client,
        file_name=file_name,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    employee_qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Response[EssQualificationUploadAttachmentIHttpActionResult]:
    """Upload attachment to qualification

     Uploads an attachment to the qualification with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        employee_qualification_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EssQualificationUploadAttachmentIHttpActionResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        employee_qualification_id=employee_qualification_id,
        file_name=file_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    employee_qualification_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    file_name: str,
) -> Optional[EssQualificationUploadAttachmentIHttpActionResult]:
    """Upload attachment to qualification

     Uploads an attachment to the qualification with the specified ID.
    The request should be a MIME multipart file upload request.

    Args:
        employee_id (str):
        employee_qualification_id (int):
        file_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EssQualificationUploadAttachmentIHttpActionResult
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            employee_qualification_id=employee_qualification_id,
            client=client,
            file_name=file_name,
        )
    ).parsed
