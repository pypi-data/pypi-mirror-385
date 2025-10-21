from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.suburb_model import SuburbModel


T = TypeVar("T", bound="SuburbResult")


@_attrs_define
class SuburbResult:
    """
    Attributes:
        result (Union[Unset, SuburbModel]):
    """

    result: Union[Unset, "SuburbModel"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.result, Unset):
            result = self.result.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.suburb_model import SuburbModel

        d = src_dict.copy()
        _result = d.pop("result", UNSET)
        result: Union[Unset, SuburbModel]
        if isinstance(_result, Unset):
            result = UNSET
        else:
            result = SuburbModel.from_dict(_result)

        suburb_result = cls(
            result=result,
        )

        suburb_result.additional_properties = d
        return suburb_result

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
