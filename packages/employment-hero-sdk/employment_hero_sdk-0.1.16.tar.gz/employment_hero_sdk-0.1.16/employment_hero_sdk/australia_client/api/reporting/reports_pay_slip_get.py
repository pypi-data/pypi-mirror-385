from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    model_pay_run_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["model.payRunId"] = model_pay_run_id

    params["model.employeeId"] = model_employee_id

    params["model.locationId"] = model_location_id

    params["model.employingEntityId"] = model_employing_entity_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/payslip",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    model_pay_run_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Get Pay Slips by Finalised Pay Run Id

     Gets the pay slips for a finalised pay run with the specified Id.

    Args:
        business_id (str):
        model_pay_run_id (Union[Unset, int]):
        model_employee_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        model_pay_run_id=model_pay_run_id,
        model_employee_id=model_employee_id,
        model_location_id=model_location_id,
        model_employing_entity_id=model_employing_entity_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    model_pay_run_id: Union[Unset, int] = UNSET,
    model_employee_id: Union[Unset, int] = UNSET,
    model_location_id: Union[Unset, int] = UNSET,
    model_employing_entity_id: Union[Unset, int] = UNSET,
) -> Response[Any]:
    """Get Pay Slips by Finalised Pay Run Id

     Gets the pay slips for a finalised pay run with the specified Id.

    Args:
        business_id (str):
        model_pay_run_id (Union[Unset, int]):
        model_employee_id (Union[Unset, int]):
        model_location_id (Union[Unset, int]):
        model_employing_entity_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        model_pay_run_id=model_pay_run_id,
        model_employee_id=model_employee_id,
        model_location_id=model_location_id,
        model_employing_entity_id=model_employing_entity_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
