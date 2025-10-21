from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.document_acknowledgements_report_export_model import DocumentAcknowledgementsReportExportModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    business_id: str,
    *,
    document_id: Union[Unset, int] = UNSET,
    employee_ids: Union[Unset, List[int]] = UNSET,
    document_status: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = 0,
    location_id: Union[Unset, int] = 0,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["documentId"] = document_id

    json_employee_ids: Union[Unset, List[int]] = UNSET
    if not isinstance(employee_ids, Unset):
        json_employee_ids = employee_ids

    params["employeeIds"] = json_employee_ids

    params["documentStatus"] = document_status

    params["employingEntityId"] = employing_entity_id

    params["locationId"] = location_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": f"/api/v2/business/{business_id}/report/documentAcknowledgements",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[List["DocumentAcknowledgementsReportExportModel"]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DocumentAcknowledgementsReportExportModel.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[List["DocumentAcknowledgementsReportExportModel"]]:
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
    document_id: Union[Unset, int] = UNSET,
    employee_ids: Union[Unset, List[int]] = UNSET,
    document_status: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = 0,
    location_id: Union[Unset, int] = 0,
) -> Response[List["DocumentAcknowledgementsReportExportModel"]]:
    """Document Acknowledgements Report

     Generates a document acknowledgements report.

    Args:
        business_id (str):
        document_id (Union[Unset, int]):
        employee_ids (Union[Unset, List[int]]):
        document_status (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):  Default: 0.
        location_id (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['DocumentAcknowledgementsReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        document_id=document_id,
        employee_ids=employee_ids,
        document_status=document_status,
        employing_entity_id=employing_entity_id,
        location_id=location_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_id: Union[Unset, int] = UNSET,
    employee_ids: Union[Unset, List[int]] = UNSET,
    document_status: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = 0,
    location_id: Union[Unset, int] = 0,
) -> Optional[List["DocumentAcknowledgementsReportExportModel"]]:
    """Document Acknowledgements Report

     Generates a document acknowledgements report.

    Args:
        business_id (str):
        document_id (Union[Unset, int]):
        employee_ids (Union[Unset, List[int]]):
        document_status (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):  Default: 0.
        location_id (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['DocumentAcknowledgementsReportExportModel']
    """

    return sync_detailed(
        business_id=business_id,
        client=client,
        document_id=document_id,
        employee_ids=employee_ids,
        document_status=document_status,
        employing_entity_id=employing_entity_id,
        location_id=location_id,
    ).parsed


async def asyncio_detailed(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_id: Union[Unset, int] = UNSET,
    employee_ids: Union[Unset, List[int]] = UNSET,
    document_status: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = 0,
    location_id: Union[Unset, int] = 0,
) -> Response[List["DocumentAcknowledgementsReportExportModel"]]:
    """Document Acknowledgements Report

     Generates a document acknowledgements report.

    Args:
        business_id (str):
        document_id (Union[Unset, int]):
        employee_ids (Union[Unset, List[int]]):
        document_status (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):  Default: 0.
        location_id (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[List['DocumentAcknowledgementsReportExportModel']]
    """

    kwargs = _get_kwargs(
        business_id=business_id,
        document_id=document_id,
        employee_ids=employee_ids,
        document_status=document_status,
        employing_entity_id=employing_entity_id,
        location_id=location_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    business_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    document_id: Union[Unset, int] = UNSET,
    employee_ids: Union[Unset, List[int]] = UNSET,
    document_status: Union[Unset, int] = 0,
    employing_entity_id: Union[Unset, int] = 0,
    location_id: Union[Unset, int] = 0,
) -> Optional[List["DocumentAcknowledgementsReportExportModel"]]:
    """Document Acknowledgements Report

     Generates a document acknowledgements report.

    Args:
        business_id (str):
        document_id (Union[Unset, int]):
        employee_ids (Union[Unset, List[int]]):
        document_status (Union[Unset, int]):  Default: 0.
        employing_entity_id (Union[Unset, int]):  Default: 0.
        location_id (Union[Unset, int]):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        List['DocumentAcknowledgementsReportExportModel']
    """

    return (
        await asyncio_detailed(
            business_id=business_id,
            client=client,
            document_id=document_id,
            employee_ids=employee_ids,
            document_status=document_status,
            employing_entity_id=employing_entity_id,
            location_id=location_id,
        )
    ).parsed
