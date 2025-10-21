from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paged_result_model_suburb_model import PagedResultModelSuburbModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    employee_id: str,
    *,
    term: str,
    page_num: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    country_id: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["term"] = term

    params["pageNum"] = page_num

    params["pageSize"] = page_size

    params["countryId"] = country_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/ess/{employee_id}/lookup/suburbs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[PagedResultModelSuburbModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PagedResultModelSuburbModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[PagedResultModelSuburbModel]:
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
    term: str,
    page_num: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    country_id: Union[Unset, str] = UNSET,
) -> Response[PagedResultModelSuburbModel]:
    """Search Suburbs

     Gets a list of suburbs that match the search term.

    Args:
        employee_id (str):
        term (str):
        page_num (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelSuburbModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        term=term,
        page_num=page_num,
        page_size=page_size,
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
    term: str,
    page_num: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    country_id: Union[Unset, str] = UNSET,
) -> Optional[PagedResultModelSuburbModel]:
    """Search Suburbs

     Gets a list of suburbs that match the search term.

    Args:
        employee_id (str):
        term (str):
        page_num (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelSuburbModel
    """

    return sync_detailed(
        employee_id=employee_id,
        client=client,
        term=term,
        page_num=page_num,
        page_size=page_size,
        country_id=country_id,
    ).parsed


async def asyncio_detailed(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    term: str,
    page_num: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    country_id: Union[Unset, str] = UNSET,
) -> Response[PagedResultModelSuburbModel]:
    """Search Suburbs

     Gets a list of suburbs that match the search term.

    Args:
        employee_id (str):
        term (str):
        page_num (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PagedResultModelSuburbModel]
    """

    kwargs = _get_kwargs(
        employee_id=employee_id,
        term=term,
        page_num=page_num,
        page_size=page_size,
        country_id=country_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    employee_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    term: str,
    page_num: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    country_id: Union[Unset, str] = UNSET,
) -> Optional[PagedResultModelSuburbModel]:
    """Search Suburbs

     Gets a list of suburbs that match the search term.

    Args:
        employee_id (str):
        term (str):
        page_num (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        country_id (Union[Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PagedResultModelSuburbModel
    """

    return (
        await asyncio_detailed(
            employee_id=employee_id,
            client=client,
            term=term,
            page_num=page_num,
            page_size=page_size,
            country_id=country_id,
        )
    ).parsed
