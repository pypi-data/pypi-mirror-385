from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.new_user_created_model import NewUserCreatedModel
from ...models.new_user_model import NewUserModel
from ...types import Response


def _get_kwargs(
    *,
    body: Union[
        NewUserModel,
        NewUserModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/user",
    }

    if isinstance(body, NewUserModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, NewUserModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[NewUserCreatedModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = NewUserCreatedModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[NewUserCreatedModel]:
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
        NewUserModel,
        NewUserModel,
    ],
) -> Response[NewUserCreatedModel]:
    """Create New User

     Creates a new user and sends an email to inform the user.

    In order to make sure that the correct brand details are included in the email, be sure to `POST`
    the API request to `https://{yourbrand}.yourpayroll.com.au`.<br />
    To prevent sending of the new user email, set `apiOnly` to `true` in the request.

    Args:
        body (NewUserModel):
        body (NewUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NewUserCreatedModel]
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
        NewUserModel,
        NewUserModel,
    ],
) -> Optional[NewUserCreatedModel]:
    """Create New User

     Creates a new user and sends an email to inform the user.

    In order to make sure that the correct brand details are included in the email, be sure to `POST`
    the API request to `https://{yourbrand}.yourpayroll.com.au`.<br />
    To prevent sending of the new user email, set `apiOnly` to `true` in the request.

    Args:
        body (NewUserModel):
        body (NewUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NewUserCreatedModel
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        NewUserModel,
        NewUserModel,
    ],
) -> Response[NewUserCreatedModel]:
    """Create New User

     Creates a new user and sends an email to inform the user.

    In order to make sure that the correct brand details are included in the email, be sure to `POST`
    the API request to `https://{yourbrand}.yourpayroll.com.au`.<br />
    To prevent sending of the new user email, set `apiOnly` to `true` in the request.

    Args:
        body (NewUserModel):
        body (NewUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[NewUserCreatedModel]
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
        NewUserModel,
        NewUserModel,
    ],
) -> Optional[NewUserCreatedModel]:
    """Create New User

     Creates a new user and sends an email to inform the user.

    In order to make sure that the correct brand details are included in the email, be sure to `POST`
    the API request to `https://{yourbrand}.yourpayroll.com.au`.<br />
    To prevent sending of the new user email, set `apiOnly` to `true` in the request.

    Args:
        body (NewUserModel):
        body (NewUserModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        NewUserCreatedModel
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
