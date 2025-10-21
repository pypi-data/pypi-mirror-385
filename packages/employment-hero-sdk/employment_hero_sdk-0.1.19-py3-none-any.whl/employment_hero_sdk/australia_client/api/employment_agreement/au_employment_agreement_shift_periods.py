from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_shift_periods_model import GetShiftPeriodsModel
from ...models.shift_period_model import ShiftPeriodModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    id: int,
    *,
    body: Union[
        GetShiftPeriodsModel,
        GetShiftPeriodsModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/employmentagreement/{id}/shiftperiods",
    }

    if isinstance(body, GetShiftPeriodsModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, GetShiftPeriodsModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ShiftPeriodModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ShiftPeriodModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ShiftPeriodModel"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftPeriodsModel,
        GetShiftPeriodsModel,
    ],
) -> Response[List["ShiftPeriodModel"]]:
    """Get Shift Periods

     Gets all the shift periods for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (GetShiftPeriodsModel):
        body (GetShiftPeriodsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ShiftPeriodModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftPeriodsModel,
        GetShiftPeriodsModel,
    ],
) -> Optional[List["ShiftPeriodModel"]]:
    """Get Shift Periods

     Gets all the shift periods for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (GetShiftPeriodsModel):
        body (GetShiftPeriodsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ShiftPeriodModel']
    """

    return sync_detailed(
        business_id=business_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftPeriodsModel,
        GetShiftPeriodsModel,
    ],
) -> Response[List["ShiftPeriodModel"]]:
    """Get Shift Periods

     Gets all the shift periods for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (GetShiftPeriodsModel):
        body (GetShiftPeriodsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ShiftPeriodModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        GetShiftPeriodsModel,
        GetShiftPeriodsModel,
    ],
) -> Optional[List["ShiftPeriodModel"]]:
    """Get Shift Periods

     Gets all the shift periods for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (GetShiftPeriodsModel):
        body (GetShiftPeriodsModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ShiftPeriodModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
