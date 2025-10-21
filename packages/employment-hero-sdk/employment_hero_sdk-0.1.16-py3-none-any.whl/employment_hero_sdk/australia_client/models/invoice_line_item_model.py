from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invoice_line_item_detail_model import InvoiceLineItemDetailModel


T = TypeVar("T", bound="InvoiceLineItemModel")


@_attrs_define
class InvoiceLineItemModel:
    """
    Attributes:
        abn (Union[Unset, str]):
        business_number (Union[Unset, str]):
        business_id (Union[Unset, int]):
        billing_plan (Union[Unset, str]):
        description (Union[Unset, str]):
        unit_price_including_gst (Union[Unset, float]):
        quantity (Union[Unset, float]):
        total_including_gst (Union[Unset, float]):
        details (Union[Unset, List['InvoiceLineItemDetailModel']]):
        white_label_name (Union[Unset, str]):
        brand_name (Union[Unset, str]):
    """

    abn: Union[Unset, str] = UNSET
    business_number: Union[Unset, str] = UNSET
    business_id: Union[Unset, int] = UNSET
    billing_plan: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    unit_price_including_gst: Union[Unset, float] = UNSET
    quantity: Union[Unset, float] = UNSET
    total_including_gst: Union[Unset, float] = UNSET
    details: Union[Unset, List["InvoiceLineItemDetailModel"]] = UNSET
    white_label_name: Union[Unset, str] = UNSET
    brand_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        abn = self.abn

        business_number = self.business_number

        business_id = self.business_id

        billing_plan = self.billing_plan

        description = self.description

        unit_price_including_gst = self.unit_price_including_gst

        quantity = self.quantity

        total_including_gst = self.total_including_gst

        details: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.details, Unset):
            details = []
            for details_item_data in self.details:
                details_item = details_item_data.to_dict()
                details.append(details_item)

        white_label_name = self.white_label_name

        brand_name = self.brand_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if abn is not UNSET:
            field_dict["abn"] = abn
        if business_number is not UNSET:
            field_dict["businessNumber"] = business_number
        if business_id is not UNSET:
            field_dict["businessId"] = business_id
        if billing_plan is not UNSET:
            field_dict["billingPlan"] = billing_plan
        if description is not UNSET:
            field_dict["description"] = description
        if unit_price_including_gst is not UNSET:
            field_dict["unitPriceIncludingGst"] = unit_price_including_gst
        if quantity is not UNSET:
            field_dict["quantity"] = quantity
        if total_including_gst is not UNSET:
            field_dict["totalIncludingGst"] = total_including_gst
        if details is not UNSET:
            field_dict["details"] = details
        if white_label_name is not UNSET:
            field_dict["whiteLabelName"] = white_label_name
        if brand_name is not UNSET:
            field_dict["brandName"] = brand_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.invoice_line_item_detail_model import InvoiceLineItemDetailModel

        d = src_dict.copy()
        abn = d.pop("abn", UNSET)

        business_number = d.pop("businessNumber", UNSET)

        business_id = d.pop("businessId", UNSET)

        billing_plan = d.pop("billingPlan", UNSET)

        description = d.pop("description", UNSET)

        unit_price_including_gst = d.pop("unitPriceIncludingGst", UNSET)

        quantity = d.pop("quantity", UNSET)

        total_including_gst = d.pop("totalIncludingGst", UNSET)

        details = []
        _details = d.pop("details", UNSET)
        for details_item_data in _details or []:
            details_item = InvoiceLineItemDetailModel.from_dict(details_item_data)

            details.append(details_item)

        white_label_name = d.pop("whiteLabelName", UNSET)

        brand_name = d.pop("brandName", UNSET)

        invoice_line_item_model = cls(
            abn=abn,
            business_number=business_number,
            business_id=business_id,
            billing_plan=billing_plan,
            description=description,
            unit_price_including_gst=unit_price_including_gst,
            quantity=quantity,
            total_including_gst=total_including_gst,
            details=details,
            white_label_name=white_label_name,
            brand_name=brand_name,
        )

        invoice_line_item_model.additional_properties = d
        return invoice_line_item_model

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
