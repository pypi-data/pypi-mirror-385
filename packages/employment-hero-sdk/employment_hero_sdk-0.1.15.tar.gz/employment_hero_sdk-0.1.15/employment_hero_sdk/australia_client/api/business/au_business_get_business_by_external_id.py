from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_business_export_model import AuBusinessExportModel
from ...types import UNSET, Response


def _get_kwargs(
    *,
    external_id: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["externalId"] = external_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/business/externalid",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuBusinessExportModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuBusinessExportModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuBusinessExportModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    external_id: str,
) -> Response[AuBusinessExportModel]:
    """Get Business Details by External ID

     Retrieves the details of the business with the specified external ID.

    Args:
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuBusinessExportModel]
    """

    kwargs = _get_kwargs(
        external_id=external_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    external_id: str,
) -> Optional[AuBusinessExportModel]:
    """Get Business Details by External ID

     Retrieves the details of the business with the specified external ID.

    Args:
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuBusinessExportModel
    """

    return sync_detailed(
        client=client,
        external_id=external_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    external_id: str,
) -> Response[AuBusinessExportModel]:
    """Get Business Details by External ID

     Retrieves the details of the business with the specified external ID.

    Args:
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuBusinessExportModel]
    """

    kwargs = _get_kwargs(
        external_id=external_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    external_id: str,
) -> Optional[AuBusinessExportModel]:
    """Get Business Details by External ID

     Retrieves the details of the business with the specified external ID.

    Args:
        external_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuBusinessExportModel
    """

    return (
        await asyncio_detailed(
            client=client,
            external_id=external_id,
        )
    ).parsed
