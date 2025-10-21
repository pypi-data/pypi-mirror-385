from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.journal_export_result_external_service import JournalExportResultExternalService
from ..models.journal_export_result_journal_export_status import JournalExportResultJournalExportStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalExportResult")


@_attrs_define
class JournalExportResult:
    """
    Attributes:
        status (Union[Unset, JournalExportResultJournalExportStatus]):
        message (Union[Unset, str]):
        journal_source (Union[Unset, JournalExportResultExternalService]):
        journal_external_reference_id (Union[Unset, str]):
    """

    status: Union[Unset, JournalExportResultJournalExportStatus] = UNSET
    message: Union[Unset, str] = UNSET
    journal_source: Union[Unset, JournalExportResultExternalService] = UNSET
    journal_external_reference_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        message = self.message

        journal_source: Union[Unset, str] = UNSET
        if not isinstance(self.journal_source, Unset):
            journal_source = self.journal_source.value

        journal_external_reference_id = self.journal_external_reference_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if message is not UNSET:
            field_dict["message"] = message
        if journal_source is not UNSET:
            field_dict["journalSource"] = journal_source
        if journal_external_reference_id is not UNSET:
            field_dict["journalExternalReferenceId"] = journal_external_reference_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _status = d.pop("status", UNSET)
        status: Union[Unset, JournalExportResultJournalExportStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = JournalExportResultJournalExportStatus(_status)

        message = d.pop("message", UNSET)

        _journal_source = d.pop("journalSource", UNSET)
        journal_source: Union[Unset, JournalExportResultExternalService]
        if isinstance(_journal_source, Unset):
            journal_source = UNSET
        else:
            journal_source = JournalExportResultExternalService(_journal_source)

        journal_external_reference_id = d.pop("journalExternalReferenceId", UNSET)

        journal_export_result = cls(
            status=status,
            message=message,
            journal_source=journal_source,
            journal_external_reference_id=journal_external_reference_id,
        )

        journal_export_result.additional_properties = d
        return journal_export_result

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
