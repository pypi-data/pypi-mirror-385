from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_ess_employee_details_edit_model import AuEssEmployeeDetailsEditModel
from ...models.au_ess_employee_details_view_model import AuEssEmployeeDetailsViewModel
from ...types import Response


def _get_kwargs(
    employee_id: str,
    *,
    body: Union[
        AuEssEmployeeDetailsEditModel,
        AuEssEmployeeDetailsEditModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/ess/{employee_id}/personaldetails",
    }

    if isinstance(body, AuEssEmployeeDetailsEditModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, AuEssEmployeeDetailsEditModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuEssEmployeeDetailsViewModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuEssEmployeeDetailsViewModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuEssEmployeeDetailsViewModel]:
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
        AuEssEmployeeDetailsEditModel,
        AuEssEmployeeDetailsEditModel,
    ],
) -> Response[AuEssEmployeeDetailsViewModel]:
    r"""Update Personal Details

     Updates the personal details for the specified employee.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".
    Valid TitleId values can be obtained from api/v2/ess/{employeeId}/lookup/title
    Valid SuburbId values can be obtained from api/v2/ess/{employeeId}/lookup/suburbs

    Args:
        employee_id (str):
        body (AuEssEmployeeDetailsEditModel):
        body (AuEssEmployeeDetailsEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuEssEmployeeDetailsViewModel]
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
        AuEssEmployeeDetailsEditModel,
        AuEssEmployeeDetailsEditModel,
    ],
) -> Optional[AuEssEmployeeDetailsViewModel]:
    r"""Update Personal Details

     Updates the personal details for the specified employee.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".
    Valid TitleId values can be obtained from api/v2/ess/{employeeId}/lookup/title
    Valid SuburbId values can be obtained from api/v2/ess/{employeeId}/lookup/suburbs

    Args:
        employee_id (str):
        body (AuEssEmployeeDetailsEditModel):
        body (AuEssEmployeeDetailsEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuEssEmployeeDetailsViewModel
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
        AuEssEmployeeDetailsEditModel,
        AuEssEmployeeDetailsEditModel,
    ],
) -> Response[AuEssEmployeeDetailsViewModel]:
    r"""Update Personal Details

     Updates the personal details for the specified employee.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".
    Valid TitleId values can be obtained from api/v2/ess/{employeeId}/lookup/title
    Valid SuburbId values can be obtained from api/v2/ess/{employeeId}/lookup/suburbs

    Args:
        employee_id (str):
        body (AuEssEmployeeDetailsEditModel):
        body (AuEssEmployeeDetailsEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuEssEmployeeDetailsViewModel]
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
        AuEssEmployeeDetailsEditModel,
        AuEssEmployeeDetailsEditModel,
    ],
) -> Optional[AuEssEmployeeDetailsViewModel]:
    r"""Update Personal Details

     Updates the personal details for the specified employee.
    Only fields to be updated need be specified. Fields left unspecified or null will not be changed.
    To update a field provide the new value, to specifically clear a value use the string \"(clear)\" or
    \"0\".
    Valid TitleId values can be obtained from api/v2/ess/{employeeId}/lookup/title
    Valid SuburbId values can be obtained from api/v2/ess/{employeeId}/lookup/suburbs

    Args:
        employee_id (str):
        body (AuEssEmployeeDetailsEditModel):
        body (AuEssEmployeeDetailsEditModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuEssEmployeeDetailsViewModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
