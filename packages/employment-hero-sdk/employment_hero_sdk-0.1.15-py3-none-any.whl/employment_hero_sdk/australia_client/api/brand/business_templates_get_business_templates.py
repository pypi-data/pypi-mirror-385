from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.business_template_model import BusinessTemplateModel
from ...types import Response


def _get_kwargs(
    brand_id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/brand/{brand_id}/business-templates",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["BusinessTemplateModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = BusinessTemplateModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["BusinessTemplateModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[List["BusinessTemplateModel"]]:
    """List Business Templates

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['BusinessTemplateModel']]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[List["BusinessTemplateModel"]]:
    """List Business Templates

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['BusinessTemplateModel']
    """

    return sync_detailed(
        brand_id=brand_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[List["BusinessTemplateModel"]]:
    """List Business Templates

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['BusinessTemplateModel']]
    """

    kwargs = _get_kwargs(
        brand_id=brand_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    brand_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[List["BusinessTemplateModel"]]:
    """List Business Templates

    Args:
        brand_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['BusinessTemplateModel']
    """

    return (
        await asyncio_detailed(
            brand_id=brand_id,
            client=client,
        )
    ).parsed
