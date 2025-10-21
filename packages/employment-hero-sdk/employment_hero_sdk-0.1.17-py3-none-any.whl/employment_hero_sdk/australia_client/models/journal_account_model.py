from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.journal_account_model_external_account_type import JournalAccountModelExternalAccountType
from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalAccountModel")


@_attrs_define
class JournalAccountModel:
    """
    Attributes:
        id (Union[Unset, int]):
        account_code (Union[Unset, str]):
        account_name (Union[Unset, str]):
        account_type (Union[Unset, JournalAccountModelExternalAccountType]):
        external_reference_id (Union[Unset, str]):
    """

    id: Union[Unset, int] = UNSET
    account_code: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    account_type: Union[Unset, JournalAccountModelExternalAccountType] = UNSET
    external_reference_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        account_code = self.account_code

        account_name = self.account_name

        account_type: Union[Unset, str] = UNSET
        if not isinstance(self.account_type, Unset):
            account_type = self.account_type.value

        external_reference_id = self.external_reference_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if account_code is not UNSET:
            field_dict["accountCode"] = account_code
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if account_type is not UNSET:
            field_dict["accountType"] = account_type
        if external_reference_id is not UNSET:
            field_dict["externalReferenceId"] = external_reference_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id", UNSET)

        account_code = d.pop("accountCode", UNSET)

        account_name = d.pop("accountName", UNSET)

        _account_type = d.pop("accountType", UNSET)
        account_type: Union[Unset, JournalAccountModelExternalAccountType]
        if isinstance(_account_type, Unset):
            account_type = UNSET
        else:
            account_type = JournalAccountModelExternalAccountType(_account_type)

        external_reference_id = d.pop("externalReferenceId", UNSET)

        journal_account_model = cls(
            id=id,
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            external_reference_id=external_reference_id,
        )

        journal_account_model.additional_properties = d
        return journal_account_model

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
