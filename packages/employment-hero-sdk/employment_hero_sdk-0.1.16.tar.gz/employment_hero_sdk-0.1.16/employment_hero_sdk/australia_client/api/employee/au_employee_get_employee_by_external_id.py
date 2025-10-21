from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_unstructured_employee_model import AuUnstructuredEmployeeModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    external_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/employee/unstructured/externalid/{external_id}",
    }

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
    business_id: str,
    external_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuUnstructuredEmployeeModel]:
    """Get Employee By External ID

     Gets the employee with the specified external ID.

    Args:
        business_id (str):
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuUnstructuredEmployeeModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        external_id=external_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    external_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuUnstructuredEmployeeModel]:
    """Get Employee By External ID

     Gets the employee with the specified external ID.

    Args:
        business_id (str):
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuUnstructuredEmployeeModel
    """

    return sync_detailed(
        business_id=business_id,
        external_id=external_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    external_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuUnstructuredEmployeeModel]:
    """Get Employee By External ID

     Gets the employee with the specified external ID.

    Args:
        business_id (str):
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuUnstructuredEmployeeModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        external_id=external_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    external_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuUnstructuredEmployeeModel]:
    """Get Employee By External ID

     Gets the employee with the specified external ID.

    Args:
        business_id (str):
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuUnstructuredEmployeeModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            external_id=external_id,
            client=client,
        )
    ).parsed
