from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.web_hook import WebHook
from ...models.web_hook_registrations_put_i_http_action_result import WebHookRegistrationsPutIHttpActionResult
from ...types import Response


def _get_kwargs(
    business_id: str,
    id: str,
    *,
    body: Union[
        WebHook,
        WebHook,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "put",
        "url": f"/api/v2/business/{business_id}/webhookregistrations/{id}",
    }

    if isinstance(body, WebHook):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, WebHook):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[WebHookRegistrationsPutIHttpActionResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = WebHookRegistrationsPutIHttpActionResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[WebHookRegistrationsPutIHttpActionResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        WebHook,
        WebHook,
    ],
) -> Response[WebHookRegistrationsPutIHttpActionResult]:
    """Update Web Hook Registration

     Updates the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):
        body (WebHook):
        body (WebHook):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsPutIHttpActionResult]
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
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        WebHook,
        WebHook,
    ],
) -> Optional[WebHookRegistrationsPutIHttpActionResult]:
    """Update Web Hook Registration

     Updates the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):
        body (WebHook):
        body (WebHook):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsPutIHttpActionResult
    """

    return sync_detailed(
        business_id=business_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        WebHook,
        WebHook,
    ],
) -> Response[WebHookRegistrationsPutIHttpActionResult]:
    """Update Web Hook Registration

     Updates the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):
        body (WebHook):
        body (WebHook):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsPutIHttpActionResult]
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
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        WebHook,
        WebHook,
    ],
) -> Optional[WebHookRegistrationsPutIHttpActionResult]:
    """Update Web Hook Registration

     Updates the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):
        body (WebHook):
        body (WebHook):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsPutIHttpActionResult
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
