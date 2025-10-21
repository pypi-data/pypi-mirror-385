from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.au_edit_business_pay_slip_api_model import AuEditBusinessPaySlipApiModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    *,
    body: Union[
        AuEditBusinessPaySlipApiModel,
        AuEditBusinessPaySlipApiModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/payslip",
    }

    if isinstance(body, AuEditBusinessPaySlipApiModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, AuEditBusinessPaySlipApiModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
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
    body: Union[
        AuEditBusinessPaySlipApiModel,
        AuEditBusinessPaySlipApiModel,
    ],
) -> Response[Any]:
    """Create payslip configuration

     Creates the payslip configuration for the specified business ID.

    ShowLineNotes field must be enabled in order to enable the ShowLocationInLineNotes field.

    An example of what you would populate the EmailBodyMessage field with would be:
    <p>Hi {{FirstName}},</p><p>{{BusinessName}} has just processed your pay and a new pay slip is
    available.</p><p>Regards {{BusinessName}}</p>

    Args:
        business_id (str):
        body (AuEditBusinessPaySlipApiModel):
        body (AuEditBusinessPaySlipApiModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        AuEditBusinessPaySlipApiModel,
        AuEditBusinessPaySlipApiModel,
    ],
) -> Response[Any]:
    """Create payslip configuration

     Creates the payslip configuration for the specified business ID.

    ShowLineNotes field must be enabled in order to enable the ShowLocationInLineNotes field.

    An example of what you would populate the EmailBodyMessage field with would be:
    <p>Hi {{FirstName}},</p><p>{{BusinessName}} has just processed your pay and a new pay slip is
    available.</p><p>Regards {{BusinessName}}</p>

    Args:
        business_id (str):
        body (AuEditBusinessPaySlipApiModel):
        body (AuEditBusinessPaySlipApiModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
