from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_billing_plan_response_model import AuBillingPlanResponseModel
from ...types import Response


def _get_kwargs(
    business_id: int,
) -> Dict[str, Any]:
    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/subscription/currentbillingplan",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[AuBillingPlanResponseModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = AuBillingPlanResponseModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[AuBillingPlanResponseModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuBillingPlanResponseModel]:
    """Get Business Billing PLan

     Get the current billing plan for the business.

    Args:
        business_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuBillingPlanResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuBillingPlanResponseModel]:
    """Get Business Billing PLan

     Get the current billing plan for the business.

    Args:
        business_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuBillingPlanResponseModel
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[AuBillingPlanResponseModel]:
    """Get Business Billing PLan

     Get the current billing plan for the business.

    Args:
        business_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AuBillingPlanResponseModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[AuBillingPlanResponseModel]:
    """Get Business Billing PLan

     Get the current billing plan for the business.

    Args:
        business_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AuBillingPlanResponseModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
        )
    ).parsed
