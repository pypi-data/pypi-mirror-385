from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.pay_run_warning_dto_pay_run_warning_type import PayRunWarningDtoPayRunWarningType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pay_run_warning_dto_object import PayRunWarningDtoObject


T = TypeVar("T", bound="PayRunWarningDto")


@_attrs_define
class PayRunWarningDto:
    """
    Attributes:
        warning_type (Union[Unset, PayRunWarningDtoPayRunWarningType]):
        employee_id (Union[Unset, int]):
        warning (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        pay_run_total_id (Union[Unset, int]):
        meta_data (Union[Unset, PayRunWarningDtoObject]):
        meta_data_json (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
        disable_auto_progression (Union[Unset, bool]):
        formatted_warning_message (Union[Unset, str]):
    """

    warning_type: Union[Unset, PayRunWarningDtoPayRunWarningType] = UNSET
    employee_id: Union[Unset, int] = UNSET
    warning: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    pay_run_total_id: Union[Unset, int] = UNSET
    meta_data: Union[Unset, "PayRunWarningDtoObject"] = UNSET
    meta_data_json: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    disable_auto_progression: Union[Unset, bool] = UNSET
    formatted_warning_message: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        warning_type: Union[Unset, str] = UNSET
        if not isinstance(self.warning_type, Unset):
            warning_type = self.warning_type.value

        employee_id = self.employee_id

        warning = self.warning

        employee_name = self.employee_name

        pay_run_total_id = self.pay_run_total_id

        meta_data: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.meta_data, Unset):
            meta_data = self.meta_data.to_dict()

        meta_data_json = self.meta_data_json

        employee_external_id = self.employee_external_id

        disable_auto_progression = self.disable_auto_progression

        formatted_warning_message = self.formatted_warning_message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if warning_type is not UNSET:
            field_dict["warningType"] = warning_type
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if warning is not UNSET:
            field_dict["warning"] = warning
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if pay_run_total_id is not UNSET:
            field_dict["payRunTotalId"] = pay_run_total_id
        if meta_data is not UNSET:
            field_dict["metaData"] = meta_data
        if meta_data_json is not UNSET:
            field_dict["metaDataJson"] = meta_data_json
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id
        if disable_auto_progression is not UNSET:
            field_dict["disableAutoProgression"] = disable_auto_progression
        if formatted_warning_message is not UNSET:
            field_dict["formattedWarningMessage"] = formatted_warning_message

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.pay_run_warning_dto_object import PayRunWarningDtoObject

        d = src_dict.copy()
        _warning_type = d.pop("warningType", UNSET)
        warning_type: Union[Unset, PayRunWarningDtoPayRunWarningType]
        if isinstance(_warning_type, Unset):
            warning_type = UNSET
        else:
            warning_type = PayRunWarningDtoPayRunWarningType(_warning_type)

        employee_id = d.pop("employeeId", UNSET)

        warning = d.pop("warning", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        pay_run_total_id = d.pop("payRunTotalId", UNSET)

        _meta_data = d.pop("metaData", UNSET)
        meta_data: Union[Unset, PayRunWarningDtoObject]
        if isinstance(_meta_data, Unset):
            meta_data = UNSET
        else:
            meta_data = PayRunWarningDtoObject.from_dict(_meta_data)

        meta_data_json = d.pop("metaDataJson", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        disable_auto_progression = d.pop("disableAutoProgression", UNSET)

        formatted_warning_message = d.pop("formattedWarningMessage", UNSET)

        pay_run_warning_dto = cls(
            warning_type=warning_type,
            employee_id=employee_id,
            warning=warning,
            employee_name=employee_name,
            pay_run_total_id=pay_run_total_id,
            meta_data=meta_data,
            meta_data_json=meta_data_json,
            employee_external_id=employee_external_id,
            disable_auto_progression=disable_auto_progression,
            formatted_warning_message=formatted_warning_message,
        )

        pay_run_warning_dto.additional_properties = d
        return pay_run_warning_dto

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
