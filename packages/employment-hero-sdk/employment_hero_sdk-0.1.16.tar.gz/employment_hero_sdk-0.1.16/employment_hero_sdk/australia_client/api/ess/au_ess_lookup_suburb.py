from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.suburb_result import SuburbResult
from ...types import UNSET, Response, Unset


def _get_kwargs(
    employee_id: str,
    *,
    suburb: str,
    state: str,
    post_code: str,
    country_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["suburb"] = suburb

    params["state"] = state

    params["postCode"] = post_code

    params["countryId"] = country_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/ess/{employee_id}/lookup/suburb",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[SuburbResult]:
    if response.status_code == HTTPStatus.OK:
        response_200 = SuburbResult.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[SuburbResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    suburb: str,
    state: str,
    post_code: str,
    country_id: Union[Unset, str] = UNSET,
) -> Response[SuburbResult]:
    """Get Suburb

     Gets the suburb for the criteria passed in

    Args:
        employee_id (str):
        suburb (str):
        state (str):
        post_code (str):
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuburbResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        suburb=suburb,
        state=state,
        post_code=post_code,
        country_id=country_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    suburb: str,
    state: str,
    post_code: str,
    country_id: Union[Unset, str] = UNSET,
) -> Optional[SuburbResult]:
    """Get Suburb

     Gets the suburb for the criteria passed in

    Args:
        employee_id (str):
        suburb (str):
        state (str):
        post_code (str):
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuburbResult
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        suburb=suburb,
        state=state,
        post_code=post_code,
        country_id=country_id,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    suburb: str,
    state: str,
    post_code: str,
    country_id: Union[Unset, str] = UNSET,
) -> Response[SuburbResult]:
    """Get Suburb

     Gets the suburb for the criteria passed in

    Args:
        employee_id (str):
        suburb (str):
        state (str):
        post_code (str):
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuburbResult]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        suburb=suburb,
        state=state,
        post_code=post_code,
        country_id=country_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    suburb: str,
    state: str,
    post_code: str,
    country_id: Union[Unset, str] = UNSET,
) -> Optional[SuburbResult]:
    """Get Suburb

     Gets the suburb for the criteria passed in

    Args:
        employee_id (str):
        suburb (str):
        state (str):
        post_code (str):
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuburbResult
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            suburb=suburb,
            state=state,
            post_code=post_code,
            country_id=country_id,
        )
    ).parsed
