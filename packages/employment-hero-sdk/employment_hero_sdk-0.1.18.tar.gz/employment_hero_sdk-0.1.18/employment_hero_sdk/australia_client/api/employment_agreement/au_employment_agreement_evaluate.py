from http import HTTPStatus
from typing import Any, Dict, Optional, Union

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
        ShiftCostingsRequestModel,
        ShiftCostingsRequestModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/employmentagreement/{id}/shiftcosting",
    }

    if isinstance(body, ShiftCostingsRequestModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, ShiftCostingsRequestModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ShiftCostingsResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ShiftCostingsResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ShiftCostingsResponseModel]:
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
        ShiftCostingsRequestModel,
        ShiftCostingsRequestModel,
    ],
) -> Response[ShiftCostingsResponseModel]:
    """Evaluate Shift Costings

     Evaluates shift costings for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (ShiftCostingsRequestModel):
        body (ShiftCostingsRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ShiftCostingsResponseModel]
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
        ShiftCostingsRequestModel,
        ShiftCostingsRequestModel,
    ],
) -> Optional[ShiftCostingsResponseModel]:
    """Evaluate Shift Costings

     Evaluates shift costings for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (ShiftCostingsRequestModel):
        body (ShiftCostingsRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ShiftCostingsResponseModel
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
        ShiftCostingsRequestModel,
        ShiftCostingsRequestModel,
    ],
) -> Response[ShiftCostingsResponseModel]:
    """Evaluate Shift Costings

     Evaluates shift costings for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (ShiftCostingsRequestModel):
        body (ShiftCostingsRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ShiftCostingsResponseModel]
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
        ShiftCostingsRequestModel,
        ShiftCostingsRequestModel,
    ],
) -> Optional[ShiftCostingsResponseModel]:
    """Evaluate Shift Costings

     Evaluates shift costings for the employment agreement with the specified ID.

    Args:
        business_id (str):
        id (int):
        body (ShiftCostingsRequestModel):
        body (ShiftCostingsRequestModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ShiftCostingsResponseModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
