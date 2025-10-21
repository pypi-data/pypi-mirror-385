from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.manager_timesheet_line_model import ManagerTimesheetLineModel
from ...models.manager_timesheet_submit_model import ManagerTimesheetSubmitModel
from ...types import Response


def _get_kwargs(
    business_id: str,
    employee_id: int,
    timesheet_id: int,
    *,
    body: Union[
        ManagerTimesheetSubmitModel,
        ManagerTimesheetSubmitModel,
    ],
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": f"/api/v2/business/{business_id}/manager/{employee_id}/timesheet/{timesheet_id}",
    }

    if isinstance(body, ManagerTimesheetSubmitModel):
        _json_body = body.to_dict()

        _kwargs["json"] = _json_body
        headers["Content-Type"] = "application/json"
    if isinstance(body, ManagerTimesheetSubmitModel):
        _data_body = body.to_dict()

        _kwargs["data"] = _data_body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[ManagerTimesheetLineModel]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ManagerTimesheetLineModel.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[ManagerTimesheetLineModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    business_id: str,
    employee_id: int,
    timesheet_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ManagerTimesheetSubmitModel,
        ManagerTimesheetSubmitModel,
    ],
) -> Response[ManagerTimesheetLineModel]:
    r"""Edit Timesheet

     Edits the timesheet with the specified ID.
    classificationId field left unspecified or null will not be changed.
    To update classificationId field provide the new value, to specifically clear a value use \"0\".

    Args:
        business_id (str):
        employee_id (int):
        timesheet_id (int):
        body (ManagerTimesheetSubmitModel):
        body (ManagerTimesheetSubmitModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagerTimesheetLineModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        timesheet_id=timesheet_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    employee_id: int,
    timesheet_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ManagerTimesheetSubmitModel,
        ManagerTimesheetSubmitModel,
    ],
) -> Optional[ManagerTimesheetLineModel]:
    r"""Edit Timesheet

     Edits the timesheet with the specified ID.
    classificationId field left unspecified or null will not be changed.
    To update classificationId field provide the new value, to specifically clear a value use \"0\".

    Args:
        business_id (str):
        employee_id (int):
        timesheet_id (int):
        body (ManagerTimesheetSubmitModel):
        body (ManagerTimesheetSubmitModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagerTimesheetLineModel
    """

    return sync_detailed(
        business_id=business_id,
        employee_id=employee_id,
        timesheet_id=timesheet_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    employee_id: int,
    timesheet_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ManagerTimesheetSubmitModel,
        ManagerTimesheetSubmitModel,
    ],
) -> Response[ManagerTimesheetLineModel]:
    r"""Edit Timesheet

     Edits the timesheet with the specified ID.
    classificationId field left unspecified or null will not be changed.
    To update classificationId field provide the new value, to specifically clear a value use \"0\".

    Args:
        business_id (str):
        employee_id (int):
        timesheet_id (int):
        body (ManagerTimesheetSubmitModel):
        body (ManagerTimesheetSubmitModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ManagerTimesheetLineModel]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        employee_id=employee_id,
        timesheet_id=timesheet_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    employee_id: int,
    timesheet_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: Union[
        ManagerTimesheetSubmitModel,
        ManagerTimesheetSubmitModel,
    ],
) -> Optional[ManagerTimesheetLineModel]:
    r"""Edit Timesheet

     Edits the timesheet with the specified ID.
    classificationId field left unspecified or null will not be changed.
    To update classificationId field provide the new value, to specifically clear a value use \"0\".

    Args:
        business_id (str):
        employee_id (int):
        timesheet_id (int):
        body (ManagerTimesheetSubmitModel):
        body (ManagerTimesheetSubmitModel):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ManagerTimesheetLineModel
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            employee_id=employee_id,
            timesheet_id=timesheet_id,
            client=client,
            body=body,
        )
    ).parsed
