from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_unstructured_employee_model import AuUnstructuredEmployeeModel
from ...models.employee_update_response_model import EmployeeUpdateResponseModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: int,
    *,
    body: Union[
        AuUnstructuredEmployeeModel,
        AuUnstructuredEmployeeModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/business/{business_id}/employee/unstructured/{employee_id}",
    }

    if isinstance(body, AuUnstructuredEmployeeModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, AuUnstructuredEmployeeModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[EmployeeUpdateResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = EmployeeUpdateResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[EmployeeUpdateResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuUnstructuredEmployeeModel,
        AuUnstructuredEmployeeModel,
    ],
) -> Response[EmployeeUpdateResponseModel]:
    r"""Update Employee

     Updates the employee with the specified ID.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".

    Args:
        business_id (str):
        employee_id (int):
        body (AuUnstructuredEmployeeModel):
        body (AuUnstructuredEmployeeModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeUpdateResponseModel]
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
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuUnstructuredEmployeeModel,
        AuUnstructuredEmployeeModel,
    ],
) -> Optional[EmployeeUpdateResponseModel]:
    r"""Update Employee

     Updates the employee with the specified ID.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".

    Args:
        business_id (str):
        employee_id (int):
        body (AuUnstructuredEmployeeModel):
        body (AuUnstructuredEmployeeModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeUpdateResponseModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuUnstructuredEmployeeModel,
        AuUnstructuredEmployeeModel,
    ],
) -> Response[EmployeeUpdateResponseModel]:
    r"""Update Employee

     Updates the employee with the specified ID.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".

    Args:
        business_id (str):
        employee_id (int):
        body (AuUnstructuredEmployeeModel):
        body (AuUnstructuredEmployeeModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EmployeeUpdateResponseModel]
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
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuUnstructuredEmployeeModel,
        AuUnstructuredEmployeeModel,
    ],
) -> Optional[EmployeeUpdateResponseModel]:
    r"""Update Employee

     Updates the employee with the specified ID.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".

    Args:
        business_id (str):
        employee_id (int):
        body (AuUnstructuredEmployeeModel):
        body (AuUnstructuredEmployeeModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EmployeeUpdateResponseModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
