from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.journal_account_model import JournalAccountModel


T = TypeVar("T", bound="JournalAccountBulkCreateModel")


@_attrs_define
class JournalAccountBulkCreateModel:
    """
    Attributes:
        error_messages (Union[Unset, List[str]]):
        created_journal_accounts (Union[Unset, List['JournalAccountModel']]):
    """

    error_messages: Union[Unset, List[str]] = UNSET
    created_journal_accounts: Union[Unset, List["JournalAccountModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        error_messages: Union[Unset, List[str]] = UNSET
        if not isinstance(self.error_messages, Unset):
            error_messages = self.error_messages

        created_journal_accounts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.created_journal_accounts, Unset):
            created_journal_accounts = []
            for created_journal_accounts_item_data in self.created_journal_accounts:
                created_journal_accounts_item = created_journal_accounts_item_data.to_dict()
                created_journal_accounts.append(created_journal_accounts_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if error_messages is not UNSET:
            field_dict["errorMessages"] = error_messages
        if created_journal_accounts is not UNSET:
            field_dict["createdJournalAccounts"] = created_journal_accounts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.journal_account_model import JournalAccountModel

        d = src_dict.copy()
        error_messages = cast(List[str], d.pop("errorMessages", UNSET))

        created_journal_accounts = []
        _created_journal_accounts = d.pop("createdJournalAccounts", UNSET)
        for created_journal_accounts_item_data in _created_journal_accounts or []:
            created_journal_accounts_item = JournalAccountModel.from_dict(created_journal_accounts_item_data)

            created_journal_accounts.append(created_journal_accounts_item)

        journal_account_bulk_create_model = cls(
            error_messages=error_messages,
            created_journal_accounts=created_journal_accounts,
        )

        journal_account_bulk_create_model.additional_properties = d
        return journal_account_bulk_create_model

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
