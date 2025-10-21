from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_user_model import UpdateUserModel
from ...models.user_updated_model import UserUpdatedModel
from ...types import Response


def _get_kwargs(
    *,
    body: Union[
        UpdateUserModel,
        UpdateUserModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": "/api/v2/user",
    }

    if isinstance(body, UpdateUserModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, UpdateUserModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[UserUpdatedModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = UserUpdatedModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[UserUpdatedModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        UpdateUserModel,
        UpdateUserModel,
    ],
) -> Response[UserUpdatedModel]:
    r"""Update User

     This is currently restricted to updating the user's \"email confirmation\" status only.
    The API user (brand manager or reseller) must have brand exclusive access to the user
    i.e. the user must only have access to businesses/employees that the API user manages.

    Args:
        body (UpdateUserModel):
        body (UpdateUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserUpdatedModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        UpdateUserModel,
        UpdateUserModel,
    ],
) -> Optional[UserUpdatedModel]:
    r"""Update User

     This is currently restricted to updating the user's \"email confirmation\" status only.
    The API user (brand manager or reseller) must have brand exclusive access to the user
    i.e. the user must only have access to businesses/employees that the API user manages.

    Args:
        body (UpdateUserModel):
        body (UpdateUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserUpdatedModel
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        UpdateUserModel,
        UpdateUserModel,
    ],
) -> Response[UserUpdatedModel]:
    r"""Update User

     This is currently restricted to updating the user's \"email confirmation\" status only.
    The API user (brand manager or reseller) must have brand exclusive access to the user
    i.e. the user must only have access to businesses/employees that the API user manages.

    Args:
        body (UpdateUserModel):
        body (UpdateUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UserUpdatedModel]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        UpdateUserModel,
        UpdateUserModel,
    ],
) -> Optional[UserUpdatedModel]:
    r"""Update User

     This is currently restricted to updating the user's \"email confirmation\" status only.
    The API user (brand manager or reseller) must have brand exclusive access to the user
    i.e. the user must only have access to businesses/employees that the API user manages.

    Args:
        body (UpdateUserModel):
        body (UpdateUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UserUpdatedModel
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
