from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.report_leave_liability_preparation_response_long_running_job_status import (
    ReportLeaveLiabilityPreparationResponseLongRunningJobStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportLeaveLiabilityPreparationResponse")


@_attrs_define
class ReportLeaveLiabilityPreparationResponse:
    """
    Attributes:
        job_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
        status (Union[Unset, ReportLeaveLiabilityPreparationResponseLongRunningJobStatus]):
    """

    job_id: Union[Unset, str] = UNSET
    status: Union[Unset, ReportLeaveLiabilityPreparationResponseLongRunningJobStatus] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        job_id = self.job_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_id is not UNSET:
            field_dict["jobId"] = job_id
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        job_id = d.pop("jobId", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ReportLeaveLiabilityPreparationResponseLongRunningJobStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ReportLeaveLiabilityPreparationResponseLongRunningJobStatus(_status)

        report_leave_liability_preparation_response = cls(
            job_id=job_id,
            status=status,
        )

        report_leave_liability_preparation_response.additional_properties = d
        return report_leave_liability_preparation_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
