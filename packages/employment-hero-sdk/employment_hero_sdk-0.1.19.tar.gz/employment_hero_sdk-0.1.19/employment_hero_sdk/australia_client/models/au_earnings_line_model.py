from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.au_earnings_line_model_nullable_lump_sum_calculation_method import (
    AuEarningsLineModelNullableLumpSumCalculationMethod,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.au_earnings_line_model_i_dictionary_string_i_list_1 import AuEarningsLineModelIDictionaryStringIList1


T = TypeVar("T", bound="AuEarningsLineModel")


@_attrs_define
class AuEarningsLineModel:
    """
    Attributes:
        super_ (Union[Unset, float]):
        sfss (Union[Unset, float]):
        help_ (Union[Unset, float]):
        payg (Union[Unset, float]):
        pay_category_id (Union[Unset, str]):
        pay_category_name (Union[Unset, str]):
        units (Union[Unset, float]):
        notes (Union[Unset, str]):
        rate (Union[Unset, float]):
        earnings (Union[Unset, float]):
        lump_sum_number_of_pay_periods (Union[Unset, float]):
        lump_sum_calculation_method (Union[Unset, AuEarningsLineModelNullableLumpSumCalculationMethod]):
        lump_sum_e_financial_year (Union[Unset, int]):
        timesheet_line_id (Union[Unset, int]):
        timesheet_line_external_id (Union[Unset, str]):
        reporting_dimension_value_ids (Union[Unset, List[int]]): Nullable</p><p><i>Note:</i> Only applicable to
            businesses where the Dimensions feature is enabled.</p><p>Specify an array of dimension value ids (normally only
            one-per dimension) eg [1,3,7].</p><p>If you prefer to specify dimension values by name, use the
            ReportingDimensionValueNames field instead.</p><p>If this field is used, ReportingDimensionValueNames will be
            ignored (the Ids take precedence)
        reporting_dimension_value_names (Union[Unset, AuEarningsLineModelIDictionaryStringIList1]):
            Nullable</p><p><i>Note:</i> Only applicable to businesses where the Dimensions feature is enabled.</p><p>Specify
            an object with dimension names and for each one, specify an array of associated value names (normally one-per
            dimension) eg { "Department": ["Accounting"], "Job Code": ["JC1"] }.</p><p>If you prefer to specify dimension
            values directly by Id, use the ReportingDimensionValueIds field instead.</p><p>If ReportingDimensionValueIds is
            used, ReportingDimensionValueNames will be ignored (the Ids take precedence)
        net_payment (Union[Unset, float]):
        id (Union[Unset, int]):
        external_id (Union[Unset, str]):
        location_id (Union[Unset, str]):
        location_name (Union[Unset, str]):
        employee_id (Union[Unset, str]):
        employee_name (Union[Unset, str]):
        employee_external_id (Union[Unset, str]):
    """

    super_: Union[Unset, float] = UNSET
    sfss: Union[Unset, float] = UNSET
    help_: Union[Unset, float] = UNSET
    payg: Union[Unset, float] = UNSET
    pay_category_id: Union[Unset, str] = UNSET
    pay_category_name: Union[Unset, str] = UNSET
    units: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    rate: Union[Unset, float] = UNSET
    earnings: Union[Unset, float] = UNSET
    lump_sum_number_of_pay_periods: Union[Unset, float] = UNSET
    lump_sum_calculation_method: Union[Unset, AuEarningsLineModelNullableLumpSumCalculationMethod] = UNSET
    lump_sum_e_financial_year: Union[Unset, int] = UNSET
    timesheet_line_id: Union[Unset, int] = UNSET
    timesheet_line_external_id: Union[Unset, str] = UNSET
    reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
    reporting_dimension_value_names: Union[Unset, "AuEarningsLineModelIDictionaryStringIList1"] = UNSET
    net_payment: Union[Unset, float] = UNSET
    id: Union[Unset, int] = UNSET
    external_id: Union[Unset, str] = UNSET
    location_id: Union[Unset, str] = UNSET
    location_name: Union[Unset, str] = UNSET
    employee_id: Union[Unset, str] = UNSET
    employee_name: Union[Unset, str] = UNSET
    employee_external_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        super_ = self.super_

        sfss = self.sfss

        help_ = self.help_

        payg = self.payg

        pay_category_id = self.pay_category_id

        pay_category_name = self.pay_category_name

        units = self.units

        notes = self.notes

        rate = self.rate

        earnings = self.earnings

        lump_sum_number_of_pay_periods = self.lump_sum_number_of_pay_periods

        lump_sum_calculation_method: Union[Unset, str] = UNSET
        if not isinstance(self.lump_sum_calculation_method, Unset):
            lump_sum_calculation_method = self.lump_sum_calculation_method.value

        lump_sum_e_financial_year = self.lump_sum_e_financial_year

        timesheet_line_id = self.timesheet_line_id

        timesheet_line_external_id = self.timesheet_line_external_id

        reporting_dimension_value_ids: Union[Unset, List[int]] = UNSET
        if not isinstance(self.reporting_dimension_value_ids, Unset):
            reporting_dimension_value_ids = self.reporting_dimension_value_ids

        reporting_dimension_value_names: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = self.reporting_dimension_value_names.to_dict()

        net_payment = self.net_payment

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
        if super_ is not UNSET:
            field_dict["super"] = super_
        if sfss is not UNSET:
            field_dict["sfss"] = sfss
        if help_ is not UNSET:
            field_dict["help"] = help_
        if payg is not UNSET:
            field_dict["payg"] = payg
        if pay_category_id is not UNSET:
            field_dict["payCategoryId"] = pay_category_id
        if pay_category_name is not UNSET:
            field_dict["payCategoryName"] = pay_category_name
        if units is not UNSET:
            field_dict["units"] = units
        if notes is not UNSET:
            field_dict["notes"] = notes
        if rate is not UNSET:
            field_dict["rate"] = rate
        if earnings is not UNSET:
            field_dict["earnings"] = earnings
        if lump_sum_number_of_pay_periods is not UNSET:
            field_dict["lumpSumNumberOfPayPeriods"] = lump_sum_number_of_pay_periods
        if lump_sum_calculation_method is not UNSET:
            field_dict["lumpSumCalculationMethod"] = lump_sum_calculation_method
        if lump_sum_e_financial_year is not UNSET:
            field_dict["lumpSumEFinancialYear"] = lump_sum_e_financial_year
        if timesheet_line_id is not UNSET:
            field_dict["timesheetLineId"] = timesheet_line_id
        if timesheet_line_external_id is not UNSET:
            field_dict["timesheetLineExternalId"] = timesheet_line_external_id
        if reporting_dimension_value_ids is not UNSET:
            field_dict["reportingDimensionValueIds"] = reporting_dimension_value_ids
        if reporting_dimension_value_names is not UNSET:
            field_dict["reportingDimensionValueNames"] = reporting_dimension_value_names
        if net_payment is not UNSET:
            field_dict["netPayment"] = net_payment
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
        from ..models.au_earnings_line_model_i_dictionary_string_i_list_1 import (
            AuEarningsLineModelIDictionaryStringIList1,
        )

        d = src_dict.copy()
        super_ = d.pop("super", UNSET)

        sfss = d.pop("sfss", UNSET)

        help_ = d.pop("help", UNSET)

        payg = d.pop("payg", UNSET)

        pay_category_id = d.pop("payCategoryId", UNSET)

        pay_category_name = d.pop("payCategoryName", UNSET)

        units = d.pop("units", UNSET)

        notes = d.pop("notes", UNSET)

        rate = d.pop("rate", UNSET)

        earnings = d.pop("earnings", UNSET)

        lump_sum_number_of_pay_periods = d.pop("lumpSumNumberOfPayPeriods", UNSET)

        _lump_sum_calculation_method = d.pop("lumpSumCalculationMethod", UNSET)
        lump_sum_calculation_method: Union[Unset, AuEarningsLineModelNullableLumpSumCalculationMethod]
        if isinstance(_lump_sum_calculation_method, Unset):
            lump_sum_calculation_method = UNSET
        else:
            lump_sum_calculation_method = AuEarningsLineModelNullableLumpSumCalculationMethod(
                _lump_sum_calculation_method
            )

        lump_sum_e_financial_year = d.pop("lumpSumEFinancialYear", UNSET)

        timesheet_line_id = d.pop("timesheetLineId", UNSET)

        timesheet_line_external_id = d.pop("timesheetLineExternalId", UNSET)

        reporting_dimension_value_ids = cast(List[int], d.pop("reportingDimensionValueIds", UNSET))

        _reporting_dimension_value_names = d.pop("reportingDimensionValueNames", UNSET)
        reporting_dimension_value_names: Union[Unset, AuEarningsLineModelIDictionaryStringIList1]
        if isinstance(_reporting_dimension_value_names, Unset):
            reporting_dimension_value_names = UNSET
        else:
            reporting_dimension_value_names = AuEarningsLineModelIDictionaryStringIList1.from_dict(
                _reporting_dimension_value_names
            )

        net_payment = d.pop("netPayment", UNSET)

        id = d.pop("id", UNSET)

        external_id = d.pop("externalId", UNSET)

        location_id = d.pop("locationId", UNSET)

        location_name = d.pop("locationName", UNSET)

        employee_id = d.pop("employeeId", UNSET)

        employee_name = d.pop("employeeName", UNSET)

        employee_external_id = d.pop("employeeExternalId", UNSET)

        au_earnings_line_model = cls(
            super_=super_,
            sfss=sfss,
            help_=help_,
            payg=payg,
            pay_category_id=pay_category_id,
            pay_category_name=pay_category_name,
            units=units,
            notes=notes,
            rate=rate,
            earnings=earnings,
            lump_sum_number_of_pay_periods=lump_sum_number_of_pay_periods,
            lump_sum_calculation_method=lump_sum_calculation_method,
            lump_sum_e_financial_year=lump_sum_e_financial_year,
            timesheet_line_id=timesheet_line_id,
            timesheet_line_external_id=timesheet_line_external_id,
            reporting_dimension_value_ids=reporting_dimension_value_ids,
            reporting_dimension_value_names=reporting_dimension_value_names,
            net_payment=net_payment,
            id=id,
            external_id=external_id,
            location_id=location_id,
            location_name=location_name,
            employee_id=employee_id,
            employee_name=employee_name,
            employee_external_id=employee_external_id,
        )

        au_earnings_line_model.additional_properties = d
        return au_earnings_line_model

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
