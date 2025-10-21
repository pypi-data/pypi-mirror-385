from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunJobModel")


@_attrs_define
class PayRunJobModel:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        job_id (Union[Unset, str]):  Example: 00000000-0000-0000-0000-000000000000.
    """

    pay_run_id: Union[Unset, int] = UNSET
    job_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        job_id = self.job_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if job_id is not UNSET:
            field_dict["jobId"] = job_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        job_id = d.pop("jobId", UNSET)

        pay_run_job_model = cls(
            pay_run_id=pay_run_id,
            job_id=job_id,
        )

        pay_run_job_model.additional_properties = d
        return pay_run_job_model

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
