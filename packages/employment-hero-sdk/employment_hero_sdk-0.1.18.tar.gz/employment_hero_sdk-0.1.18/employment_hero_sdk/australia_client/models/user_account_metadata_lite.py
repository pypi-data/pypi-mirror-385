from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.metadata_lite import MetadataLite


T = TypeVar("T", bound="UserAccountMetadataLite")


@_attrs_define
class UserAccountMetadataLite:
    """
    Attributes:
        user_id (Union[Unset, int]):
        username (Union[Unset, str]):
        relations (Union[Unset, List['MetadataLite']]):
    """

    user_id: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    relations: Union[Unset, List["MetadataLite"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        user_id = self.user_id

        username = self.username

        relations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.relations, Unset):
            relations = []
            for relations_item_data in self.relations:
                relations_item = relations_item_data.to_dict()
                relations.append(relations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["userId"] = user_id
        if username is not UNSET:
            field_dict["username"] = username
        if relations is not UNSET:
            field_dict["relations"] = relations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metadata_lite import MetadataLite

        d = src_dict.copy()
        user_id = d.pop("userId", UNSET)

        username = d.pop("username", UNSET)

        relations = []
        _relations = d.pop("relations", UNSET)
        for relations_item_data in _relations or []:
            relations_item = MetadataLite.from_dict(relations_item_data)

            relations.append(relations_item)

        user_account_metadata_lite = cls(
            user_id=user_id,
            username=username,
            relations=relations,
        )

        user_account_metadata_lite.additional_properties = d
        return user_account_metadata_lite

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
