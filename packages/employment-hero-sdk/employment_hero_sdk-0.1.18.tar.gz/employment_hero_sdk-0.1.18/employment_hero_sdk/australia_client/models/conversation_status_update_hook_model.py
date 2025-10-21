from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConversationStatusUpdateHookModel")


@_attrs_define
class ConversationStatusUpdateHookModel:
    """
    Attributes:
        business_id (Union[Unset, int]):
        case_id (Union[Unset, str]):
        status (Union[Unset, str]):
        subject (Union[Unset, str]):
        is_automatic (Union[Unset, bool]):
    """

    business_id: Union[Unset, int] = UNSET
    case_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    subject: Union[Unset, str] = UNSET
    is_automatic: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        business_id = self.business_id

        case_id = self.case_id

        status = self.status

        subject = self.subject

        is_automatic = self.is_automatic

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if case_id is not UNSET:
            field_dict["caseId"] = case_id
        if status is not UNSET:
            field_dict["status"] = status
        if subject is not UNSET:
            field_dict["subject"] = subject
        if is_automatic is not UNSET:
            field_dict["isAutomatic"] = is_automatic

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        business_id = d.pop("businessId", UNSET)

        case_id = d.pop("caseId", UNSET)

        status = d.pop("status", UNSET)

        subject = d.pop("subject", UNSET)

        is_automatic = d.pop("isAutomatic", UNSET)

        conversation_status_update_hook_model = cls(
            business_id=business_id,
            case_id=case_id,
            status=status,
            subject=subject,
            is_automatic=is_automatic,
        )

        conversation_status_update_hook_model.additional_properties = d
        return conversation_status_update_hook_model

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
