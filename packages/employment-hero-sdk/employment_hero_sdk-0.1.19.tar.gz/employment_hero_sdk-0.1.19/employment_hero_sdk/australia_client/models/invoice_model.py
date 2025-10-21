import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invoice_line_item_model import InvoiceLineItemModel


T = TypeVar("T", bound="InvoiceModel")


@_attrs_define
class InvoiceModel:
    """
    Attributes:
        id (Union[Unset, int]):
        invoice_number (Union[Unset, str]):
        date (Union[Unset, datetime.datetime]):
        total_excluding_gst (Union[Unset, float]):
        gst (Union[Unset, float]):
        total_including_gst (Union[Unset, float]):
        culture_name (Union[Unset, str]):
        currency (Union[Unset, str]):
        line_items (Union[Unset, List['InvoiceLineItemModel']]):
    """

    id: Union[Unset, int] = UNSET
    invoice_number: Union[Unset, str] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET
    total_excluding_gst: Union[Unset, float] = UNSET
    gst: Union[Unset, float] = UNSET
    total_including_gst: Union[Unset, float] = UNSET
    culture_name: Union[Unset, str] = UNSET
    currency: Union[Unset, str] = UNSET
    line_items: Union[Unset, List["InvoiceLineItemModel"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        invoice_number = self.invoice_number

        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        total_excluding_gst = self.total_excluding_gst

        gst = self.gst

        total_including_gst = self.total_including_gst

        culture_name = self.culture_name

        currency = self.currency

        line_items: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.line_items, Unset):
            line_items = []
            for line_items_item_data in self.line_items:
                line_items_item = line_items_item_data.to_dict()
                line_items.append(line_items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if invoice_number is not UNSET:
            field_dict["invoiceNumber"] = invoice_number
        if date is not UNSET:
            field_dict["date"] = date
        if total_excluding_gst is not UNSET:
            field_dict["totalExcludingGst"] = total_excluding_gst
        if gst is not UNSET:
            field_dict["gst"] = gst
        if total_including_gst is not UNSET:
            field_dict["totalIncludingGst"] = total_including_gst
        if culture_name is not UNSET:
            field_dict["cultureName"] = culture_name
        if currency is not UNSET:
            field_dict["currency"] = currency
        if line_items is not UNSET:
            field_dict["lineItems"] = line_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.invoice_line_item_model import InvoiceLineItemModel

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        invoice_number = d.pop("invoiceNumber", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        total_excluding_gst = d.pop("totalExcludingGst", UNSET)

        gst = d.pop("gst", UNSET)

        total_including_gst = d.pop("totalIncludingGst", UNSET)

        culture_name = d.pop("cultureName", UNSET)

        currency = d.pop("currency", UNSET)

        line_items = []
        _line_items = d.pop("lineItems", UNSET)
        for line_items_item_data in _line_items or []:
            line_items_item = InvoiceLineItemModel.from_dict(line_items_item_data)

            line_items.append(line_items_item)

        invoice_model = cls(
            id=id,
            invoice_number=invoice_number,
            date=date,
            total_excluding_gst=total_excluding_gst,
            gst=gst,
            total_including_gst=total_including_gst,
            culture_name=culture_name,
            currency=currency,
            line_items=line_items,
        )

        invoice_model.additional_properties = d
        return invoice_model

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
