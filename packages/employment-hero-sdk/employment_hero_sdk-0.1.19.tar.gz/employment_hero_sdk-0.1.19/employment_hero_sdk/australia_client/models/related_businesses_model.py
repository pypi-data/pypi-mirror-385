from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.abbreviated_business_model import AbbreviatedBusinessModel


T = TypeVar("T", bound="RelatedBusinessesModel")


@_attrs_define
class RelatedBusinessesModel:
    """
    Attributes:
        related_businesses (Union[Unset, List['AbbreviatedBusinessModel']]):
        user_id (Union[Unset, int]):
    """

    related_businesses: Union[Unset, List["AbbreviatedBusinessModel"]] = UNSET
    user_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        related_businesses: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.related_businesses, Unset):
            related_businesses = []
            for related_businesses_item_data in self.related_businesses:
                related_businesses_item = related_businesses_item_data.to_dict()
                related_businesses.append(related_businesses_item)

        user_id = self.user_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if related_businesses is not UNSET:
            field_dict["relatedBusinesses"] = related_businesses
        if user_id is not UNSET:
            field_dict["userId"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.abbreviated_business_model import AbbreviatedBusinessModel

        d = src_dict.copy()
        related_businesses = []
        _related_businesses = d.pop("relatedBusinesses", UNSET)
        for related_businesses_item_data in _related_businesses or []:
            related_businesses_item = AbbreviatedBusinessModel.from_dict(related_businesses_item_data)

            related_businesses.append(related_businesses_item)

        user_id = d.pop("userId", UNSET)

        related_businesses_model = cls(
            related_businesses=related_businesses,
            user_id=user_id,
        )

        related_businesses_model.additional_properties = d
        return related_businesses_model

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
