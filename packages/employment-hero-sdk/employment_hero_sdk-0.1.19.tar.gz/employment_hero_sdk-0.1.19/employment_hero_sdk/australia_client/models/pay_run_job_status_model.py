from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PayRunJobStatusModel")


@_attrs_define
class PayRunJobStatusModel:
    """
    Attributes:
        pay_run_id (Union[Unset, int]):
        status (Union[Unset, str]):
        external_id (Union[Unset, str]):
        additional_info (Union[Unset, str]):
    """

    pay_run_id: Union[Unset, int] = UNSET
    status: Union[Unset, str] = UNSET
    external_id: Union[Unset, str] = UNSET
    additional_info: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pay_run_id = self.pay_run_id

        status = self.status

        external_id = self.external_id

        additional_info = self.additional_info

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pay_run_id is not UNSET:
            field_dict["payRunId"] = pay_run_id
        if status is not UNSET:
            field_dict["status"] = status
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if additional_info is not UNSET:
            field_dict["additionalInfo"] = additional_info

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pay_run_id = d.pop("payRunId", UNSET)

        status = d.pop("status", UNSET)

        external_id = d.pop("externalId", UNSET)

        additional_info = d.pop("additionalInfo", UNSET)

        pay_run_job_status_model = cls(
            pay_run_id=pay_run_id,
            status=status,
            external_id=external_id,
            additional_info=additional_info,
        )

        pay_run_job_status_model.additional_properties = d
        return pay_run_job_status_model

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
