from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_unstructured_employee_model import AuUnstructuredEmployeeModel
from ...models.employee_partial_edit_model import EmployeePartialEditModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
    *,
    body: Union[
        EmployeePartialEditModel,
        EmployeePartialEditModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/ess/{employee_id}/details",
    }

    if isinstance(body, EmployeePartialEditModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, EmployeePartialEditModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuUnstructuredEmployeeModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuUnstructuredEmployeeModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuUnstructuredEmployeeModel]:
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
    body: Union[
        EmployeePartialEditModel,
        EmployeePartialEditModel,
    ],
) -> Response[AuUnstructuredEmployeeModel]:
    """Save Details

     Saves any employee details that the employee is allowed to set.

    Args:
        employee_id (str):
        body (EmployeePartialEditModel):
        body (EmployeePartialEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuUnstructuredEmployeeModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EmployeePartialEditModel,
        EmployeePartialEditModel,
    ],
) -> Optional[AuUnstructuredEmployeeModel]:
    """Save Details

     Saves any employee details that the employee is allowed to set.

    Args:
        employee_id (str):
        body (EmployeePartialEditModel):
        body (EmployeePartialEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuUnstructuredEmployeeModel
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EmployeePartialEditModel,
        EmployeePartialEditModel,
    ],
) -> Response[AuUnstructuredEmployeeModel]:
    """Save Details

     Saves any employee details that the employee is allowed to set.

    Args:
        employee_id (str):
        body (EmployeePartialEditModel):
        body (EmployeePartialEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuUnstructuredEmployeeModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        EmployeePartialEditModel,
        EmployeePartialEditModel,
    ],
) -> Optional[AuUnstructuredEmployeeModel]:
    """Save Details

     Saves any employee details that the employee is allowed to set.

    Args:
        employee_id (str):
        body (EmployeePartialEditModel):
        body (EmployeePartialEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuUnstructuredEmployeeModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
