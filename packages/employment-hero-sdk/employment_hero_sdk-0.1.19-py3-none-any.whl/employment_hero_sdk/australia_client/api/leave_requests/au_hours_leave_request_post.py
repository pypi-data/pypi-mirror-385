from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.hour_leave_request_model import HourLeaveRequestModel
from ...models.hour_leave_request_response_model import HourLeaveRequestResponseModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
    *,
    body: Union[
        HourLeaveRequestModel,
        HourLeaveRequestModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/leaverequest",
    }

    if isinstance(body, HourLeaveRequestModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, HourLeaveRequestModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[HourLeaveRequestResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = HourLeaveRequestResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[HourLeaveRequestResponseModel]:
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
    body: Union[
        HourLeaveRequestModel,
        HourLeaveRequestModel,
    ],
) -> Response[HourLeaveRequestResponseModel]:
    """Create Leave Request

     Creates a new leave request for an employee.

    Args:
        business_id (str):
        employee_id (str):
        body (HourLeaveRequestModel):
        body (HourLeaveRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HourLeaveRequestResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        body=body,
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
    body: Union[
        HourLeaveRequestModel,
        HourLeaveRequestModel,
    ],
) -> Optional[HourLeaveRequestResponseModel]:
    """Create Leave Request

     Creates a new leave request for an employee.

    Args:
        business_id (str):
        employee_id (str):
        body (HourLeaveRequestModel):
        body (HourLeaveRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HourLeaveRequestResponseModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        HourLeaveRequestModel,
        HourLeaveRequestModel,
    ],
) -> Response[HourLeaveRequestResponseModel]:
    """Create Leave Request

     Creates a new leave request for an employee.

    Args:
        business_id (str):
        employee_id (str):
        body (HourLeaveRequestModel):
        body (HourLeaveRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HourLeaveRequestResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        HourLeaveRequestModel,
        HourLeaveRequestModel,
    ],
) -> Optional[HourLeaveRequestResponseModel]:
    """Create Leave Request

     Creates a new leave request for an employee.

    Args:
        business_id (str):
        employee_id (str):
        body (HourLeaveRequestModel):
        body (HourLeaveRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HourLeaveRequestResponseModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
