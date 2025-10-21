from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_employee_filter_model_au_filter_type_enum import AuEmployeeFilterModelAuFilterTypeEnum
from ..models.au_employee_filter_model_filter_operator_enum import AuEmployeeFilterModelFilterOperatorEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuEmployeeFilterModel")


@_attrs_define
class AuEmployeeFilterModel:
    """
    Attributes:
        filter_type (Union[Unset, AuEmployeeFilterModelAuFilterTypeEnum]):
        operator (Union[Unset, AuEmployeeFilterModelFilterOperatorEnum]):
        value (Union[Unset, str]):
    """

    filter_type: Union[Unset, AuEmployeeFilterModelAuFilterTypeEnum] = UNSET
    operator: Union[Unset, AuEmployeeFilterModelFilterOperatorEnum] = UNSET
    value: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        filter_type: Union[Unset, str] = UNSET
        if not isinstance(self.filter_type, Unset):
            filter_type = self.filter_type.value

        operator: Union[Unset, str] = UNSET
        if not isinstance(self.operator, Unset):
            operator = self.operator.value

        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filter_type is not UNSET:
            field_dict["filterType"] = filter_type
        if operator is not UNSET:
            field_dict["operator"] = operator
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _filter_type = d.pop("filterType", UNSET)
        filter_type: Union[Unset, AuEmployeeFilterModelAuFilterTypeEnum]
        if isinstance(_filter_type, Unset):
            filter_type = UNSET
        else:
            filter_type = AuEmployeeFilterModelAuFilterTypeEnum(_filter_type)

        _operator = d.pop("operator", UNSET)
        operator: Union[Unset, AuEmployeeFilterModelFilterOperatorEnum]
        if isinstance(_operator, Unset):
            operator = UNSET
        else:
            operator = AuEmployeeFilterModelFilterOperatorEnum(_operator)

        value = d.pop("value", UNSET)

        au_employee_filter_model = cls(
            filter_type=filter_type,
            operator=operator,
            value=value,
        )

        au_employee_filter_model.additional_properties = d
        return au_employee_filter_model

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
