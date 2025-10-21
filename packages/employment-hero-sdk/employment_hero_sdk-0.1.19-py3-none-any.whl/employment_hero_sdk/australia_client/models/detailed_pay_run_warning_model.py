from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.detailed_pay_run_warning_model_pay_run_warning_type import DetailedPayRunWarningModelPayRunWarningType
from ..types import UNSET, Unset

T = TypeVar("T", bound="DetailedPayRunWarningModel")


@_attrs_define
class DetailedPayRunWarningModel:
    """
    Attributes:
        warning_type (Union[Unset, DetailedPayRunWarningModelPayRunWarningType]):
        warning_type_description (Union[Unset, str]):
        employee_id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        warning (Union[Unset, str]):
    """

    warning_type: Union[Unset, DetailedPayRunWarningModelPayRunWarningType] = UNSET
    warning_type_description: Union[Unset, str] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    warning: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        warning_type: Union[Unset, str] = UNSET
        if not isinstance(self.warning_type, Unset):
            warning_type = self.warning_type.value

        warning_type_description = self.warning_type_description

        employee_id = self.employee_id

        employee_name = self.employee_name

        warning = self.warning

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if warning_type is not UNSET:
            field_dict["warningType"] = warning_type
        if warning_type_description is not UNSET:
            field_dict["warningTypeDescription"] = warning_type_description
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _warning_type = d.pop("warningType", UNSET)
        warning_type: Union[Unset, DetailedPayRunWarningModelPayRunWarningType]
        if isinstance(_warning_type, Unset):
            warning_type = UNSET
        else:
            warning_type = DetailedPayRunWarningModelPayRunWarningType(_warning_type)

        warning_type_description = d.pop("warningTypeDescription", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        warning = d.pop("warning", UNSET)

        detailed_pay_run_warning_model = cls(
            warning_type=warning_type,
            warning_type_description=warning_type_description,
            employee_id=employee_id,
            employee_name=employee_name,
            warning=warning,
        )

        detailed_pay_run_warning_model.additional_properties = d
        return detailed_pay_run_warning_model

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
