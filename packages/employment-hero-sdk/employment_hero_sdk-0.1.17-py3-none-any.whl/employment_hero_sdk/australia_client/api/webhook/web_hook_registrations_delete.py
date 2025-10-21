from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.web_hook_registrations_delete_i_http_action_result import WebHookRegistrationsDeleteIHttpActionResult
from ...types import Response


def _get_kwargs(
    business_id: str,
    id: str,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v2/business/{business_id}/webhookregistrations/{id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[WebHookRegistrationsDeleteIHttpActionResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = WebHookRegistrationsDeleteIHttpActionResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[WebHookRegistrationsDeleteIHttpActionResult]:
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
) -> Response[WebHookRegistrationsDeleteIHttpActionResult]:
    """Delete Web Hook Registration

     Deletes the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsDeleteIHttpActionResult]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
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
) -> Optional[WebHookRegistrationsDeleteIHttpActionResult]:
    """Delete Web Hook Registration

     Deletes the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsDeleteIHttpActionResult
    """

    return sync_detailed(
        business_id=business_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[WebHookRegistrationsDeleteIHttpActionResult]:
    """Delete Web Hook Registration

     Deletes the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsDeleteIHttpActionResult]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[WebHookRegistrationsDeleteIHttpActionResult]:
    """Delete Web Hook Registration

     Deletes the web hook registration with the specified ID.

    Args:
        business_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsDeleteIHttpActionResult
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
        )
    ).parsed
