from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attachment_model import AttachmentModel
    from ..models.expense_request_edit_line_item_model import ExpenseRequestEditLineItemModel


T = TypeVar("T", bound="ExpenseRequestEditModel")


@_attrs_define
class ExpenseRequestEditModel:
    """
    Attributes:
        employee_id (int): Required
        attachments (Union[Unset, List['AttachmentModel']]):
        id (Union[Unset, int]):
        description (Union[Unset, str]):
        line_items (Union[Unset, List['ExpenseRequestEditLineItemModel']]):
    """

    employee_id: int
    attachments: Union[Unset, List["AttachmentModel"]] = UNSET
    id: Union[Unset, int] = UNSET
    description: Union[Unset, str] = UNSET
    line_items: Union[Unset, List["ExpenseRequestEditLineItemModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_id = self.employee_id

        attachments: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.attachments, Unset):
            attachments = []
            for attachments_item_data in self.attachments:
                attachments_item = attachments_item_data.to_dict()
                attachments.append(attachments_item)

        id = self.id

        description = self.description

        line_items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.line_items, Unset):
            line_items = []
            for line_items_item_data in self.line_items:
                line_items_item = line_items_item_data.to_dict()
                line_items.append(line_items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "employeeId": employee_id,
            }
        )
        if attachments is not UNSET:
            field_dict["attachments"] = attachments
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if line_items is not UNSET:
            field_dict["lineItems"] = line_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attachment_model import AttachmentModel
        from ..models.expense_request_edit_line_item_model import ExpenseRequestEditLineItemModel

        d = src_dict.copy()
        employee_id = d.pop("employeeId")

        attachments = []
        _attachments = d.pop("attachments", UNSET)
        for attachments_item_data in _attachments or []:
            attachments_item = AttachmentModel.from_dict(attachments_item_data)

            attachments.append(attachments_item)

        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        line_items = []
        _line_items = d.pop("lineItems", UNSET)
        for line_items_item_data in _line_items or []:
            line_items_item = ExpenseRequestEditLineItemModel.from_dict(line_items_item_data)

            line_items.append(line_items_item)

        expense_request_edit_model = cls(
            employee_id=employee_id,
            attachments=attachments,
            id=id,
            description=description,
            line_items=line_items,
        )

        expense_request_edit_model.additional_properties = d
        return expense_request_edit_model

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
