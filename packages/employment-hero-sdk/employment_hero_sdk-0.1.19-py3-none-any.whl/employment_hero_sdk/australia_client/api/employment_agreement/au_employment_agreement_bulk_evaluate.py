from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.shift_costings_request_model import ShiftCostingsRequestModel
from ...models.shift_costings_response_model import ShiftCostingsResponseModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    id: int,
    *,
    body: Union[
        List["ShiftCostingsRequestModel"],
        List["ShiftCostingsRequestModel"],
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/employmentagreement/{id}/shiftcosting/bulk",
    }

    if isinstance(body, List["ShiftCostingsRequestModel"]):
        _json_body = []
        for body_item_data in body:
            body_item = body_item_data.to_dict()
            _json_body.append(body_item)

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, List["ShiftCostingsRequestModel"]):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["ShiftCostingsResponseModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ShiftCostingsResponseModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["ShiftCostingsResponseModel"]]:
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
        List["ShiftCostingsRequestModel"],
        List["ShiftCostingsRequestModel"],
    ],
) -> Response[List["ShiftCostingsResponseModel"]]:
    """Bulk Evaluate Shift Costings

     Bulk Evaluates shift costings for the employment agreement with the specified ID.
    Limited to 100 entries per request

    Args:
        business_id (str):
        id (int):
        body (List['ShiftCostingsRequestModel']):
        body (List['ShiftCostingsRequestModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ShiftCostingsResponseModel']]
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
        List["ShiftCostingsRequestModel"],
        List["ShiftCostingsRequestModel"],
    ],
) -> Optional[List["ShiftCostingsResponseModel"]]:
    """Bulk Evaluate Shift Costings

     Bulk Evaluates shift costings for the employment agreement with the specified ID.
    Limited to 100 entries per request

    Args:
        business_id (str):
        id (int):
        body (List['ShiftCostingsRequestModel']):
        body (List['ShiftCostingsRequestModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ShiftCostingsResponseModel']
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
        List["ShiftCostingsRequestModel"],
        List["ShiftCostingsRequestModel"],
    ],
) -> Response[List["ShiftCostingsResponseModel"]]:
    """Bulk Evaluate Shift Costings

     Bulk Evaluates shift costings for the employment agreement with the specified ID.
    Limited to 100 entries per request

    Args:
        business_id (str):
        id (int):
        body (List['ShiftCostingsRequestModel']):
        body (List['ShiftCostingsRequestModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['ShiftCostingsResponseModel']]
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
        List["ShiftCostingsRequestModel"],
        List["ShiftCostingsRequestModel"],
    ],
) -> Optional[List["ShiftCostingsResponseModel"]]:
    """Bulk Evaluate Shift Costings

     Bulk Evaluates shift costings for the employment agreement with the specified ID.
    Limited to 100 entries per request

    Args:
        business_id (str):
        id (int):
        body (List['ShiftCostingsRequestModel']):
        body (List['ShiftCostingsRequestModel']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['ShiftCostingsResponseModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
