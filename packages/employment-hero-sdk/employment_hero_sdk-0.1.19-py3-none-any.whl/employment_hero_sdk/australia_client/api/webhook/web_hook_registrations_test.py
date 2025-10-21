from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.web_hook_registrations_test_i_http_action_result import WebHookRegistrationsTestIHttpActionResult
from ...types import UNSET, Response


def _get_kwargs(
    business_id: str,
    id: str,
    *,
    filter_: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["filter"] = filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/webhookregistrations/{id}/test",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[WebHookRegistrationsTestIHttpActionResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = WebHookRegistrationsTestIHttpActionResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[WebHookRegistrationsTestIHttpActionResult]:
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
    filter_: str,
) -> Response[WebHookRegistrationsTestIHttpActionResult]:
    """Test Web Hook

     Tests a web hook given a registration ID and a filter string.

    Args:
        business_id (str):
        id (str):
        filter_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsTestIHttpActionResult]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
        filter_=filter_,
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
    filter_: str,
) -> Optional[WebHookRegistrationsTestIHttpActionResult]:
    """Test Web Hook

     Tests a web hook given a registration ID and a filter string.

    Args:
        business_id (str):
        id (str):
        filter_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsTestIHttpActionResult
    """

    return sync_detailed(
        business_id=business_id,
        id=id,
        client=client,
        filter_=filter_,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_: str,
) -> Response[WebHookRegistrationsTestIHttpActionResult]:
    """Test Web Hook

     Tests a web hook given a registration ID and a filter string.

    Args:
        business_id (str):
        id (str):
        filter_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[WebHookRegistrationsTestIHttpActionResult]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        id=id,
        filter_=filter_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    filter_: str,
) -> Optional[WebHookRegistrationsTestIHttpActionResult]:
    """Test Web Hook

     Tests a web hook given a registration ID and a filter string.

    Args:
        business_id (str):
        id (str):
        filter_ (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        WebHookRegistrationsTestIHttpActionResult
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            id=id,
            client=client,
            filter_=filter_,
        )
    ).parsed
