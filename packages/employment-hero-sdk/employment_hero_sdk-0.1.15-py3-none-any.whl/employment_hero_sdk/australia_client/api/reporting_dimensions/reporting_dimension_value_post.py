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
    *,
    body: Union[
        ReportingDimensionValueApiModel,
        ReportingDimensionValueApiModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/dimension/{dimension_id}/value",
    }

    if isinstance(body, ReportingDimensionValueApiModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, ReportingDimensionValueApiModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ReportingDimensionValueApiModel,
        ReportingDimensionValueApiModel,
    ],
) -> Response[ReportingDimensionValueApiModel]:
    """Create Dimension Value

     Creates a new value for the specified dimension.

    Args:
        business_id (str):
        dimension_id (int):
        body (ReportingDimensionValueApiModel):
        body (ReportingDimensionValueApiModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReportingDimensionValueApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        dimension_id=dimension_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    dimension_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ReportingDimensionValueApiModel,
        ReportingDimensionValueApiModel,
    ],
) -> Optional[ReportingDimensionValueApiModel]:
    """Create Dimension Value

     Creates a new value for the specified dimension.

    Args:
        business_id (str):
        dimension_id (int):
        body (ReportingDimensionValueApiModel):
        body (ReportingDimensionValueApiModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ReportingDimensionValueApiModel
    """

    return sync_detailed(
        business_id=business_id,
        dimension_id=dimension_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    dimension_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ReportingDimensionValueApiModel,
        ReportingDimensionValueApiModel,
    ],
) -> Response[ReportingDimensionValueApiModel]:
    """Create Dimension Value

     Creates a new value for the specified dimension.

    Args:
        business_id (str):
        dimension_id (int):
        body (ReportingDimensionValueApiModel):
        body (ReportingDimensionValueApiModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ReportingDimensionValueApiModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        dimension_id=dimension_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    dimension_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ReportingDimensionValueApiModel,
        ReportingDimensionValueApiModel,
    ],
) -> Optional[ReportingDimensionValueApiModel]:
    """Create Dimension Value

     Creates a new value for the specified dimension.

    Args:
        business_id (str):
        dimension_id (int):
        body (ReportingDimensionValueApiModel):
        body (ReportingDimensionValueApiModel):

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
            client=client,
            body=body,
        )
    ).parsed
