from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportingDimensionValueSelectModel")


@_attrs_define
class ReportingDimensionValueSelectModel:
    """
    Attributes:
        reporting_dimension_id (Union[Unset, int]):
        is_deleted (Union[Unset, bool]):
        is_no_longer_allowed (Union[Unset, bool]):
        value (Union[Unset, int]):
        text (Union[Unset, str]):
    """

    reporting_dimension_id: Union[Unset, int] = UNSET
    is_deleted: Union[Unset, bool] = UNSET
    is_no_longer_allowed: Union[Unset, bool] = UNSET
    value: Union[Unset, int] = UNSET
    text: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        reporting_dimension_id = self.reporting_dimension_id

        is_deleted = self.is_deleted

        is_no_longer_allowed = self.is_no_longer_allowed

        value = self.value

        text = self.text

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reporting_dimension_id is not UNSET:
            field_dict["reportingDimensionId"] = reporting_dimension_id
        if is_deleted is not UNSET:
            field_dict["isDeleted"] = is_deleted
        if is_no_longer_allowed is not UNSET:
            field_dict["isNoLongerAllowed"] = is_no_longer_allowed
        if value is not UNSET:
            field_dict["value"] = value
        if text is not UNSET:
            field_dict["text"] = text

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        reporting_dimension_id = d.pop("reportingDimensionId", UNSET)

        is_deleted = d.pop("isDeleted", UNSET)

        is_no_longer_allowed = d.pop("isNoLongerAllowed", UNSET)

        value = d.pop("value", UNSET)

        text = d.pop("text", UNSET)

        reporting_dimension_value_select_model = cls(
            reporting_dimension_id=reporting_dimension_id,
            is_deleted=is_deleted,
            is_no_longer_allowed=is_no_longer_allowed,
            value=value,
            text=text,
        )

        reporting_dimension_value_select_model.additional_properties = d
        return reporting_dimension_value_select_model

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
