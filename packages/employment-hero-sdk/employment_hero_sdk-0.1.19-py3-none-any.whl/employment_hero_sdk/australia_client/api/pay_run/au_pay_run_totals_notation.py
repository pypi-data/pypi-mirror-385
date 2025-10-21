from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pay_run_total_notation_model import PayRunTotalNotationModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    body: Union[
        PayRunTotalNotationModel,
        PayRunTotalNotationModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/payrun/{pay_run_id}/notation/{employee_id}",
    }

    if isinstance(body, PayRunTotalNotationModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, PayRunTotalNotationModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PayRunTotalNotationModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PayRunTotalNotationModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PayRunTotalNotationModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        PayRunTotalNotationModel,
        PayRunTotalNotationModel,
    ],
) -> Response[PayRunTotalNotationModel]:
    """Create Note for Employee

     Creates a note for an employee record in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        body (PayRunTotalNotationModel):
        body (PayRunTotalNotationModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PayRunTotalNotationModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        PayRunTotalNotationModel,
        PayRunTotalNotationModel,
    ],
) -> Optional[PayRunTotalNotationModel]:
    """Create Note for Employee

     Creates a note for an employee record in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        body (PayRunTotalNotationModel):
        body (PayRunTotalNotationModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PayRunTotalNotationModel
    """

    return sync_detailed(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        PayRunTotalNotationModel,
        PayRunTotalNotationModel,
    ],
) -> Response[PayRunTotalNotationModel]:
    """Create Note for Employee

     Creates a note for an employee record in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        body (PayRunTotalNotationModel):
        body (PayRunTotalNotationModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PayRunTotalNotationModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        pay_run_id=pay_run_id,
        employee_id=employee_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    pay_run_id: int,
    employee_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        PayRunTotalNotationModel,
        PayRunTotalNotationModel,
    ],
) -> Optional[PayRunTotalNotationModel]:
    """Create Note for Employee

     Creates a note for an employee record in a pay run.

    Args:
        business_id (str):
        pay_run_id (int):
        employee_id (int):
        body (PayRunTotalNotationModel):
        body (PayRunTotalNotationModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PayRunTotalNotationModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            pay_run_id=pay_run_id,
            employee_id=employee_id,
            client=client,
            body=body,
        )
    ).parsed
