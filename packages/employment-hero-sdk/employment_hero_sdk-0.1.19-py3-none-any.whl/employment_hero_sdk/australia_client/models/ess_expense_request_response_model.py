import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_model import AttachmentModel
    from ..models.expense_request_line_item_model import ExpenseRequestLineItemModel


T = TypeVar("T", bound="EssExpenseRequestResponseModel")


@_attrs_define
class EssExpenseRequestResponseModel:
    """
    Attributes:
        can_cancel (Union[Unset, bool]):
        can_modify (Union[Unset, bool]):
        id (Union[Unset, int]):
        employee_id (Union[Unset, int]):
        employee_name (Union[Unset, str]):
        status (Union[Unset, str]):
        description (Union[Unset, str]):
        line_items (Union[Unset, List['ExpenseRequestLineItemModel']]):
        attachments (Union[Unset, List['AttachmentModel']]):
        status_updated_by_user (Union[Unset, str]):
        status_update_notes (Union[Unset, str]):
        date_status_updated (Union[Unset, datetime.datetime]):
        date_created (Union[Unset, datetime.datetime]):
    """

    can_cancel: Union[Unset, bool] = UNSET
    can_modify: Union[Unset, bool] = UNSET
    id: Union[Unset, int] = UNSET
    employee_id: Union[Unset, int] = UNSET
    employee_name: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    line_items: Union[Unset, List["ExpenseRequestLineItemModel"]] = UNSET
    attachments: Union[Unset, List["AttachmentModel"]] = UNSET
    status_updated_by_user: Union[Unset, str] = UNSET
    status_update_notes: Union[Unset, str] = UNSET
    date_status_updated: Union[Unset, datetime.datetime] = UNSET
    date_created: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        can_cancel = self.can_cancel

        can_modify = self.can_modify

        id = self.id

        employee_id = self.employee_id

        employee_name = self.employee_name

        status = self.status

        description = self.description

        line_items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.line_items, Unset):
            line_items = []
            for line_items_item_data in self.line_items:
                line_items_item = line_items_item_data.to_dict()
                line_items.append(line_items_item)

        attachments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        status_updated_by_user = self.status_updated_by_user

        status_update_notes = self.status_update_notes

        date_status_updated: Union[Unset, str] = UNSET
        if not isinstance(self.date_status_updated, Unset):
            date_status_updated = self.date_status_updated.isoformat()

        date_created: Union[Unset, str] = UNSET
        if not isinstance(self.date_created, Unset):
            date_created = self.date_created.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if can_cancel is not UNSET:
            field_dict["canCancel"] = can_cancel
        if can_modify is not UNSET:
            field_dict["canModify"] = can_modify
        if id is not UNSET:
            field_dict["id"] = id
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if status is not UNSET:
            field_dict["status"] = status
        if description is not UNSET:
            field_dict["description"] = description
        if line_items is not UNSET:
            field_dict["lineItems"] = line_items
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if status_updated_by_user is not UNSET:
            field_dict["statusUpdatedByUser"] = status_updated_by_user
        if status_update_notes is not UNSET:
            field_dict["statusUpdateNotes"] = status_update_notes
        if date_status_updated is not UNSET:
            field_dict["dateStatusUpdated"] = date_status_updated
        if date_created is not UNSET:
            field_dict["dateCreated"] = date_created

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment_model import AttachmentModel
        from ..models.expense_request_line_item_model import ExpenseRequestLineItemModel

        d = src_dict.copy()
        can_cancel = d.pop("canCancel", UNSET)

        can_modify = d.pop("canModify", UNSET)

        id = d.pop("id", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        status = d.pop("status", UNSET)

        description = d.pop("description", UNSET)

        line_items = []
        _line_items = d.pop("lineItems", UNSET)
        for line_items_item_data in _line_items or []:
            line_items_item = ExpenseRequestLineItemModel.from_dict(line_items_item_data)

            line_items.append(line_items_item)

        attachments = []
        _attachments = d.pop("attachments", UNSET)
        for attachments_item_data in _attachments or []:
            attachments_item = AttachmentModel.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        status_updated_by_user = d.pop("statusUpdatedByUser", UNSET)

        status_update_notes = d.pop("statusUpdateNotes", UNSET)

        _date_status_updated = d.pop("dateStatusUpdated", UNSET)
        date_status_updated: Union[Unset, datetime.datetime]
        if isinstance(_date_status_updated, Unset):
            date_status_updated = UNSET
        else:
            date_status_updated = isoparse(_date_status_updated)

        _date_created = d.pop("dateCreated", UNSET)
        date_created: Union[Unset, datetime.datetime]
        if isinstance(_date_created, Unset):
            date_created = UNSET
        else:
            date_created = isoparse(_date_created)

        ess_expense_request_response_model = cls(
            can_cancel=can_cancel,
            can_modify=can_modify,
            id=id,
            employee_id=employee_id,
            employee_name=employee_name,
            status=status,
            description=description,
            line_items=line_items,
            attachments=attachments,
            status_updated_by_user=status_updated_by_user,
            status_update_notes=status_update_notes,
            date_status_updated=date_status_updated,
            date_created=date_created,
        )

        ess_expense_request_response_model.additional_properties = d
        return ess_expense_request_response_model

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
