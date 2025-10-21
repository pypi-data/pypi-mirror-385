import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Attachment")


@_attrs_define
class Attachment:
    """
    Attributes:
        data (Union[Unset, str]):
        is_deleted (Union[Unset, bool]):
        id (Union[Unset, int]):
        friendly_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        url (Union[Unset, str]):
        date_scanned (Union[Unset, datetime.datetime]):
        is_infected (Union[Unset, bool]):
    """

    data: Union[Unset, str] = UNSET
    is_deleted: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    friendly_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    url: Union[Unset, str] = UNSET
    date_scanned: Union[Unset, datetime.datetime] = UNSET
    is_infected: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data

        is_deleted = self.is_deleted

        id = self.id

        friendly_name = self.friendly_name

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        url = self.url

        date_scanned: Union[Unset, str] = UNSET
        if not isinstance(self.date_scanned, Unset):
            date_scanned = self.date_scanned.isoformat()

        is_infected = self.is_infected

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if is_deleted is not UNSET:
            field_dict["isDeleted"] = is_deleted
        if id is not UNSET:
            field_dict["id"] = id
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if url is not UNSET:
            field_dict["url"] = url
        if date_scanned is not UNSET:
            field_dict["dateScanned"] = date_scanned
        if is_infected is not UNSET:
            field_dict["isInfected"] = is_infected

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data = d.pop("data", UNSET)

        is_deleted = d.pop("isDeleted", UNSET)

        id = d.pop("id", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        url = d.pop("url", UNSET)

        _date_scanned = d.pop("dateScanned", UNSET)
        date_scanned: Union[Unset, datetime.datetime]
        if isinstance(_date_scanned, Unset):
            date_scanned = UNSET
        else:
            date_scanned = isoparse(_date_scanned)

        is_infected = d.pop("isInfected", UNSET)

        attachment = cls(
            data=data,
            is_deleted=is_deleted,
            id=id,
            friendly_name=friendly_name,
            date_created=date_created,
            url=url,
            date_scanned=date_scanned,
            is_infected=is_infected,
        )

        attachment.additional_properties = d
        return attachment

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
