import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_qualification_document_model import EmployeeQualificationDocumentModel


T = TypeVar("T", bound="EmployeeQualificationModel")


@_attrs_define
class EmployeeQualificationModel:
    """
    Attributes:
        qualification_id (Union[Unset, int]):
        name (Union[Unset, str]):
        expiry_date (Union[Unset, datetime.datetime]):
        issue_date (Union[Unset, datetime.datetime]):
        documents (Union[Unset, List['EmployeeQualificationDocumentModel']]):
        reference_number (Union[Unset, str]):
    """

    qualification_id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    expiry_date: Union[Unset, datetime.datetime] = UNSET
    issue_date: Union[Unset, datetime.datetime] = UNSET
    documents: Union[Unset, List["EmployeeQualificationDocumentModel"]] = UNSET
    reference_number: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        qualification_id = self.qualification_id

        name = self.name

        expiry_date: Union[Unset, str] = UNSET
        if not isinstance(self.expiry_date, Unset):
            expiry_date = self.expiry_date.isoformat()

        issue_date: Union[Unset, str] = UNSET
        if not isinstance(self.issue_date, Unset):
            issue_date = self.issue_date.isoformat()

        documents: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.documents, Unset):
            documents = []
            for documents_item_data in self.documents:
                documents_item = documents_item_data.to_dict()
                documents.append(documents_item)

        reference_number = self.reference_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if qualification_id is not UNSET:
            field_dict["qualificationId"] = qualification_id
        if name is not UNSET:
            field_dict["name"] = name
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if issue_date is not UNSET:
            field_dict["issueDate"] = issue_date
        if documents is not UNSET:
            field_dict["documents"] = documents
        if reference_number is not UNSET:
            field_dict["referenceNumber"] = reference_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_qualification_document_model import EmployeeQualificationDocumentModel

        d = src_dict.copy()
        qualification_id = d.pop("qualificationId", UNSET)

        name = d.pop("name", UNSET)

        _expiry_date = d.pop("expiryDate", UNSET)
        expiry_date: Union[Unset, datetime.datetime]
        if isinstance(_expiry_date, Unset):
            expiry_date = UNSET
        else:
            expiry_date = isoparse(_expiry_date)

        _issue_date = d.pop("issueDate", UNSET)
        issue_date: Union[Unset, datetime.datetime]
        if isinstance(_issue_date, Unset):
            issue_date = UNSET
        else:
            issue_date = isoparse(_issue_date)

        documents = []
        _documents = d.pop("documents", UNSET)
        for documents_item_data in _documents or []:
            documents_item = EmployeeQualificationDocumentModel.from_dict(documents_item_data)

            documents.append(documents_item)

        reference_number = d.pop("referenceNumber", UNSET)

        employee_qualification_model = cls(
            qualification_id=qualification_id,
            name=name,
            expiry_date=expiry_date,
            issue_date=issue_date,
            documents=documents,
            reference_number=reference_number,
        )

        employee_qualification_model.additional_properties = d
        return employee_qualification_model

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
