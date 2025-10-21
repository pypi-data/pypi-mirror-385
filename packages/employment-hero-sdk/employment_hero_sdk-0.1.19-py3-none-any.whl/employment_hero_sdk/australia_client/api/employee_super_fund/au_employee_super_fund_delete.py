from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.save_super_fund_response_model import SaveSuperFundResponseModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: str,
    superfund_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v2/business/{business_id}/employee/{employee_id}/superfund/{superfund_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[SaveSuperFundResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SaveSuperFundResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[SaveSuperFundResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: str,
    superfund_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[SaveSuperFundResponseModel]:
    """Delete Super Fund

     Deletes the employee's super fund with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        superfund_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SaveSuperFundResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        superfund_id=superfund_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: str,
    superfund_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[SaveSuperFundResponseModel]:
    """Delete Super Fund

     Deletes the employee's super fund with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        superfund_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SaveSuperFundResponseModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        superfund_id=superfund_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: str,
    superfund_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[SaveSuperFundResponseModel]:
    """Delete Super Fund

     Deletes the employee's super fund with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        superfund_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SaveSuperFundResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        superfund_id=superfund_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: str,
    superfund_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[SaveSuperFundResponseModel]:
    """Delete Super Fund

     Deletes the employee's super fund with the specified ID.

    Args:
        business_id (str):
        employee_id (str):
        superfund_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SaveSuperFundResponseModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            superfund_id=superfund_id,
            client=client,
        )
    ).parsed
