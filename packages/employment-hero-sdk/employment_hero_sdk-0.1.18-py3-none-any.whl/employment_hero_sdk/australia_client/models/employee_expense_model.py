from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.employee_expense_model_i_dictionary_string_i_list_1 import EmployeeExpenseModelIDictionaryStringIList1


T = TypeVar("T", bound="EmployeeExpenseModel")


@_attrs_define
class EmployeeExpenseModel:
    """
    Attributes:
        employee_expense_category_id (Union[Unset, str]):
        employee_expense_category_name (Union[Unset, str]):
        notes (Union[Unset, str]):
        amount (Union[Unset, float]):
        tax_code (Union[Unset, str]):
        tax_rate (Union[Unset, float]):
        tax_code_display_name (Union[Unset, str]):
        reporting_dimension_value_ids (Union[Unset, List[int]]): Nullable</p><p><i>Note:</i> Only applicable to
            businesses where the Dimensions feature is enabled.</p><p>Specify an array of dimension value ids (normally only
            one-per dimension) eg [1,3,7].</p><p>If you prefer to specify dimension values by name, use the
            ReportingDimensionValueNames field instead.</p><p>If this field is used, ReportingDimensionValueNames will be
            ignored (the Ids take precedence)
        reporting_dimension_value_names (Union[Unset, EmployeeExpenseModelIDictionaryStringIList1]):
            Nullable</p><p><i>Note:</i> Only applicable to businesses where the Dimensions feature is enabled.</p><p>Specify
            an object with dimension names and for each one, specify an array of associated value names (normally one-per
            dimension) eg { "Department": ["Accounting"], "Job Code": ["JC1"] }.</p><p>If you prefer to specify dimension
            values directly by Id, use the ReportingDimensionValueIds field instead.</p><p>If ReportingDimensionValueIds is
            used, ReportingDimensionValueNames will be ignored (the Ids take precedence)
        id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        location_id (Union[Unset, str]):
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
    """

    employee_expense_category_id: Union[Unset, str] = UNSET
    employee_expense_category_name: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    amount: Union[Unset, float] = UNSET
    tax_code: Union[Unset, str] = UNSET
    tax_rate: Union[Unset, float] = UNSET
    tax_code_display_name: Union[Unset, str] = UNSET
    reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
    reporting_dimension_value_names: Union[Unset, "EmployeeExpenseModelIDictionaryStringIList1"] = UNSET
    id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    location_id: Union[Unset, str] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        employee_expense_category_id = self.employee_expense_category_id

        employee_expense_category_name = self.employee_expense_category_name

        notes = self.notes

        amount = self.amount

        tax_code = self.tax_code

        tax_rate = self.tax_rate

        tax_code_display_name = self.tax_code_display_name

        reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.reporting_dimension_value_ids, Unset):
            reporting_dimension_value_ids = self.reporting_dimension_value_ids

        reporting_dimension_value_names: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = self.reporting_dimension_value_names.to_dict()

        id = self.id

        external_id = self.external_id

        location_id = self.location_id

        location_name = self.location_name

        employee_id = self.employee_id

        employee_name = self.employee_name

        employee_external_id = self.employee_external_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if employee_expense_category_id is not UNSET:
            field_dict["employeeExpenseCategoryId"] = employee_expense_category_id
        if employee_expense_category_name is not UNSET:
            field_dict["employeeExpenseCategoryName"] = employee_expense_category_name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if amount is not UNSET:
            field_dict["amount"] = amount
        if tax_code is not UNSET:
            field_dict["taxCode"] = tax_code
        if tax_rate is not UNSET:
            field_dict["taxRate"] = tax_rate
        if tax_code_display_name is not UNSET:
            field_dict["taxCodeDisplayName"] = tax_code_display_name
        if reporting_dimension_value_ids is not UNSET:
            field_dict["reportingDimensionValueIds"] = reporting_dimension_value_ids
        if reporting_dimension_value_names is not UNSET:
            field_dict["reportingDimensionValueNames"] = reporting_dimension_value_names
        if id is not UNSET:
            field_dict["id"] = id
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if location_id is not UNSET:
            field_dict["locationId"] = location_id
        if location_name is not UNSET:
            field_dict["locationName"] = location_name
        if employee_id is not UNSET:
            field_dict["employeeId"] = employee_id
        if employee_name is not UNSET:
            field_dict["employeeName"] = employee_name
        if employee_external_id is not UNSET:
            field_dict["employeeExternalId"] = employee_external_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.employee_expense_model_i_dictionary_string_i_list_1 import (
            EmployeeExpenseModelIDictionaryStringIList1,
        )

        d = src_dict.copy()
        employee_expense_category_id = d.pop("employeeExpenseCategoryId", UNSET)

        employee_expense_category_name = d.pop("employeeExpenseCategoryName", UNSET)

        notes = d.pop("notes", UNSET)

        amount = d.pop("amount", UNSET)

        tax_code = d.pop("taxCode", UNSET)

        tax_rate = d.pop("taxRate", UNSET)

        tax_code_display_name = d.pop("taxCodeDisplayName", UNSET)

        reporting_dimension_value_ids = cast(List[int], d.pop("reportingDimensionValueIds", UNSET))

        _reporting_dimension_value_names = d.pop("reportingDimensionValueNames", UNSET)
        reporting_dimension_value_names: Union[Unset, EmployeeExpenseModelIDictionaryStringIList1]
        if isinstance(_reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = UNSET
        else:
            reporting_dimension_value_names = EmployeeExpenseModelIDictionaryStringIList1.from_dict(
                _reporting_dimension_value_names
            )

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        employee_expense_model = cls(
            employee_expense_category_id=employee_expense_category_id,
            employee_expense_category_name=employee_expense_category_name,
            notes=notes,
            amount=amount,
            tax_code=tax_code,
            tax_rate=tax_rate,
            tax_code_display_name=tax_code_display_name,
            reporting_dimension_value_ids=reporting_dimension_value_ids,
            reporting_dimension_value_names=reporting_dimension_value_names,
            id=id,
            external_id=external_id,
            location_id=location_id,
            location_name=location_name,
            employee_id=employee_id,
            employee_name=employee_name,
            employee_external_id=employee_external_id,
        )

        employee_expense_model.additional_properties = d
        return employee_expense_model

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
