from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.submit_leave_accruals_model_id_type import SubmitLeaveAccrualsModelIdType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.submit_leave_accruals_model_dictionary_string_list_1 import (
        SubmitLeaveAccrualsModelDictionaryStringList1,
    )


T = TypeVar("T", bound="SubmitLeaveAccrualsModel")


@_attrs_define
class SubmitLeaveAccrualsModel:
    """
    Attributes:
        replace_existing (Union[Unset, bool]):
        employee_id_type (Union[Unset, SubmitLeaveAccrualsModelIdType]):
        suppress_calculations (Union[Unset, bool]):
        leave (Union[Unset, SubmitLeaveAccrualsModelDictionaryStringList1]):
    """

    replace_existing: Union[Unset, bool] = UNSET
    employee_id_type: Union[Unset, SubmitLeaveAccrualsModelIdType] = UNSET
    suppress_calculations: Union[Unset, bool] = UNSET
    leave: Union[Unset, "SubmitLeaveAccrualsModelDictionaryStringList1"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        replace_existing = self.replace_existing

        employee_id_type: Union[Unset, str] = UNSET
        if not isinstance(self.employee_id_type, Unset):
            employee_id_type = self.employee_id_type.value

        suppress_calculations = self.suppress_calculations

        leave: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.leave, Unset):
            leave = self.leave.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if replace_existing is not UNSET:
            field_dict["replaceExisting"] = replace_existing
        if employee_id_type is not UNSET:
            field_dict["employeeIdType"] = employee_id_type
        if suppress_calculations is not UNSET:
            field_dict["suppressCalculations"] = suppress_calculations
        if leave is not UNSET:
            field_dict["leave"] = leave

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.submit_leave_accruals_model_dictionary_string_list_1 import (
            SubmitLeaveAccrualsModelDictionaryStringList1,
        )

        d = src_dict.copy()
        replace_existing = d.pop("replaceExisting", UNSET)

        _employee_id_type = d.pop("employeeIdType", UNSET)
        employee_id_type: Union[Unset, SubmitLeaveAccrualsModelIdType]
        if isinstance(_employee_id_type, Unset):
            employee_id_type = UNSET
        else:
            employee_id_type = SubmitLeaveAccrualsModelIdType(_employee_id_type)

        suppress_calculations = d.pop("suppressCalculations", UNSET)

        _leave = d.pop("leave", UNSET)
        leave: Union[Unset, SubmitLeaveAccrualsModelDictionaryStringList1]
        if isinstance(_leave, Unset):
            leave = UNSET
        else:
            leave = SubmitLeaveAccrualsModelDictionaryStringList1.from_dict(_leave)

        submit_leave_accruals_model = cls(
            replace_existing=replace_existing,
            employee_id_type=employee_id_type,
            suppress_calculations=suppress_calculations,
            leave=leave,
        )

        submit_leave_accruals_model.additional_properties = d
        return submit_leave_accruals_model

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
