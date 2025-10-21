from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.check_kiosk_pin_model import CheckKioskPinModel
from ...models.kiosk_employee_model import KioskEmployeeModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    kiosk_id: str,
    *,
    body: Union[
        CheckKioskPinModel,
        CheckKioskPinModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/kiosk/{kiosk_id}/checkpin",
    }

    if isinstance(body, CheckKioskPinModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, CheckKioskPinModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[KioskEmployeeModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = KioskEmployeeModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[KioskEmployeeModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    kiosk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        CheckKioskPinModel,
        CheckKioskPinModel,
    ],
) -> Response[KioskEmployeeModel]:
    """Verify Kiosk PIN

     Verifies the employee's kiosk PIN. Returns error code 400 if the PIN is incorrect.

    Args:
        business_id (str):
        kiosk_id (str):
        body (CheckKioskPinModel):
        body (CheckKioskPinModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[KioskEmployeeModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    kiosk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        CheckKioskPinModel,
        CheckKioskPinModel,
    ],
) -> Optional[KioskEmployeeModel]:
    """Verify Kiosk PIN

     Verifies the employee's kiosk PIN. Returns error code 400 if the PIN is incorrect.

    Args:
        business_id (str):
        kiosk_id (str):
        body (CheckKioskPinModel):
        body (CheckKioskPinModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        KioskEmployeeModel
    """

    return sync_detailed(
        business_id=business_id,
        kiosk_id=kiosk_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    kiosk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        CheckKioskPinModel,
        CheckKioskPinModel,
    ],
) -> Response[KioskEmployeeModel]:
    """Verify Kiosk PIN

     Verifies the employee's kiosk PIN. Returns error code 400 if the PIN is incorrect.

    Args:
        business_id (str):
        kiosk_id (str):
        body (CheckKioskPinModel):
        body (CheckKioskPinModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[KioskEmployeeModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        kiosk_id=kiosk_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    kiosk_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        CheckKioskPinModel,
        CheckKioskPinModel,
    ],
) -> Optional[KioskEmployeeModel]:
    """Verify Kiosk PIN

     Verifies the employee's kiosk PIN. Returns error code 400 if the PIN is incorrect.

    Args:
        business_id (str):
        kiosk_id (str):
        body (CheckKioskPinModel):
        body (CheckKioskPinModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        KioskEmployeeModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            kiosk_id=kiosk_id,
            client=client,
            body=body,
        )
    ).parsed
