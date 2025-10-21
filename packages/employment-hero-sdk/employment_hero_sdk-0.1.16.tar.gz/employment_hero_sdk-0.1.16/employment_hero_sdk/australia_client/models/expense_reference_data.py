from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.expense_category_response_model import ExpenseCategoryResponseModel
    from ..models.expense_tax_code import ExpenseTaxCode
    from ..models.location_model import LocationModel


T = TypeVar("T", bound="ExpenseReferenceData")


@_attrs_define
class ExpenseReferenceData:
    """
    Attributes:
        expense_categories (Union[Unset, List['ExpenseCategoryResponseModel']]):
        tax_codes (Union[Unset, List['ExpenseTaxCode']]):
        locations (Union[Unset, List['LocationModel']]):
        default_location_id (Union[Unset, int]):
    """

    expense_categories: Union[Unset, List["ExpenseCategoryResponseModel"]] = UNSET
    tax_codes: Union[Unset, List["ExpenseTaxCode"]] = UNSET
    locations: Union[Unset, List["LocationModel"]] = UNSET
    default_location_id: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        expense_categories: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.expense_categories, Unset):
            expense_categories = []
            for expense_categories_item_data in self.expense_categories:
                expense_categories_item = expense_categories_item_data.to_dict()
                expense_categories.append(expense_categories_item)

        tax_codes: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.tax_codes, Unset):
            tax_codes = []
            for tax_codes_item_data in self.tax_codes:
                tax_codes_item = tax_codes_item_data.to_dict()
                tax_codes.append(tax_codes_item)

        locations: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.locations, Unset):
            locations = []
            for locations_item_data in self.locations:
                locations_item = locations_item_data.to_dict()
                locations.append(locations_item)

        default_location_id = self.default_location_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if expense_categories is not UNSET:
            field_dict["expenseCategories"] = expense_categories
        if tax_codes is not UNSET:
            field_dict["taxCodes"] = tax_codes
        if locations is not UNSET:
            field_dict["locations"] = locations
        if default_location_id is not UNSET:
            field_dict["defaultLocationId"] = default_location_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.expense_category_response_model import ExpenseCategoryResponseModel
        from ..models.expense_tax_code import ExpenseTaxCode
        from ..models.location_model import LocationModel

        d = src_dict.copy()
        expense_categories = []
        _expense_categories = d.pop("expenseCategories", UNSET)
        for expense_categories_item_data in _expense_categories or []:
            expense_categories_item = ExpenseCategoryResponseModel.from_dict(expense_categories_item_data)

            expense_categories.append(expense_categories_item)

        tax_codes = []
        _tax_codes = d.pop("taxCodes", UNSET)
        for tax_codes_item_data in _tax_codes or []:
            tax_codes_item = ExpenseTaxCode.from_dict(tax_codes_item_data)

            tax_codes.append(tax_codes_item)

        locations = []
        _locations = d.pop("locations", UNSET)
        for locations_item_data in _locations or []:
            locations_item = LocationModel.from_dict(locations_item_data)

            locations.append(locations_item)

        default_location_id = d.pop("defaultLocationId", UNSET)

        expense_reference_data = cls(
            expense_categories=expense_categories,
            tax_codes=tax_codes,
            locations=locations,
            default_location_id=default_location_id,
        )

        expense_reference_data.additional_properties = d
        return expense_reference_data

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
