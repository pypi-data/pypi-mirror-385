import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="EssDocumentModel")


@_attrs_define
class EssDocumentModel:
    """
    Attributes:
        id (Union[Unset, str]):
        friendly_name (Union[Unset, str]):
        date_created (Union[Unset, datetime.datetime]):
        requires_employee_acknowledgement (Union[Unset, bool]):
        date_acknowledged (Union[Unset, datetime.datetime]):
    """

    id: Union[Unset, str] = UNSET
    friendly_name: Union[Unset, str] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    requires_employee_acknowledgement: Union[Unset, bool] = UNSET
    date_acknowledged: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        friendly_name = self.friendly_name

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        requires_employee_acknowledgement = self.requires_employee_acknowledgement

        date_acknowledged: Union[Unset, str] = UNSET
        if not isinstance(self.date_acknowledged, Unset):
            date_acknowledged = self.date_acknowledged.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if friendly_name is not UNSET:
            field_dict["friendlyName"] = friendly_name
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created
        if requires_employee_acknowledgement is not UNSET:
            field_dict["requiresEmployeeAcknowledgement"] = requires_employee_acknowledgement
        if date_acknowledged is not UNSET:
            field_dict["dateAcknowledged"] = date_acknowledged

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        friendly_name = d.pop("friendlyName", UNSET)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        requires_employee_acknowledgement = d.pop("requiresEmployeeAcknowledgement", UNSET)

        _date_acknowledged = d.pop("dateAcknowledged", UNSET)
        date_acknowledged: Union[Unset, datetime.datetime]
        if isinstance(_date_acknowledged, Unset):
            date_acknowledged = UNSET
        else:
            date_acknowledged = isoparse(_date_acknowledged)

        ess_document_model = cls(
            id=id,
            friendly_name=friendly_name,
            date_created=date_created,
            requires_employee_acknowledgement=requires_employee_acknowledgement,
            date_acknowledged=date_acknowledged,
        )

        ess_document_model.additional_properties = d
        return ess_document_model

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
