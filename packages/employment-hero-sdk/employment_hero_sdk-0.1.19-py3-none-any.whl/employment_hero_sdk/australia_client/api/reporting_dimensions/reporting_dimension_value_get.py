from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.reporting_dimension_value_api_model import ReportingDimensionValueApiModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    dimension_id: int,
    id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/dimension/{dimension_id}/value/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ReportingDimensionValueApiModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ReportingDimensionValueApiModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ReportingDimensionValueApiModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    dimension_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ReportingDimensionValueApiModel]:
    """Get Dimension Value by ID

     Gets the dimension value with the specified ID.

    Args:
        business_id (str):
        dimension_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReportingDimensionValueApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        dimension_id=dimension_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    dimension_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ReportingDimensionValueApiModel]:
    """Get Dimension Value by ID

     Gets the dimension value with the specified ID.

    Args:
        business_id (str):
        dimension_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReportingDimensionValueApiModel
    """

    return sync_detailed(
        business_id=business_id,
        dimension_id=dimension_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    dimension_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ReportingDimensionValueApiModel]:
    """Get Dimension Value by ID

     Gets the dimension value with the specified ID.

    Args:
        business_id (str):
        dimension_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReportingDimensionValueApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        dimension_id=dimension_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    dimension_id: int,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[ReportingDimensionValueApiModel]:
    """Get Dimension Value by ID

     Gets the dimension value with the specified ID.

    Args:
        business_id (str):
        dimension_id (int):
        id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReportingDimensionValueApiModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            dimension_id=dimension_id,
            id=id,
            client=client,
        )
    ).parsed
